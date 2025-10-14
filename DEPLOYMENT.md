# Chronicle Deployment Guide

## 🎯 Deployment Overview

Chronicle consists of:
- **Frontend**: React app (static files after build)
- **Backend**: FastAPI Python server (needs to run continuously)
- **Database**: SQLite file (stored on server)

## 📦 Option 1: Build and Deploy (Recommended)

### **Step 1: Build the Frontend**

```bash
cd /home/tom/lnx_mac_int_drv/dev/chron/frontend
npm run build
```

This creates a `dist/` folder with optimized static files (HTML, CSS, JS).

### **Step 2: Prepare Backend for Production**

Update backend to serve both API and frontend:

```bash
cd /home/tom/lnx_mac_int_drv/dev/chron/backend
pip install -r requirements.txt
```

### **Step 3: Deploy to ritualstack.io**

#### **Option A: Subdomain (chronicle.ritualstack.io)**

1. **Upload files to server:**
```bash
# From your local machine
rsync -avz --progress \
  /home/tom/lnx_mac_int_drv/dev/chron/ \
  user@ritualstack.io:/var/www/chronicle/
```

2. **On the server, set up the backend:**
```bash
ssh user@ritualstack.io

# Navigate to chronicle directory
cd /var/www/chronicle/backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create systemd service to keep backend running
sudo nano /etc/systemd/system/chronicle.service
```

3. **Create systemd service file:**
```ini
[Unit]
Description=Chronicle Timeline Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/chronicle/backend
Environment="PATH=/var/www/chronicle/backend/.venv/bin"
ExecStart=/var/www/chronicle/backend/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8001

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. **Start the service:**
```bash
sudo systemctl enable chronicle
sudo systemctl start chronicle
sudo systemctl status chronicle
```

5. **Configure Nginx (if using):**
```nginx
server {
    listen 80;
    server_name chronicle.ritualstack.io;

    # Serve frontend static files
    location / {
        root /var/www/chronicle/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://localhost:8001/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /docs {
        proxy_pass http://localhost:8001/docs;
    }

    location /transcribe/ {
        proxy_pass http://localhost:8001/transcribe/;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

6. **SSL with Let's Encrypt:**
```bash
sudo certbot --nginx -d chronicle.ritualstack.io
```

#### **Option B: Path-based (ritualstack.io/chronicle)**

If you want it at a path instead of subdomain:

```nginx
location /chronicle/ {
    alias /var/www/chronicle/frontend/dist/;
    try_files $uri $uri/ /chronicle/index.html;
}

location /chronicle/api/ {
    proxy_pass http://localhost:8001/;
}
```

## 📦 Option 2: Docker Deployment (Advanced)

I can create Docker files if you prefer containerized deployment.

## 🔧 Quick Deploy Script

Want me to create an automated deployment script that:
1. Builds the frontend
2. Packages everything
3. Uploads to your server
4. Sets up services automatically

## 🎯 What You Need on ritualstack.io

1. **SSH access**
2. **Python 3.8+** installed
3. **Node.js** (only if building on server)
4. **Nginx or Apache** (for serving files)
5. **Systemd** (to keep backend running)

## 📝 Environment Variables

Update API URLs in frontend before building:

```javascript
// frontend/src/services/api.js
const BASE_URL = 'https://chronicle.ritualstack.io/api';
// OR
const BASE_URL = 'https://ritualstack.io/chronicle/api';
```

---

## 🚀 Quick Start Commands

```bash
# 1. Build frontend
cd frontend && npm run build

# 2. Test backend locally
cd backend && source .venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8001

# 3. Package for deployment
cd .. && tar -czf chronicle-deploy.tar.gz frontend/dist backend

# 4. Upload to server
scp chronicle-deploy.tar.gz user@ritualstack.io:/var/www/

# 5. Extract and configure on server
ssh user@ritualstack.io
cd /var/www && tar -xzf chronicle-deploy.tar.gz
```

---

## ❓ What's your preference?

1. **Simple manual setup** (follow steps above)
2. **Automated deploy script** (I'll create it)
3. **Docker deployment** (cleanest but more setup)
4. **Guide me through your specific server setup**
