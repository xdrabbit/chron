from datetime import datetime
import csv
import io
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from backend.db.base import get_session
from backend.models import Event
from backend.services.pdf_utils import build_timeline_pdf

router = APIRouter()

# Base path handled directly in routes for clarity

def _normalize_date(raw_value):
    if isinstance(raw_value, datetime):
        return raw_value
    if isinstance(raw_value, str):
        cleaned = raw_value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(cleaned)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid date format") from exc
    raise HTTPException(status_code=400, detail="Invalid date value")


@router.post("/events/", response_model=Event)
def create_event(event: Event, session: Session = Depends(get_session)):
    event.date = _normalize_date(event.date)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@router.get("/timelines/")
def get_timelines(session: Session = Depends(get_session)):
    """Get all unique timeline names"""
    statement = select(Event.timeline).distinct()
    timelines = session.exec(statement).all()
    return sorted(timelines)


@router.get("/events/", response_model=list[Event])
def get_events(timeline: Optional[str] = Query(None), session: Session = Depends(get_session)):
    statement = select(Event).order_by(Event.date)
    if timeline:
        statement = statement.where(Event.timeline == timeline)
    events = session.exec(statement).all()
    return events


@router.get("/events/export/csv")
def export_events_csv(session: Session = Depends(get_session)):
    """Export all events to CSV format"""
    statement = select(Event).order_by(Event.date)
    events = session.exec(statement).all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['title', 'description', 'date', 'timeline', 'emotion', 'tags'])
    
    # Write events
    for event in events:
        writer.writerow([
            event.title,
            event.description,
            event.date.strftime('%Y-%m-%d %H:%M:%S'),
            event.timeline,
            event.emotion or '',
            event.tags or ''
        ])
    
    # Create response
    csv_content = output.getvalue()
    output.close()
    
    headers = {
        "Content-Disposition": 'attachment; filename="chronicle-events.csv"'
    }
    
    return StreamingResponse(
        io.StringIO(csv_content), 
        media_type="text/csv", 
        headers=headers
    )


@router.get("/events/export/pdf")
def export_events_pdf(session: Session = Depends(get_session)):
    statement = select(Event).order_by(Event.date)
    events = session.exec(statement).all()
    payload = [
        {
            "title": event.title,
            "description": event.description,
            "date": event.date,
        }
        for event in events
    ]
    buffer = build_timeline_pdf(payload)
    headers = {
        "Content-Disposition": 'attachment; filename="chronicle-timeline.pdf"'
    }
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)

@router.put("/events/{event_id}", response_model=Event)
def update_event(event_id: str, payload: Event, session: Session = Depends(get_session)):
    payload.date = _normalize_date(payload.date)
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    event.title = payload.title
    event.description = payload.description
    event.date = payload.date
    event.timeline = payload.timeline or "Default"
    event.emotion = payload.emotion
    event.tags = payload.tags

    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@router.post("/events/import/csv")
