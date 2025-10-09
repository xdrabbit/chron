from typing import List, Optional
from datetime import datetime
import uuid
from sqlmodel import SQLModel, Field, Relationship

class EventParticipantLink(SQLModel, table=True):
    event_id: Optional[str] = Field(default=None, foreign_key="event.id", primary_key=True)
    participant_id: Optional[int] = Field(default=None, foreign_key="participant.id", primary_key=True)

class Event(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    description: str
    date: datetime
    emotion: Optional[str] = None
    tags: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    attachments: List["Attachment"] = Relationship(back_populates="event")
    participants: List["Participant"] = Relationship(back_populates="events", link_model=EventParticipantLink)

class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    events: List[Event] = Relationship(back_populates="participants", link_model=EventParticipantLink)

class Attachment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(foreign_key="event.id")
    file_path: str
    file_type: str
    event: Event = Relationship(back_populates="attachments")
