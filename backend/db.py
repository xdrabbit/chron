from sqlmodel import create_engine, Session
import os

# Create data directory if it doesn't exist
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chronicle.db")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

engine = create_engine(f"sqlite:///{db_path}")

def get_session():
    with Session(engine) as session:
        yield session