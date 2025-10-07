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

## Features

✅ **Full CRUD Operations**
- Create events with title, description, and date
- View all events in chronological timeline order
- Edit existing events
- Delete events with confirmation

✅ **Modern UI**
- Clean, responsive design with Tailwind CSS
- Gradient background with card-based layout
- Hover effects and smooth transitions
- Loading states and error handling

✅ **Backend API**
- RESTful API with FastAPI
- SQLite database with SQLModel ORM
- CORS enabled for frontend communication
- Automatic database table creation

---

## File Structure

```
chron/
 ├── backend/
 │   ├── main.py
 │   ├── events.py
 │   ├── models.py
 │   ├── db.py
 │   └── requirements.txt
 ├── frontend/
 │   ├── index.html
 │   ├── package.json
 │   ├── vite.config.js
 │   ├── tailwind.config.js
 │   ├── postcss.config.js
 │   └── src/
 │       ├── main.jsx
 │       ├── App.jsx
 │       ├── index.css
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