async def import_events_csv(file: UploadFile = File(...), session: Session = Depends(get_session)):
    """
    Import events from CSV file.
    Expected CSV format: title,description,date,timeline,emotion,tags
    Date format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    Timeline is optional, defaults to "Default"
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read the CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        imported_events = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header row
            try:
                # Validate required fields
                if not row.get('title') or not row.get('description') or not row.get('date'):
                    errors.append(f"Row {row_num}: Missing required fields (title, description, date)")
                    continue
                
                # Parse date - handle various formats
                date_str = row['date'].strip()
                try:
                    # Try datetime first (YYYY-MM-DD HH:MM:SS)
                    if ' ' in date_str:
                        event_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    else:
                        # Try date only (YYYY-MM-DD) - set time to noon
                        event_date = datetime.strptime(date_str, '%Y-%m-%d').replace(hour=12)
                except ValueError:
                    try:
                        # Try ISO format
                        event_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid date format '{date_str}'. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS")
                        continue
                
                # Create event
                event = Event(
                    title=row['title'].strip(),
                    description=row['description'].strip(),
                    date=event_date,
                    timeline=row.get('timeline', '').strip() or "Default",
                    emotion=row.get('emotion', '').strip() or None,
                    tags=row.get('tags', '').strip() or None
                )
                
                session.add(event)
                imported_events.append(event)
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                continue
        
        # Commit all valid events
        if imported_events:
            session.commit()
            for event in imported_events:
                session.refresh(event)
        
        return {
            "message": f"Successfully imported {len(imported_events)} events",
            "imported_count": len(imported_events),
            "error_count": len(errors),
            "errors": errors,
            "events": imported_events
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")


@router.get("/events/stats")
def get_database_stats(session: Session = Depends(get_session)):
    """Get database statistics"""
    try:
        # Count total events
        statement = select(Event)
        events = session.exec(statement).all()
        
        # Get date range if events exist
        if events:
            dates = [event.date for event in events]
            earliest_date = min(dates)
            latest_date = max(dates)
        else:
            earliest_date = None
            latest_date = None
        
        return {
            "total_events": len(events),
            "earliest_event": earliest_date,
            "latest_event": latest_date,
            "database_status": "healthy"
        }
    except Exception as e:
        return {
            "total_events": 0,
            "database_status": "error",
            "error": str(e)
        }


@router.post("/events/seed")
def seed_sample_events(session: Session = Depends(get_session)):
    """Add sample events for testing purposes"""
    try:
        # Sample events data
        sample_events = [
            {
                "title": "Project Started",
                "description": "Beginning of the Chronicle project development",
                "date": datetime(2025, 1, 15, 9, 0, 0),
                "timeline": "Work Projects",
                "emotion": "excited",
                "tags": "development,milestone"
            },
            {
                "title": "First Release",
                "description": "Released the initial version with basic timeline functionality",
                "date": datetime(2025, 3, 20, 14, 30, 0),
                "timeline": "Work Projects",
                "emotion": "accomplished",
                "tags": "release,milestone"
            },
            {
                "title": "User Feedback",
                "description": "Received valuable feedback from early users",
                "date": datetime(2025, 4, 5, 11, 15, 0),
                "timeline": "Work Projects",
                "emotion": "thoughtful",
                "tags": "feedback,improvement"
            },
            {
                "title": "Morning Workout",
                "description": "Started a new fitness routine",
                "date": datetime(2025, 10, 1, 7, 0, 0),
                "timeline": "Personal Life",
                "emotion": "energetic",
                "tags": "health,fitness"
            },
            {
                "title": "CSV Feature Added",
                "description": "Implemented CSV import and export functionality",
                "date": datetime(2025, 10, 10, 16, 45, 0),
                "timeline": "Work Projects",
                "emotion": "satisfied",
                "tags": "feature,enhancement"
            },
            {
                "title": "Testing Panel Created",
                "description": "Added a testing panel with database management tools",
                "date": datetime(2025, 10, 10, 18, 0, 0),
                "timeline": "Work Projects",
                "emotion": "productive",
                "tags": "testing,development,tools"
            },
            {
                "title": "Client Issue Reported",
                "description": "Client texted about urgent production system issue",
                "date": datetime(2025, 10, 10, 8, 45, 0),
                "timeline": "Client Communications",
                "emotion": "concerned",
                "tags": "urgent,client,support"
            }
        ]
        
        created_events = []
        for event_data in sample_events:
            event = Event(**event_data)
            session.add(event)
            created_events.append(event)
        
        session.commit()
        
        for event in created_events:
            session.refresh(event)
        
        return {
            "message": f"Successfully seeded {len(created_events)} sample events",
            "created_count": len(created_events),
            "events": created_events
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error seeding data: {str(e)}")


@router.delete("/events/")
def clear_all_events(session: Session = Depends(get_session)):
    """Clear all events from the database - USE WITH CAUTION"""
    try:
        # Get all events
        statement = select(Event)
        events = session.exec(statement).all()
        event_count = len(events)
        
        # Delete all events
        for event in events:
            session.delete(event)
        
        session.commit()
        
        return {
            "message": f"Successfully cleared {event_count} events from database",
            "deleted_count": event_count
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")


@router.delete("/events/{event_id}")
def delete_event(event_id: str, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    session.delete(event)
    session.commit()
    return {"deleted": event_id}
