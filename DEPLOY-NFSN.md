# Chronicle Deployment on NearlyFreeSpeech.net (NFSN)

**Server:** ssh.nyc1.nearlyfreespeech.net  
**User:** xdrabbit_ritualstack  
**Domain:** chronicle.ritualstack.io

---

## 🎯 NearlyFreeSpeech.net Setup Process

### Step 1: Create chronicle.ritualstack.io Subdomain

**Option A: Add Alias to Existing Site**
1. Log into https://members.nearlyfreespeech.net/
2. Go to **Domains** → **ritualstack.io**
3. Click **"Add an Alias"**
4. Enter: `chronicle.ritualstack.io`
5. Click **"Add Alias"**

**Option B: Create Dedicated Site (Recommended)**
1. Log into https://members.nearlyfreespeech.net/
2. Go to **Sites** → **"Create a New Site"**
3. Fill in:
   - **Short Name:** `chronicle` (internal name)
   - **Domain:** `chronicle.ritualstack.io`
   - **Server:** NYC1 (or your preferred location)
4. Click **"Create Site"**
5. NFSN will provision the site (takes a few minutes)

---

## 📋 NFSN Directory Structure

NearlyFreeSpeech.net sites have a specific structure:
```
/home/
├── protected/     # Backend, database, scripts (not web-accessible)
├── public/        # Frontend static files (web root)
└── logs/          # Server logs
```

---

## 🚀 Deployment Method for NFSN

### Important Notes:
- ⚠️ **NFSN doesn't support systemd or long-running processes by default**
- ⚠️ **FastAPI backend needs to run as CGI or use Daemon Site**
- ✅ **Frontend works perfectly** (just static files)

### Option 1: Static Frontend + Separate Backend (Recommended)

Since NFSN doesn't easily support long-running Python processes, best approach:

1. **Deploy Frontend to NFSN** (static files)
2. **Run Backend elsewhere** (keep on your local server at 192.168.0.15:8000)
3. **Enable CORS on backend** to allow chronicle.ritualstack.io

### Option 2: Daemon Site (Costs Extra)

NFSN offers "Daemon Sites" that can run long-running processes:
- Cost: ~$0.02/day + bandwidth
- Allows running FastAPI backend continuously
- See: https://members.nearlyfreespeech.net/support/daemon

---

## 🎯 Deployment Instructions

### Deploy Frontend Only (Easiest)

#### 1. Build Frontend Locally

```bash
cd /home/tom/lnx_mac_int_drv/dev/chron/frontend
npm run build
```

#### 2. Update API URL for Remote Backend

Edit `frontend/.env.production`:
```env
# Point to your local server or another hosting
VITE_API_URL=http://192.168.0.15:8000
# OR use Daemon site: https://chronicle-api.ritualstack.io
```

#### 3. Rebuild with New API URL

```bash
npm run build
```

#### 4. Upload to NFSN

```bash
# Package frontend
cd /home/tom/lnx_mac_int_drv/dev/chron
tar -czf chronicle-frontend.tar.gz frontend/dist

# Upload to NFSN
scp chronicle-frontend.tar.gz xdrabbit_ritualstack@ssh.nyc1.nearlyfreespeech.net:/home/tmp/

# SSH to server
ssh xdrabbit_ritualstack@ssh.nyc1.nearlyfreespeech.net

# Extract to public directory
cd /home/public
tar -xzf /home/tmp/chronicle-frontend.tar.gz --strip-components=2
# This extracts frontend/dist/* directly to /home/public

# Set permissions
chmod -R 755 /home/public
```

#### 5. Test

Visit: https://chronicle.ritualstack.io

---

## 🔧 Backend Options

### Option A: Keep Backend on Local Server

**Pros:** 
- Free, simple, works immediately
- No additional NFSN costs

**Cons:** 
- Needs port forwarding or VPN
- Local server must stay online

**Setup:**
1. Keep backend running on 192.168.0.15:8000
2. Set up port forwarding on your router:
   - External Port: 8000
   - Internal IP: 192.168.0.15
   - Internal Port: 8000
3. Get dynamic DNS (e.g., from No-IP, DuckDNS)
4. Update frontend API URL to your dynamic DNS

### Option B: Deploy Backend to NFSN Daemon Site

