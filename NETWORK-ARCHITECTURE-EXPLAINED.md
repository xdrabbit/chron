# Chronicle Network Architecture - How It Actually Works

## Your Current Setup (The Reality!)

```
┌─────────────────────────────────────────────────────────────┐
│ thomas-mac-mini (M1) - YOUR WORKSTATION                     │
│ • Browser (Chrome/Safari/Firefox)                            │
│ • dev server                │
│ • LAN: 192.168.0.12                                          │
│ • Tailscale: 100.108.73.70 (for remote access)              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ HTTP over LAN (192.168.0.x network)
                 │ Frontend → Backend API calls
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ linuxmacmini (2015 i5) - BACKEND SERVER (no GUI)           │
│ • FastAPI backend on :8000                                   │
│ • Ollama LLM on :11434                                       │
│ • SQLite database                                            │
│ • Whisper.cpp (CPU fallback)                                 │
│ • Python virtualenv: backend/.venv                           │
│ • LAN: 192.168.0.15                                          │
│ • Tailscale: 100.104.39.64 (for remote access)              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Optional: GPU acceleration over LAN
                 │ (only when needed for Whisper)
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ oasis-wsl2 (Windows 11 + Ubuntu WSL)                        │
│ • RTX 3060 GPU                                               │
│ • Whisper GPU service                                        │
│ • Optional: Ollama for larger models                         │
│ • LAN: 192.168.0.45 (Windows host)                          │
│ • Tailscale: 100.89.178.59 (WSL2)                           │
└─────────────────────────────────────────────────────────────┘
```
