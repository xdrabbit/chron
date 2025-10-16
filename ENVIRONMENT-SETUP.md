# Environment Configuration for Multi-Machine Setup

## Your Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ thomas-mac-mini (M1) - Your Workstation                     │
│ • Frontend (Vite/React)                                      │
│ • Local: 192.168.0.12                                        │
│ • Tailscale: 100.108.73.70                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ linuxmacmini (2015 i5) - Chronicle Backend                  │
│ • FastAPI backend                                            │
│ • SQLite database                                            │
│ • Ollama LLM (llama3.2) - **RUNS HERE**                     │
│ • CPU Whisper (fallback)                                     │
│ • Local: 192.168.0.15                                        │
│ • Tailscale: 100.104.39.64                                   │
│ • Funnel: https://linuxmacmini.tail42ac25.ts.net            │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ (Optional GPU acceleration)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ oasis-wsl2 (Ubuntu WSL) - GPU Whisper Service               │
│ • GPU: RTX 3060                                              │
│ • CUDA Whisper transcription                                 │
│ • Tailscale: 100.89.178.59                                   │
│ • Funnel: https://oasis-wsl2.tail42ac25.ts.net              │
└─────────────────────────────────────────────────────────────┘
```

## Environment Configuration

### Option 1: Ollama on linuxmacmini (Recommended for Speed)

If Ollama on linuxmacmini is fast enough (which it should be with our optimizations!):

```bash
# On linuxmacmini - .env or export these
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.2"

# Optional: Use oasis-wsl2 for GPU Whisper
export WHISPER_GPU_URL="https://oasis-wsl2.tail42ac25.ts.net"
```

**Benefits:**
- ✅ Zero network latency for LLM (localhost)
- ✅ Connection pooling works perfectly (local Unix socket)
- ✅ Sub-2 second responses likely
- ✅ Optional GPU whisper for audio

### Option 2: Ollama on oasis-wsl2 (For Better Model Performance)

If you need larger models or faster inference:

```bash
# On linuxmacmini - .env or export these
export OLLAMA_URL="http://100.89.178.59:11434"  # or https://oasis-wsl2.tail42ac25.ts.net:11434
export OLLAMA_MODEL="llama3.2"  # or larger models

# GPU Whisper on same machine
export WHISPER_GPU_URL="https://oasis-wsl2.tail42ac25.ts.net"
```

**Benefits:**
- ✅ RTX 3060 acceleration for faster inference
- ✅ Can run larger models (llama3.2:7b, mixtral)
- ✅ Connection pooling reduces Tailscale overhead
- ⚠️  Small network latency (~10-50ms on Tailscale)

## Important: LAN vs Tailscale

**You're on the same LAN!** When at home:
- ✅ Use LAN IPs (192.168.0.x) - MUCH faster
- ❌ Don't use Tailscale IPs (100.x.x.x) - unnecessary overhead
- 💡 Save Tailscale for when you're away from home

**LAN Performance:**
- Latency: 1-5ms
- No encryption overhead
- Direct gigabit connection

**Tailscale on same LAN:**
- Latency: 10-50ms
- WireGuard encryption overhead
- Good for remote, overkill for home

## Recommended Configuration

### Start with Option 1 (Local Ollama)

The optimizations make local Ollama **very fast**:
1. Connection pooling eliminates setup overhead
2. Reduced context window (1024 tokens) speeds inference
3. Smaller models (llama3.2) are plenty smart for timeline queries

**Test it:**
```bash
# On linuxmacmini
cd /home/tom/lnx_mac_int_drv/dev/chron
python3 test_performance.py
```

### Switch to Option 2 if needed

Only switch to oasis-wsl2 if:
- You need larger models (7B+)
- Timeline queries need more reasoning
- Local performance isn't meeting needs

## Setting Environment Variables

### Backend (linuxmacmini)

For LAN use (recommended at home):
```bash
# Temporary (current session):
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.2"
export WHISPER_GPU_URL="http://192.168.0.45:8001"  # oasis via LAN (if GPU service running)
```

For remote use (when away from home):
```bash
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.2"
export WHISPER_GPU_URL="https://oasis-wsl2.tail42ac25.ts.net"  # oasis via Tailscale
```

### Permanent (add to ~/.bashrc on linuxmacmini):
```bash
echo 'export OLLAMA_URL="http://localhost:11434"' >> ~/.bashrc
echo 'export OLLAMA_MODEL="llama3.2"' >> ~/.bashrc
echo 'export WHISPER_GPU_URL="http://192.168.0.45:8001"' >> ~/.bashrc
source ~/.bashrc
```

### Frontend (thomas-mac-mini - your workstation)

The frontend needs to know where the backend is!

For LAN use (fastest - recommended at home):
```bash
cd frontend
echo "VITE_API_URL=http://192.168.0.15:8000" > .env.local
npm run dev
```

For remote use (when away from home):
```bash
cd frontend
echo "VITE_API_URL=https://linuxmacmini.tail42ac25.ts.net:8000" > .env.local
npm run dev
```

Or use the switcher:
```bash
./switch-environment.sh
```

## Network Optimizations Apply to Both

The optimizations I provided work **even better** for your setup:

### For Localhost (Option 1):
- ✅ Connection pooling uses Unix sockets (ultra-fast)
- ✅ No TCP overhead at all
- ✅ Expected: 1-3 second responses

### For Tailscale (Option 2):
- ✅ Connection pooling reuses Tailscale WireGuard tunnels
- ✅ TCP keepalive prevents tunnel timeouts
- ✅ Reduced context = less data over network
- ✅ Expected: 2-5 second responses

## Testing Both Options

### Test Local (linuxmacmini):
```bash
# Make sure Ollama is running locally
curl http://localhost:11434/api/tags

# Test performance
export OLLAMA_URL="http://localhost:11434"
python3 test_performance.py
```

### Test Remote (oasis-wsl2):
```bash
# Test Ollama connectivity via Tailscale
curl http://100.89.178.59:11434/api/tags

# Test performance
export OLLAMA_URL="http://100.89.178.59:11434"
python3 test_performance.py
```

## My Recommendation

**Start with localhost Ollama** (Option 1):
1. Run optimizations: `./optimize-network.sh`
2. Start Ollama locally: `ollama serve`
3. Keep env vars at defaults (localhost)
4. Test: `python3 test_performance.py`

With the optimizations, your 2015 i5 should handle llama3.2 just fine for timeline queries. The reduced context window and connection pooling make it **much** faster than before.

Only move to oasis-wsl2 if you need:
- Larger models (7B+)
- More complex reasoning
- Faster batch processing

## Monitoring Performance

Check which configuration is faster:
```bash
# View real-time metrics
curl http://localhost:8000/ask/metrics | jq

# Watch backend logs
tail -f backend.log

# Monitor Ollama
ollama ps
```

## Whisper Configuration

For audio transcription, you have options:

1. **GPU (Recommended)**: Set `WHISPER_GPU_URL` to use RTX 3060
2. **CPU Fallback**: Automatic if GPU unavailable
3. **whisper.cpp**: Local, blazing fast for small files

The code automatically tries GPU first, falls back to CPU if needed.

---

**Bottom line:** Start with localhost, let the optimizations work their magic! 🚀
