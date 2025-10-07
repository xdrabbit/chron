from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from events import router as events_router
from sqlmodel import SQLModel
from db import engine

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
