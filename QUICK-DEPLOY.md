# Chronicle Deployment Quick Reference

## 🎯 Current Status
- ✅ Frontend ready for deployment
- ✅ Backend running locally (192.168.0.15:8000)
- ⏳ Subdomain creation required (chronicle.ritualstack.io)
- ⏳ Backend hosting decision needed

## 📋 Step-by-Step Deployment

### 1. Create Subdomain on NFSN (Required First!)

Go to: https://members.nearlyfreespeech.net/

**Option A: Create as New Site**
1. Click **Sites** → **Create a New Site**
2. Short Name: `chronicle-ritualstack` (internal reference)
3. Domain: `chronicle.ritualstack.io`
4. Server: Choose any (doesn't matter for static sites)

**Option B: Add as Alias to Existing Site**
1. Click **Domains** → **Add a domain alias**
2. Domain: `chronicle.ritualstack.io`
3. Alias to: Your existing ritualstack.io site

### 2. Deploy Frontend (Frontend-Only Approach)

```bash
# Simple frontend deployment
./deploy-frontend-nfsn.sh
```

This will:
- Build the React frontend (`npm run build`)
- Upload to NFSN
- Extract to `/home/public`
- Create `.htaccess` for React Router
- Backup old files

**Result:** https://chronicle.ritualstack.io will be live!

### 3. Backend Options (Choose One)

#### Option A: Keep Backend Local (Simplest)
**Pros:** Free, no changes needed
**Cons:** Requires your local machine to be running

Your backend stays on `192.168.0.15:8000`. You need:
- Port forwarding on router (port 8000 → 192.168.0.15:8000)
- Dynamic DNS or static IP
- Update `frontend/.env.production`:
  ```
  VITE_API_URL=http://your-public-ip-or-domain:8000/api
  ```

#### Option B: NFSN Daemon Site
**Pros:** Everything in one place
**Cons:** Costs ~$0.02/day + bandwidth

1. In NFSN panel: Sites → Make site a "daemon site"
2. Deploy backend with full deploy.sh
3. Run FastAPI with:
   ```bash
   cd /home/protected
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

#### Option C: Free External Hosting (Recommended!)
**Pros:** Free, reliable, no local dependencies
**Cons:** Separate service to manage

**Railway.app** (Easiest):
1. Sign up at https://railway.app (free tier: 500 hours/month)
2. New Project → Deploy from GitHub repo
3. Set buildpack to Python
4. Environment variables: `DATABASE_URL`, etc.
5. Get your Railway URL: `https://chronicle-backend.railway.app`
6. Update `frontend/.env.production`:
   ```
   VITE_API_URL=https://chronicle-backend.railway.app/api
   ```

**Render.com**:
- Free tier with auto-sleep after 15 min inactivity
- Similar setup to Railway

**Fly.io**:
- Free tier includes 3 VMs
- More control, slightly more complex

## 🔧 Environment Configuration

Edit `frontend/.env.production` before deploying:

```bash
# If backend is on Railway:
VITE_API_URL=https://chronicle-backend.railway.app/api

# If backend stays local (with port forwarding):
VITE_API_URL=http://your-domain.com:8000/api

# If backend is on NFSN daemon site:
VITE_API_URL=https://chronicle.ritualstack.io/api
```

## 🚀 Quick Deploy Commands

```bash
# Build and test frontend locally
cd frontend
npm run build
npm run preview  # Test production build locally

# Deploy frontend to NFSN
cd ..
./deploy-frontend-nfsn.sh

# Connect via SSH to check
ssh xdrabbit_ritualstack@ssh.nyc1.nearlyfreespeech.net
ls -la /home/public
```

## 🌐 Testing Checklist

After deployment:

- [ ] Visit https://chronicle.ritualstack.io
- [ ] Check browser console for API errors
- [ ] Test adding an event
- [ ] Test voice transcription (if backend accessible)
- [ ] Test visual timeline zoom/pan
- [ ] Check mobile responsiveness

## 🔍 Troubleshooting

**Frontend shows but API fails:**
- Check `VITE_API_URL` in `.env.production`
- Verify backend is running and accessible
- Check CORS settings in backend (allow `chronicle.ritualstack.io`)

**404 errors on page refresh:**
- `.htaccess` file should be in `/home/public`
- Contains React Router rewrite rules (created automatically by script)

**Subdomain not working:**
- DNS takes 15-60 minutes to propagate
- Check NFSN panel that subdomain is active
- Try `dig chronicle.ritualstack.io` to verify DNS

**Backend connection errors:**
- If using local backend, verify port forwarding
- Test backend directly: `curl http://your-backend-url/api/health`
- Check firewall rules

## 💡 Recommended Path

**For immediate deployment:**
1. Create subdomain on NFSN (Step 1)
2. Deploy frontend with `./deploy-frontend-nfsn.sh` (Step 2)
3. Deploy backend to Railway.app (free, easy) (Step 3, Option C)
4. Update `.env.production` with Railway URL
5. Redeploy frontend with `./deploy-frontend-nfsn.sh`

**Total cost:** $0.00/month
**Total time:** ~20 minutes

## 📞 Support

- NFSN Docs: https://www.nearlyfreespeech.net/about/faq
- Railway Docs: https://docs.railway.app
- This project's guides: `DEPLOY-NFSN.md`, `DEPLOYMENT.md`
