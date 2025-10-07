from sqlmodel import create_engine, Session

engine = create_engine("sqlite:///../data/chronicle.db")

def get_session():
    with Session(engine) as session:
        yield session
