from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel
from datetime import date
from models import Event
from db import get_session

router = APIRouter(prefix="/events", tags=["events"])

class EventCreate(BaseModel):
    title: str
    description: str
    date: date

class EventUpdate(BaseModel):
    title: str
    description: str
    date: date

@router.get("/", response_model=List[Event])
def get_events(session: Session = Depends(get_session)):
    """Get all events"""
    events = session.exec(select(Event).order_by(Event.date)).all()
    return events

@router.get("/{event_id}", response_model=Event)
def get_event(event_id: int, session: Session = Depends(get_session)):
    """Get a specific event by ID"""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.post("/", response_model=Event)
def create_event(event_data: EventCreate, session: Session = Depends(get_session)):
    """Create a new event"""
    event = Event(
        title=event_data.title,
        description=event_data.description,
        date=event_data.date
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@router.put("/{event_id}", response_model=Event)
def update_event(event_id: int, event_data: EventUpdate, session: Session = Depends(get_session)):
    """Update an existing event"""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.title = event_data.title
    event.description = event_data.description
    event.date = event_data.date
    
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@router.delete("/{event_id}")
def delete_event(event_id: int, session: Session = Depends(get_session)):
    """Delete an event"""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    session.delete(event)
    session.commit()
    return {"message": "Event deleted successfully"}
