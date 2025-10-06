from fastapi import FastAPI
from sqlmodel import SQLModel, Session, select
from fastapi.middleware.cors import CORSMiddleware
from db import engine, get_session
from models import Event

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/events/")
def create_event(event: Event, session: Session = get_session()):
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@app.get("/events/")
def list_events(session: Session = get_session()):
    events = session.exec(select(Event).order_by(Event.date)).all()
    return events

@app.put("/events/{id}")
def update_event(id: int, updated: Event, session: Session = get_session()):
    event = session.get(Event, id)
    if not event: return {"error": "Event not found"}
    event.title = updated.title
    event.description = updated.description
    event.date = updated.date
    session.add(event)
    session.commit()
    return event

@app.delete("/events/{id}")
def delete_event(id: int, session: Session = get_session()):
    event = session.get(Event, id)
    if event:
        session.delete(event)
        session.commit()
    return {"deleted": id}