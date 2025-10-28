╔══════════════════════════════════════════════════════════════════╗
║              IMPORTANT: Correct Ports for Chronicle             ║
╚══════════════════════════════════════════════════════════════════╝

🔍 PORT CONFLICT DISCOVERED!

Port 3000 is used by Gitea (your Git service), NOT Chronicle!

✅ CORRECT PORTS:

  • Chronicle Frontend (Vite): 5173
  • Chronicle Backend (FastAPI): 8000
  • Ollama LLM: 11434
  • Gitea (Git service): 3000  ← This is what you saw!

📱 ACCESS CHRONICLE:

  From your Mac browser, use ONE of these:

  1. Via hostname:
     http://thomas-mac-mini:5173  (if frontend on Mac)
     http://linuxmacmini:5173     (if frontend on linuxmacmini)

  2. Via LAN IP (RECOMMENDED):
     Frontend on Mac → http://192.168.0.12:5173
     Frontend on linuxmacmini → http://192.168.0.15:5173

  3. Via localhost (only if frontend on same machine as browser):
     http://localhost:5173

🎯 WHERE IS FRONTEND RUNNING?

Check which machine is running: npm run dev

  On linuxmacmini:
    ps aux | grep vite
    # If found: Access at http://192.168.0.15:5173 from Mac

  On thomas-mac-mini:
    # You'll run: cd frontend && npm run dev
    # Access at: http://localhost:5173

💡 RECOMMENDED SETUP:

  Run frontend on YOUR MAC (thomas-mac-mini):
    1. Copy the project to your Mac (if not already there)
    2. cd frontend
    3. npm install  (first time only)
    4. npm run dev
    5. Visit: http://localhost:5173

  Backend stays on linuxmacmini (already running):
    • Backend: http://192.168.0.15:8000 ✅
    • Ollama: http://192.168.0.15:11434 ✅

🔧 FRONTEND CONFIG:

  The .env.local already created should have:
    VITE_API_URL=http://192.168.0.15:8000

  This tells frontend where to find backend!

📊 CHECK STATUS:

  Frontend running?
    curl http://192.168.0.15:5173  (or localhost:5173)

  Backend running?
    curl http://192.168.0.15:8000/events/

  Gitea (port 3000)?
    curl http://localhost:3000  ← This is what you saw!

🎯 NEXT STEPS:

  1. Decide where to run frontend:
     • On Mac (thomas-mac-mini) - RECOMMENDED for GUI
     • On linuxmacmini (headless) - Already running on :5173

  2. If frontend already running on linuxmacmini:
     From Mac browser → http://192.168.0.15:5173

  3. If you want frontend on Mac:
     • Stop frontend on linuxmacmini: pkill -f vite
     • On Mac: cd frontend && npm run dev
     • Access: http://localhost:5173

📚 SUMMARY:

  Port 3000 = Gitea (your Git service) 
  Port 5173 = Chronicle frontend (Vite) ← USE THIS!
  Port 8000 = Chronicle backend (FastAPI)

  You should see Chronicle, not "Ashby Legal"!
