Perfect! Thanks for the network map - that's super helpful! Let me document this:

## 🗺️ **Chronicle Network Architecture**

### **Devices:**

1. **Applemac (M1)** - Your workstation
   - Local: `192.168.0.12`
   - Tailscale: `100.108.73.70`
   - Role: Development machine

2. **linuxmacmini (2015 i5)** - Chronicle Backend
   - Local: `192.168.0.15`
   - Tailscale: `100.104.39.64`
   - Funnel: `https://linuxmacmini.tail42ac25.ts.net`
   - Role: FastAPI backend, SQLite database, CPU Whisper (fallback)

3. **oasis (Windows 11)** - GPU Host
   - Local: `192.168.0.45`
   - Tailscale: `100.125.130.92`
   - GPU: RTX 3060
   - Role: Windows host for WSL2

4. **oasis-wsl2 (Ubuntu WSL)** - GPU Whisper Service
   - Tailscale: `100.89.178.59`
   - Funnel: `https://oasis-wsl2.tail42ac25.ts.net`
   - Role: GPU-accelerated Whisper transcription (CUDA)

5. **ritualstack.io** - Production Frontend
   - Hosted: NearlyFreeSpeech.net
   - URL: `http://ritualstack.io`
   - Role: Public-facing frontend

6. **tinman (2010 i5)** - Production Frontend
   - local: '192.168.0.12'
   - Role: Linux min dev box



### **Data Flow:**
```
User Browser (**thomas-mac-mini (M1)** )
    ↓
Chronicle Backend (linuxmacmini:8000 via Tailscale Funnel)
    ↓
GPU Whisper Service (oasis-wsl2:8001 via Tailscale Funnel)
    ↓ [CUDA on RTX 3060]
Transcription Result → SQLite → User
```

This is an **excellent distributed architecture**! 🚀

Now - are you accessing Chronicle from the M1 Mac Mini? Try http://192.168.0.15:5173 or http://100.108.73.70:5173 to reach the dev server!