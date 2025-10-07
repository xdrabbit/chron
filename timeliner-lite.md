Excellent — that’s exactly how you should do it.
 We’ll call this version **Chronicle — Minimal Prototype Build (MVP v0.1)**.



------

```markdown
# 🧱 DEVELOPMENT SCRIPT: “Chronicle” – Minimal Prototype (MVP v0.1)

## PURPOSE
This is the **bare minimum working prototype** of Chronicle — a local event diary that allows users to:
- Create and store events with date, title, and description
- View all events in chronological order (timeline)
- Edit or delete events  

All data is stored locally (SQLite).  
No AI, transcription, or external APIs in this version.  

The goal: produce a small, stable, testable local app that demonstrates the core event logging and timeline display.

---

## SYSTEM OVERVIEW
**Stack**
- Backend: FastAPI (Python 3.11)
- Database: SQLite
- Frontend: React + Vite + Tailwind
- Communication: REST API via Axios

**Local Run:**  
Backend (Uvicorn) + Frontend (Vite) — no dependencies on internet or third-party services.

---

## CORE FEATURES (MVP)
| Feature | Description |
|----------|--------------|
| Add Event | Create event with title, description, and date |
| List Events | Display all events sorted by date |
| Edit Event | Update event text or date |
| Delete Event | Remove an event |
| Timeline View | Simple visual list ordered by date |

---

## FILE STRUCTURE
```

chronicle/
 ├── backend/
 │   ├── main.py
 │   ├── models.py
 │   ├── db.py
 │   └── requirements.txt
 ├── frontend/
 │   ├── index.html
 │   ├── vite.config.js
 │   └── src/
 │       ├── main.jsx
 │       ├── App.jsx
 │       ├── components/
 │       │   ├── EventForm.jsx
 │       │   └── Timeline.jsx
 │       └── services/api.js
 └── data/
 └── chronicle.db

```
---

## BACKEND (FastAPI)
Handles local data storage and event CRUD.

**Dependencies**
```bash
fastapi
uvicorn
sqlmodel
pydantic
```

**Database Schema**

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**API Endpoints**

| Method | Path           | Description                      |
| ------ | -------------- | -------------------------------- |
| POST   | `/events/`     | Create a new event               |
| GET    | `/events/`     | List all events (sorted by date) |
| PUT    | `/events/{id}` | Edit an event                    |
| DELETE | `/events/{id}` | Delete an event                  |

**Example main.py**

```python
from fastapi import FastAPI
from sqlmodel import SQLModel, Session, select
from fastapi.middleware.cors import CORSMiddleware
from db import engine, get_session
from models import Event

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/events/")
def create_event(event: Event, session: Session = get_session()):
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@app.get("/events/")
def list_events(session: Session = get_session()):
    events = session.exec(select(Event).order_by(Event.date)).all()
    return events

@app.put("/events/{id}")
def update_event(id: int, updated: Event, session: Session = get_session()):
    event = session.get(Event, id)
    if not event: return {"error": "Event not found"}
    event.title = updated.title
    event.description = updated.description
    event.date = updated.date
    session.add(event)
    session.commit()
    return event

@app.delete("/events/{id}")
def delete_event(id: int, session: Session = get_session()):
    event = session.get(Event, id)
    if event:
        session.delete(event)
        session.commit()
    return {"deleted": id}
```

**db.py**

```python
from sqlmodel import create_engine, Session

engine = create_engine("sqlite:///data/chronicle.db")

def get_session():
    with Session(engine) as session:
        yield session
```

------

## FRONTEND (React + Vite)

Simple interface for event input and display.

**Dependencies**

```bash
react
react-dom
vite
axios
tailwindcss
date-fns
```

**Components**

```
EventForm.jsx
import { useState } from "react";
import axios from "axios";

export default function EventForm({ onSave }) {
  const [form, setForm] = useState({ title: "", description: "", date: "" });

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    await axios.post("http://localhost:8000/events/", form);
    setForm({ title: "", description: "", date: "" });
    onSave();
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2 p-2">
      <input name="title" placeholder="Title" value={form.title} onChange={handleChange} className="border p-2 rounded" />
      <textarea name="description" placeholder="Description" value={form.description} onChange={handleChange} className="border p-2 rounded" />
      <input type="date" name="date" value={form.date} onChange={handleChange} className="border p-2 rounded" />
      <button type="submit" className="bg-blue-600 text-white p-2 rounded">Add Event</button>
    </form>
  );
}
Timeline.jsx
import { useEffect, useState } from "react";
import axios from "axios";

export default function Timeline() {
  const [events, setEvents] = useState([]);

  const loadEvents = async () => {
    const res = await axios.get("http://localhost:8000/events/");
    setEvents(res.data);
  };

  useEffect(() => { loadEvents(); }, []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2">Timeline</h2>
      <ul className="space-y-2">
        {events.map(e => (
          <li key={e.id} className="border rounded p-2">
            <div className="font-semibold">{e.title}</div>
            <div className="text-sm text-gray-600">{new Date(e.date).toLocaleDateString()}</div>
            <div>{e.description}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
App.jsx
import EventForm from "./components/EventForm";
import Timeline from "./components/Timeline";
import { useState } from "react";

export default function App() {
  const [refresh, setRefresh] = useState(0);
  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Chronicle MVP</h1>
      <EventForm onSave={() => setRefresh(refresh + 1)} />
      <Timeline key={refresh} />
    </div>
  );
}
```

------

## HOW TO RUN LOCALLY

**1. Backend**

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**2. Frontend**

```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173/).

------

## HANDOFF INSTRUCTIONS (For Agent or Tester)

> Read this entire script.
>  Create all files and directories as specified.
>  Ensure backend starts successfully and frontend connects to `localhost:8000`.
>  Verify that events can be created, displayed, and deleted.
>  No AI or external API dependencies are to be implemented in this version.
>  Keep codebase minimal, readable, and self-contained.

------

**End of Minimal Development Script (Chronicle MVP v0.1)**

```
---

Would you like me to drop this version into the same canvas as a *second document* (so we can keep v1 “full spec” and v0.1 “MVP” separate)?
```