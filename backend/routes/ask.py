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
    Ask a natural language question about your timeline.
    
    This endpoint:
    1. Searches your events using keywords from the question
    2. Sends relevant events to local LLM for contextual understanding
    3. Returns a conversational answer with source references
    
    Examples:
    - "What meetings did I have about funding last week?"
    - "Summarize my bank calls from October"
    - "What were the action items from the council meeting?"
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
        
        # Extract keywords from question for FTS5 search
        # Simple approach: remove common question words and special chars
        import re
        question_lower = request.question.lower()
        # Remove special FTS5 characters that cause syntax errors
        question_clean = re.sub(r'[^\w\s]', '', question_lower)
        
        stop_words = {'what', 'when', 'where', 'who', 'why', 'how', 'did', 'i', 'have', 
                     'about', 'the', 'a', 'an', 'is', 'are', 'was', 'were', 'my', 'me',
                     'from', 'to', 'in', 'on', 'at', 'for', 'with'}
        
        keywords = [word for word in question_clean.split() 
                   if word not in stop_words and len(word) > 2]
        
        # Build search query (OR search for natural questions)
        if keywords:
            search_query = " OR ".join(keywords[:5])  # Use top 5 keywords
        else:
            # If no keywords, fallback to a generic search
            search_query = "meeting OR call OR event"
        
        logger.info(f"Search query from question: {search_query}")
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
        
        # Search for relevant events
        search_results = search_events(search_query, limit=10)
        
        # Get full event details - FILTER BY TIMELINE
        if search_results:
            event_ids = [r["event_id"] for r in search_results]
            query = session.query(Event).filter(Event.id.in_(event_ids))
            
            # Add timeline filter if specified
            if request.timeline:
                query = query.filter(Event.timeline == request.timeline)
                logger.info(f"Filtering events to timeline: {request.timeline}")
            
            events = query.all()
            
            # Convert to dicts for Ollama
            events_data = []
            for event in events:
                events_data.append({
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'date': event.date.isoformat(),
                    'timeline': event.timeline,
                    'tags': event.tags,
                    'audio_file': event.audio_file
                })
        else:
            events_data = []
        
        # Ask Ollama
        result = ollama.ask(
            question=request.question,
            context_events=events_data,
            conversation_history=request.conversation_history
        )
        
        return AskResponse(
            answer=result["answer"],
            sources=result["sources"],
            model=result.get("model", "unknown"),
            context_used=result.get("context_used", 0),
            search_results_count=len(search_results),
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
