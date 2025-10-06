# 🧱 chron — Minimal Event Diary MVP

Chron is a local event diary app that lets you:
- Create and store events (date, title, description)
- View all events in a chronological timeline
- Edit or delete events

All data is stored locally (SQLite).  
No external APIs, no AI — just a clean, minimal working prototype.

---

## Stack

- **Backend:** FastAPI (Python 3.11), SQLite, SQLModel
- **Frontend:** React + Vite + Tailwind CSS
- **Communication:** REST API via Axios

---

## Local Development

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173/).

---

## File Structure

```
chron/
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

## Handoff Notes

- Backend should start successfully and frontend should connect to `localhost:8000`
- Verify events can be created, displayed, updated, and deleted
- No external dependencies required

**End of Minimal Development Script (Chron MVP v0.1)**