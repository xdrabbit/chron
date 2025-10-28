from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
import os

# Import all models to ensure they are registered with SQLModel
from models import Event, Participant, Attachment, EventParticipantLink
from db.base import engine
from db.fts import create_fts_table
from routes.events import router as events_router
from routes.transcribe import router as transcribe_router
from routes.analyze import router as analyze_router
from routes.search import router as search_router
# AI features disabled - FTS5 search is instant and sufficient for timeline queries
# from routes.ask import router as ask_router

app = FastAPI()

# Mount static files for serving uploaded audio
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.include_router(events_router)
app.include_router(transcribe_router)
app.include_router(analyze_router)
app.include_router(search_router)
# app.include_router(ask_router)  # Disabled - use FTS5 search instead

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
    
    # Note: Auto-warmup disabled - use FTS5 search or manually warmup with:
    # curl -X POST http://localhost:8000/ask/warmup
    # Or just wait ~90s on first AI request
