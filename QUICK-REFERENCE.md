# Chronicle Quick Reference - LAN vs Remote Setup

## 🏠 At Home (LAN - Use This!)

### On linuxmacmini:
```bash
export OLLAMA_URL="http://localhost:11434"
export WHISPER_GPU_URL="http://192.168.0.45:8001"
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### On thomas-mac-mini (your Mac):
```bash
# Create frontend/.env.local:
echo "VITE_API_URL=http://192.168.0.15:8000" > frontend/.env.local

# Start frontend:
cd frontend && npm run dev

# Visit in browser (Vite default port):
http://localhost:5173

# Or from Mac to linuxmacmini:
http://192.168.0.15:5173
```

**Why?** LAN = 1-5ms latency, Tailscale = 10-50ms

---

## 🌍 Away from Home (Remote)

### On linuxmacmini:
```bash
export OLLAMA_URL="http://localhost:11434"
export WHISPER_GPU_URL="https://oasis-wsl2.tail42ac25.ts.net"
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### On thomas-mac-mini (anywhere):
```bash
# Switch to remote config:
./switch-environment.sh  # Choose option 2

# Or manually:
echo "VITE_API_URL=https://linuxmacmini.tail42ac25.ts.net:8000" > frontend/.env.local

# Start frontend:
cd frontend && npm run dev

# Visit via Tailscale
```

---

## 🚀 One-Time Setup

```bash
# On linuxmacmini:
./complete-setup.sh

# This sets everything up automatically!
```

---

## 📊 Quick Tests

```bash
# Test backend:
curl http://192.168.0.15:8000/events/

# Test Ollama:
curl http://localhost:11434/api/tags

# Test AI performance:
python3 test_performance.py

# View metrics:
curl http://192.168.0.15:8000/ask/metrics
```

---

## 🔧 Troubleshooting

**Frontend can't connect to backend?**
- Check frontend/.env.local has correct VITE_API_URL
- Restart Vite after changing .env: `npm run dev`

**Backend not responding?**
- Check it's running: `ps aux | grep uvicorn`
- Check logs: `tail -f backend.log`

**Ollama too slow?**
- First request is always slow (model loading)
- Keep Ollama running: `ollama serve`
- Monitor: `ollama ps`

---

## 💡 Remember

- **At home**: Use LAN IPs (192.168.0.x) - FASTEST
- **Remote**: Use Tailscale - SECURE
- **Browser**: Always runs on your Mac (thomas-mac-mini)
- **Backend**: Always runs on linuxmacmini (no GUI needed)

---

## 📚 Full Docs

- `NETWORK-ARCHITECTURE-EXPLAINED.md` - How it all works
- `AI-LATENCY-OPTIMIZATIONS.md` - Technical details
- `ENVIRONMENT-SETUP.md` - Configuration guide
