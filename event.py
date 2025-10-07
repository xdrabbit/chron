from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    date: date
