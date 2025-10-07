from fastapi import FastAPI
from events import router as events_router
from sqlmodel import SQLModel
from db import engine

app = FastAPI()
app.include_router(events_router)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
