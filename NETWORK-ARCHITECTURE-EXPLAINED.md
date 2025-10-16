# Chronicle Network Architecture - How It Actually Works

## Your Current Setup (The Reality!)

```
┌─────────────────────────────────────────────────────────────┐
│ thomas-mac-mini (M1) - YOUR WORKSTATION                     │
│ • Browser (Chrome/Safari/Firefox)                            │
│ • Vite dev server (npm run dev) on :3000                    │
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

## What You See in Browser

When you type `localhost:3000`:
1. ✅ Browser connects to Vite dev server on **your Mac** (localhost = 192.168.0.12)
2. ✅ Frontend JavaScript runs in **your browser**
3. ✅ Frontend makes API calls to backend URL (determined by `api.js`)
4. ✅ By default, it uses `window.location.hostname` which is `localhost` or `thomas-mac-mini`
5. ✅ Browser resolves this and connects to `http://192.168.0.15:8000` (linuxmacmini)

## The Smart URL Resolution

The frontend code in `src/services/api.js`:

```javascript
const resolveBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    return envUrl;  // Explicit override
  }

  if (typeof window !== "undefined") {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:8000`;  // Smart detection
  }

  return "http://localhost:8000";  // Fallback
};
```

**What this means:**
- If you access via `http://thomas-mac-mini:3000` → backend is `http://thomas-mac-mini:8000`
- If you access via `http://192.168.0.12:3000` → backend is `http://192.168.0.12:8000`
- If you access via `http://localhost:3000` → backend is `http://localhost:8000`

**The Issue:** When using `localhost`, it tries to connect to port 8000 on **your Mac**, not linuxmacmini!

## Optimal Configuration for LAN

### Option 1: Access via hostname (RECOMMENDED)

```bash
# On thomas-mac-mini browser, visit:
http://thomas-mac-mini:3000

# Frontend will automatically use:
http://thomas-mac-mini:8000
```

This works because:
- Your Mac can route to linuxmacmini via LAN
- No need for Tailscale overhead
- Uses fast LAN network (1Gbps vs Tailscale overhead)

### Option 2: Set explicit backend URL (BEST FOR DEVELOPMENT)

Create `.env` in frontend directory:

```bash
# frontend/.env
VITE_API_URL=http://192.168.0.15:8000
```

Then restart Vite:
```bash
cd frontend
npm run dev
```

Now you can use `localhost:3000` and it will correctly connect to linuxmacmini!

### Option 3: Use IP address directly

```bash
# In browser:
http://192.168.0.12:3000

# Frontend will use:
http://192.168.0.12:8000
```

## Recommended LAN Configuration

### For linuxmacmini backend:

```bash
# Use LAN IPs, not Tailscale!
export OLLAMA_URL="http://localhost:11434"  # Local Ollama on same machine
export WHISPER_GPU_URL="http://192.168.0.45:8001"  # oasis over LAN (if needed)
```

### For frontend on thomas-mac-mini:

```bash
# frontend/.env
VITE_API_URL=http://192.168.0.15:8000
```

## When to Use Tailscale

**Use Tailscale ONLY when:**
- You're away from home (coffee shop, traveling, etc.)
- You need secure remote access
- You're on a different network

**On LAN, use local IPs:**
- Faster (no encryption overhead)
- Lower latency
- No bandwidth limits
- Simpler debugging

## Performance Comparison

### LAN (192.168.0.x):
- Latency: 1-5ms
- Bandwidth: 1Gbps (or your network speed)
- Overhead: None

### Tailscale (100.x.x.x) on same LAN:
- Latency: 10-50ms (encryption + routing)
- Bandwidth: Still good, but encrypted
- Overhead: WireGuard encryption/decryption

**For AI requests on LAN: 192.168.0.x is MUCH faster!**

## Recommended Setup Scripts

### For Home/LAN use:

```bash
# frontend/.env.local
VITE_API_URL=http://192.168.0.15:8000

# linuxmacmini ~/.bashrc
export OLLAMA_URL="http://localhost:11434"
export WHISPER_GPU_URL="http://192.168.0.45:8001"  # If using GPU
```

### For Remote use (via Tailscale):

```bash
# frontend/.env.production
VITE_API_URL=https://linuxmacmini.tail42ac25.ts.net:8000

# linuxmacmini ~/.bashrc (remote mode)
export OLLAMA_URL="http://localhost:11434"
export WHISPER_GPU_URL="https://oasis-wsl2.tail42ac25.ts.net"
```

## How to Test

### Check what URL frontend is using:

```javascript
// In browser console (F12):
console.log(window.location.hostname);
// Should show: "thomas-mac-mini" or "192.168.0.12"

// Check API base URL:
fetch('/api/events')  // Look at network tab to see actual URL
```

### Test backend connectivity:

```bash
# From thomas-mac-mini terminal:
curl http://192.168.0.15:8000/events/

# Test Ollama on linuxmacmini:
curl http://192.168.0.15:11434/api/tags
```

## Summary

**Your Understanding is Correct!**
- ✅ Browser runs on your Mac (thomas-mac-mini)
- ✅ You don't need GUI on linuxmacmini
- ✅ Tailscale is overkill on your LAN
- ✅ Use local IPs (192.168.0.x) for best performance

**Set this once and forget:**

```bash
# On thomas-mac-mini
cd ~/lnx_mac_int_drv/dev/chron/frontend
echo "VITE_API_URL=http://192.168.0.15:8000" > .env.local

# Restart frontend
npm run dev

# Now visit: http://localhost:3000
# It will correctly connect to linuxmacmini backend!
```

**Expected improvement:**
- LAN latency: ~2ms vs Tailscale ~20ms
- Combined with our optimizations: **Even faster than tested!**

---

**Bottom line:** Use LAN IPs at home, save Tailscale for remote access! 🏠→⚡ 🌍→🔐
