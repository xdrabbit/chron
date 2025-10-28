# 🧱 Chronicle — AI-Powered Event Timeline

Chronicle is a comprehensive event timeline application that combines local storage with AI-powered features for efficient event management and documentation.

## ✨ Features

- **Event Management**: Create, edit, and delete timeline events with rich metadata
- **AI CSV Import**: Paste CSV data from AI assistants (ChatGPT, Claude) directly into your timeline
- **Voice Transcription**: Record and transcribe audio events with automatic timeline integration
- **Full-Text Search**: Powerful FTS5 search across events and attached documents
- **Document Management**: Upload and search through PDF documents attached to events
- **Timeline Visualization**: Multiple timeline views including swim lanes and visual timelines
- **Export Capabilities**: Export your timeline data to CSV
- **Local-First**: All data stored locally in SQLite, no external dependencies required

## 🛠️ Stack

- **Backend:** FastAPI (Python), SQLite with FTS5, SQLModel
- **Frontend:** React + Vite + Tailwind CSS
- **AI Integration:** Local Ollama models for transcription and NLP
- **Communication:** REST API with Axios

## 🚀 Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Ollama (for AI features)

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173).

### 3. AI Features (Optional)

For voice transcription and AI analysis:
```bash
# Install Ollama and pull models
ollama pull llama3.2
ollama pull whisper
```

## 📁 Project Structure

```
chron/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── models.py              # SQLModel database models
│   ├── db/                    # Database utilities
│   ├── routes/                # API endpoints
│   ├── services/              # Business logic (Ollama, Whisper, etc.)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   └── services/         # API client
│   └── package.json
├── data/                      # SQLite database
├── whisper-gpu/              # GPU-accelerated transcription
└── docs/                     # Documentation
```

## 🔄 Recent Updates

### v1.0.0 (October 2025)
- ✅ **CSV Import Fix**: Resolved state persistence issues in AI CSV import
- ✅ **Voice Transcription**: Added complete voice recording and transcription workflow
- ✅ **Document Search**: Full-text search across uploaded documents
- ✅ **Timeline Views**: Multiple visualization options including swim lanes
- ✅ **Merge to Main**: Feature branch successfully merged with all tests passing

## 🧪 Testing

Run the comprehensive smoke test suite:

```bash
python3 test_smoke.py
```

This tests all API endpoints, CRUD operations, search, export, and document management.

## 📚 Documentation

- [Network Architecture](NETWORK-ARCHITECTURE-EXPLAINED.md)
- [Deployment Guide](DEPLOYMENT.md)
- [AI Integration](OLLAMA-CACHING-EXPLAINED.md)
- [Voice Transcription](whisper-gpu/README.md)

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Run smoke tests: `python3 test_smoke.py`
4. Submit a pull request

## 📄 License

This project is for personal/local use. All data remains on your local machine.