**Setup:**
1. Create daemon site in NFSN panel:
   - Go to **Sites** → **"Create a New Site"**
   - Choose **"Daemon"** type
   - Name: `chronicle-api`
   - Domain: `chronicle-api.ritualstack.io`

2. Upload backend:
```bash
# Package backend
tar -czf chronicle-backend.tar.gz backend

# Upload
scp chronicle-backend.tar.gz xdrabbit_ritualstack@ssh.nyc1.nearlyfreespeech.net:/home/protected/

# SSH and extract
ssh xdrabbit_ritualstack@ssh.nyc1.nearlyfreespeech.net
cd /home/protected
tar -xzf chronicle-backend.tar.gz

# Set up Python environment
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Create daemon control script:
```bash
nano /home/protected/run-daemon
```

Add:
```bash
#!/bin/sh
cd /home/protected/backend
source .venv/bin/activate
exec python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

```bash
chmod +x /home/protected/run-daemon
```

4. Start via NFSN panel:
   - Go to your daemon site
   - Click **"Actions"** → **"Start Daemon"**

5. Update frontend to use daemon API:
```env
VITE_API_URL=https://chronicle-api.ritualstack.io
```

### Option C: Use Free Backend Hosting

Deploy backend to:
- **Railway.app** (Free tier available)
- **Render.com** (Free tier)
- **Fly.io** (Free allowance)
- **PythonAnywhere** (Free tier)

Then point frontend to that URL.

---

## 📝 Quick Deploy Script for NFSN Frontend

```bash
#!/bin/bash
# Deploy frontend only to NFSN

cd /home/tom/lnx_mac_int_drv/dev/chron/frontend

echo "Building frontend..."
npm run build

echo "Packaging..."
cd ..
tar -czf chronicle-frontend.tar.gz frontend/dist

echo "Uploading to NFSN..."
scp chronicle-frontend.tar.gz xdrabbit_ritualstack@ssh.nyc1.nearlyfreespeech.net:/home/tmp/

echo "Extracting on server..."
ssh xdrabbit_ritualstack@ssh.nyc1.nearlyfreespeech.net << 'EOF'
  cd /home/public
  rm -rf *  # Be careful! This clears the public directory
  tar -xzf /home/tmp/chronicle-frontend.tar.gz --strip-components=2
  chmod -R 755 /home/public
  rm /home/tmp/chronicle-frontend.tar.gz
  echo "Deployment complete!"
EOF

echo "Visit: https://chronicle.ritualstack.io"
```

---

## 🔐 NFSN-Specific Notes

### SSH Keys
Add your SSH key for easier access:
```bash
# Generate if you don't have one
ssh-keygen -t ed25519

# Copy to NFSN
ssh-copy-id xdrabbit_ritualstack@ssh.nyc1.nearlyfreespeech.net
```

### File Permissions
- Public files: `chmod 755` (directories), `chmod 644` (files)
- Protected files: `chmod 700` (directories), `chmod 600` (files)

### SSL/HTTPS
- NFSN provides free SSL automatically
- Just use https:// URLs
- No certbot needed!

### .htaccess for React Router
Create `/home/public/.htaccess`:
```apache
# React Router support
RewriteEngine On
RewriteBase /
RewriteRule ^index\.html$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]
```

---

## 💡 Recommended Setup

**For Chronicle on NFSN:**

1. **Frontend:** Deploy to chronicle.ritualstack.io (NFSN)
2. **Backend:** Use Railway.app free tier or keep on local server
3. **Database:** SQLite file on backend server

**This gives you:**
- ✅ Fast, reliable frontend hosting
- ✅ No daemon costs on NFSN
- ✅ Backend with full Python support
- ✅ Simple, maintainable setup

---

## 📞 NFSN Support

- FAQ: https://faq.nearlyfreespeech.net/
- Support: https://members.nearlyfreespeech.net/support/
- SSH Guide: https://faq.nearlyfreespeech.net/section/uploading/howssh

---

## ✅ Quick Start Checklist

- [ ] Create chronicle.ritualstack.io in NFSN panel
- [ ] Build frontend with production API URL
- [ ] Upload frontend to /home/public
- [ ] Set up .htaccess for routing
- [ ] Test https://chronicle.ritualstack.io
- [ ] Decide on backend hosting
- [ ] Configure CORS on backend
- [ ] Test full app functionality

**Need help deciding on backend hosting? Let me know!**
