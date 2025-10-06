from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)