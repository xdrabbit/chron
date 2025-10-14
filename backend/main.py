from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

# Import all models to ensure they are registered with SQLModel
from backend.models import Event, Participant, Attachment, EventParticipantLink
from backend.db.base import engine
from backend.db.fts import create_fts_table
from backend.routes.events import router as events_router
from backend.routes.transcribe import router as transcribe_router
from backend.routes.analyze import router as analyze_router
from backend.routes.search import router as search_router

app = FastAPI()
app.include_router(events_router)
app.include_router(transcribe_router)
app.include_router(analyze_router)
app.include_router(search_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    # Create FTS5 table for full-text search
    create_fts_table()
