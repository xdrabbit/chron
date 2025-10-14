# Chronicle Deployment Summary

## What We Have Now

### Frontend (Static Site)
- **Hosted on:** NearlyFreeSpeech.net (NFSN)
- **URLs:** 
  - http://ritualstack.io (main)
  - http://chronicle.ritualstack.io (alias)
- **Location:** `/home/public` on NFSN server
- **Note:** Both domains point to the same files (they're aliases)

### Backend (FastAPI)
- **Running on:** Your Linux Mac Mini (linuxmacmini)
- **Local address:** http://192.168.0.15:8000 or http://100.104.39.64:8000 (Tailscale)
- **Public address:** https://linuxmacmini.tail42ac25.ts.net/
- **Exposed via:** Tailscale Funnel (makes it publicly accessible over HTTPS)

### How It Works Together

```
User Browser
    ↓
http://chronicle.ritualstack.io (NFSN)
    ↓
Loads React Frontend
    ↓
Makes API calls to: https://linuxmacmini.tail42ac25.ts.net/api
    ↓
Tailscale Funnel (public HTTPS)
    ↓
Your Linux Mac Mini (local backend on port 8000)
```

## Why So Complicated?

**The Problem:** 
- NFSN shared hosting doesn't support long-running processes (like FastAPI)
- Mixed content errors: Can't make HTTP requests from HTTPS pages

**The Solution:**
- Frontend → NFSN (cheap static hosting)
- Backend → Local server + Tailscale Funnel (free HTTPS proxy)

## What You Need Running

### On Linux Mac Mini:
1. **Backend:** `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
2. **Tailscale Funnel:** `sudo tailscale funnel --bg 8000`

Both are currently running!

## To Deploy Updates

### Update Frontend:
```bash
cd /home/tom/lnx_mac_int_drv/dev/chron
./deploy-frontend-nfsn.sh
```
This will:
1. Build React app
2. Upload to NFSN
3. Takes ~2 minutes

### Update Backend:
Just restart it on the Linux Mac Mini:
```bash
cd /home/tom/lnx_mac_int_drv/dev/chron
# Stop old process if needed
pkill -f "uvicorn backend.main:app"
# Start new one
backend/.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
```

## Current Status

✅ **Frontend:** Deployed and live
✅ **Backend:** Running locally with Tailscale Funnel
✅ **Database:** SQLite on Linux Mac Mini
✅ **Voice Transcription:** Working (Whisper on local server)
✅ **Visual Timeline:** Working
✅ **Public Access:** Anyone can use it at http://ritualstack.io

## Important Notes

1. **HTTP vs HTTPS:** 
   - Frontend is HTTP only (NFSN hasn't provisioned SSL yet)
   - Backend is HTTPS (via Tailscale Funnel)
   - This actually works fine now!

2. **Tailscale Funnel:**
   - Is PUBLICLY accessible (not just Tailscale network)
   - Provides free HTTPS
   - Running in background on Linux Mac Mini

3. **If Backend Goes Down:**
   - Frontend still loads
   - Shows error: "Unable to fetch events"
   - Just restart backend + funnel on Linux Mac Mini

## Simplification Options (For Later)

If you want to simplify:

**Option A:** Deploy backend to Railway.app or Render.com (free tier)
- Backend runs on cloud
- No need to keep local machine running
- Update `VITE_API_URL` in `.env.production`

**Option B:** Upgrade NFSN to daemon site (~$0.02/day)
- Everything on NFSN
- No local dependencies

**Option C:** Keep current setup
- It works!
- Free (except NFSN storage)
- Just requires local machine to be on

## Quick Reference

- **Frontend URL:** http://chronicle.ritualstack.io
- **Backend URL:** https://linuxmacmini.tail42ac25.ts.net/
- **Deployment Script:** `./deploy-frontend-nfsn.sh`
- **Check Backend:** `curl https://linuxmacmini.tail42ac25.ts.net/events/`
- **Check Funnel:** `tailscale funnel status`

## The Bottom Line

You now have Chronicle running in production! It's accessible to anyone at:
- http://ritualstack.io
- http://chronicle.ritualstack.io

The setup is a bit complex because we're mixing:
- Static hosting (NFSN)
- Local backend (Linux Mac Mini)  
- Public HTTPS proxy (Tailscale Funnel)

But it's FREE and it WORKS! 🎉
