"""
Search API endpoints using FTS5 full-text search
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
import json

from backend.db.base import get_session
from backend.db.fts import search_events, rebuild_index
from backend.models import Event

router = APIRouter()

@router.get("/search")
def search(
    q: str = Query(..., description="Search query (supports AND, OR, NOT, phrase searches)"),
    limit: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """
    Full-text search across events.
    
    Query syntax examples:
    - "town council" - phrase search (exact match)
    - ordinance AND 2020 - both terms must appear
    - meeting OR hearing - either term
    - daniel NOT subdivision - exclude subdivision
    - ordinance* - prefix search (matches ordinance, ordinances, etc.)
    """
    try:
        # Search using FTS5
        results = search_events(q, limit)
        
        # Get full event details for matching events
        event_ids = [r["event_id"] for r in results]
        if not event_ids:
            return []
        
        # Fetch events from database
        statement = select(Event).where(Event.id.in_(event_ids))
        events = session.exec(statement).all()
        
        # Map events by ID for easy lookup
        events_map = {event.id: event for event in events}
        
        # Combine FTS results with full event data
        enriched_results = []
        for result in results:
            event = events_map.get(result["event_id"])
            if event:
                # Parse word timestamps if available
                words = []
                if event.transcription_words:
                    try:
                        words = json.loads(event.transcription_words)
                    except:
                        pass
                
                enriched_results.append({
                    "event": event,
                    "title_snippet": result["title_snippet"],
                    "description_snippet": result["description_snippet"],
                    "rank": result["rank"],
                    "has_audio": bool(event.audio_file),
                    "word_timestamps": words
                })
        
        return enriched_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.post("/search/rebuild-index")
def rebuild_search_index():
    """
    Rebuild the full-text search index from scratch.
    Use this if the search index gets out of sync with the database.
    """
    try:
        count = rebuild_index()
        return {
            "success": True,
            "message": f"Search index rebuilt successfully",
            "events_indexed": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rebuild index: {str(e)}")

@router.get("/search/suggestions")
def search_suggestions(
    q: str = Query(..., description="Partial search term"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get search suggestions based on partial input.
    Returns common terms from the index.
    """
    # This is a simplified version - you could enhance it to return
    # frequently searched terms, common phrases, etc.
    try:
        results = search_events(f"{q}*", limit)
        
        # Extract unique terms from results
        suggestions = []
        seen = set()
        for result in results:
            title = result["title"]
            if title and title not in seen:
                suggestions.append(title)
                seen.add(title)
        
        return {"suggestions": suggestions[:limit]}
    except:
        return {"suggestions": []}
