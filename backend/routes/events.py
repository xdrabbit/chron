from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
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

@router.get("/events/", response_model=list[Event])
def get_events(session: Session = Depends(get_session)):
    statement = select(Event).order_by(Event.date)
    events = session.exec(statement).all()
    return events


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
def update_event(event_id: int, payload: Event, session: Session = Depends(get_session)):
    payload.date = _normalize_date(payload.date)
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    event.title = payload.title
    event.description = payload.description
    event.date = payload.date

    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@router.delete("/events/{event_id}")
def delete_event(event_id: int, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    session.delete(event)
    session.commit()
    return {"deleted": event_id}
