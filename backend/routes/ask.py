"""
Ask Your Timeline - Conversational AI Endpoint

Natural language interface to query timeline events using local LLM.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from pydantic import BaseModel
from typing import List, Optional
import logging

from backend.db.base import get_session
from backend.db.fts import search_events
from backend.models import Event
from backend.services.ollama_service import get_ollama_service

logger = logging.getLogger(__name__)

router = APIRouter()


class AskRequest(BaseModel):
    """Request for conversational query."""
    question: str
    timeline: Optional[str] = None  # Which timeline to search in
    conversation_history: Optional[List[dict]] = None


class AskResponse(BaseModel):
    """Response from conversational query."""
    answer: str
    sources: List[dict]
    model: str
    context_used: int
    search_results_count: int
    error: bool = False


@router.post("/ask", response_model=AskResponse)
async def ask_timeline(
    request: AskRequest,
    session: Session = Depends(get_session)
):
    """
    SMART AI AGENT: Ask a natural language question about your timeline.
    
    Flow:
    1. Ollama extracts search keywords from question (2-3 sec)
    2. FTS5 searches events with those keywords (instant)
    3. Ollama generates answer from focused snippets (3-5 sec)
    
    Total: 5-10 seconds instead of 60+!
    
    Examples:
    - "What meetings did I have about funding last week?"
    - "What did Judge Smith say about rezoning?"
    - "Were there any test transcriptions?"
    """
    try:
        # Get Ollama service
        ollama = get_ollama_service()
        
        # Check if Ollama is available
        if not ollama.is_available():
            raise HTTPException(
                status_code=503,
                detail="AI service (Ollama) is not available. Please ensure Ollama is running."
            )
        
        logger.info(f"Question: {request.question}")
        logger.info(f"Timeline filter: {request.timeline}")
        
        # If no timeline specified, ask user to specify one
        if not request.timeline:
            # Get available timelines
            from sqlmodel import select
            timelines_query = select(Event.timeline).distinct()
            available_timelines = [t for (t,) in session.exec(timelines_query).all()]
            
            if len(available_timelines) > 1:
                timeline_list = ", ".join(available_timelines)
                return AskResponse(
                    answer=f"I need to know which timeline to search. You have these timelines: {timeline_list}. Please select a timeline first, then ask your question.",
                    sources=[],
                    model=ollama.model,
                    context_used=0,
                    search_results_count=0,
                    error=False
                )
        
        # Create FTS5 search function with timeline filter
        def fts_search_with_timeline(keywords: str):
            """Search FTS5 and filter by timeline"""
            # Search using FTS5
            search_results = search_events(keywords, limit=10)
            
            # Get full event details and filter by timeline
            if search_results:
                event_ids = [r["event_id"] for r in search_results]
                query = session.query(Event).filter(Event.id.in_(event_ids))
                
                # Add timeline filter if specified
                if request.timeline:
                    query = query.filter(Event.timeline == request.timeline)
                
                events = query.all()
                
                # Enrich search results with full event data
                events_map = {str(e.id): e for e in events}
                enriched = []
                for result in search_results:
                    event_id = result["event_id"]
                    if event_id in events_map:
                        event = events_map[event_id]
                        enriched.append({
                            'event': {
                                'id': str(event.id),
                                'title': event.title,
                                'description': event.description,
                                'date': event.date.isoformat(),
                                'timeline': event.timeline,
                                'tags': event.tags,
                                'audio_file': event.audio_file
                            },
                            'title_snippet': result.get('title_snippet', ''),
                            'description_snippet': result.get('description_snippet', ''),
                            'rank': result.get('rank', 0)
                        })
                
                return enriched
            
            return []
        
        # SMART AGENT: Pass FTS5 search function to Ollama
        # Ollama will extract keywords, call FTS5, then generate answer
        result = ollama.ask(
            question=request.question,
            fts_search_func=fts_search_with_timeline,
            conversation_history=request.conversation_history
        )
        
        return AskResponse(
            answer=result["answer"],
            sources=result["sources"],
            model=result.get("model", "unknown"),
            context_used=result.get("context_used", 0),
            search_results_count=result.get("context_used", 0),
            error=result.get("error", False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")


@router.get("/ask/status")
async def check_ai_status():
    """
    Check if the AI service (Ollama) is available.
    """
    ollama = get_ollama_service()
    is_available = ollama.is_available()
    
    return {
        "available": is_available,
        "service": "Ollama",
        "url": ollama.base_url,
        "model": ollama.model,
        "message": "AI service is ready" if is_available else "AI service is not available. Please start Ollama."
    }


@router.get("/ask/metrics")
async def get_performance_metrics():
    """
    Get performance metrics for AI requests.
    """
    from backend.services.performance import get_monitor
    
    monitor = get_monitor()
    return {
        "metrics": monitor.get_all_stats(),
        "note": "Statistics from last 100 requests per category"
    }


@router.post("/ask/warmup")
async def warmup_ollama():
    """
    Warm up the Ollama model with a quick request.
    This loads the model into memory so subsequent requests are faster.
    """
    ollama = get_ollama_service()
    
    if not ollama.is_available():
        return {
            "success": False,
            "message": "Ollama is not available"
        }
    
    try:
        import time
        start = time.time()
        
        # Quick test prompt to load model
        result = ollama.ask(
            question="Hello",
            context_events=[],
            conversation_history=None
        )
        
        elapsed = time.time() - start
        
        return {
            "success": True,
            "message": f"Model warmed up in {elapsed:.2f}s",
            "model": ollama.model,
            "response_time": round(elapsed, 2)
        }
    except Exception as e:
        logger.error(f"Error warming up model: {e}")
        return {
            "success": False,
            "message": f"Failed to warm up: {str(e)}"
        }
