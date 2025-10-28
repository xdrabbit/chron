from typing import List, Optional
from datetime import datetime
import uuid
from sqlmodel import SQLModel, Field, Relationship
from pydantic import validator

class EventParticipantLink(SQLModel, table=True):
    event_id: Optional[str] = Field(default=None, foreign_key="event.id", primary_key=True)
    participant_id: Optional[int] = Field(default=None, foreign_key="participant.id", primary_key=True)

class Event(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    description: str
    date: datetime
    timeline: str = Field(default="Default")
    emotion: Optional[str] = None
    tags: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('date', 'created_at', pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, str):
            try:
                # Handle ISO format with or without microseconds
                if '.' in v:
                    return datetime.fromisoformat(v.replace('Z', '+00:00'))
                else:
                    return datetime.fromisoformat(v)
            except ValueError:
                # Fallback for other formats
                try:
                    return datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
        return v
    # Audio and transcription fields
    audio_file: Optional[str] = None  # Path to audio file
    transcription_words: Optional[str] = None  # JSON string of word-level timestamps
    summary: Optional[str] = None  # Smart summary (snippet + key topics)
    # Legal workflow fields
    actor: Optional[str] = None  # Who was responsible: Tom, Lisa, Realtor, Court, etc.
    evidence_links: Optional[str] = None  # URLs or file paths to supporting evidence
    privileged_notes: Optional[str] = None  # Attorney work product - NOT exported to PDF
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
    # All new fields are optional to maintain backward compatibility
    original_filename: Optional[str] = Field(default=None)
    file_size: Optional[int] = Field(default=None)
    mime_type: Optional[str] = Field(default=None)
    parsed_content: Optional[str] = Field(default=None)
    page_count: Optional[int] = Field(default=None)
    word_count: Optional[int] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    event: Event = Relationship(back_populates="attachments")
    
    @validator('created_at', pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                try:
                    return datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
        return v
