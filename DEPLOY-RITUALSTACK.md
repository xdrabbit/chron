# Chronicle Deployment Guide for ritualstack.io
**User:** xdrabbit_ritualstack  
**Domain:** chronicle.ritualstack.io  
**Date:** October 13, 2025

---

## 🚀 Quick Deploy (Automated)

### Option 1: Use the Deploy Script

```bash
cd /home/tom/lnx_mac_int_drv/dev/chron

# Run the automated deployment
./deploy.sh

# Follow the prompts - it will:
# ✅ Build the frontend
# ✅ Package everything
# ✅ Upload to ritualstack.io
# ✅ Extract and set up backend
```

---

## 📋 Manual Deployment (Step-by-Step)

If you prefer to do it manually or the script has issues:

### Step 1: Build Frontend Locally

```bash
cd /home/tom/lnx_mac_int_drv/dev/chron/frontend
npm install
npm run build
# Creates dist/ folder with production-ready files
```

### Step 2: Package for Deployment

```bash
cd /home/tom/lnx_mac_int_drv/dev/chron
tar -czf chronicle-deploy.tar.gz \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='.venv' \
  --exclude='.git' \
  frontend/dist \
  backend \
  nginx-chronicle.conf \
  chronicle.service
```

### Step 3: Upload to Server

```bash
scp chronicle-deploy.tar.gz xdrabbit_ritualstack@ritualstack.io:/tmp/
```

### Step 4: SSH into Server and Extract

```bash
ssh xdrabbit_ritualstack@ritualstack.io

# Create directory and extract
sudo mkdir -p /var/www/chronicle
cd /var/www/chronicle
sudo tar -xzf /tmp/chronicle-deploy.tar.gz
sudo chown -R xdrabbit_ritualstack:www-data /var/www/chronicle
```

### Step 5: Set Up Backend

```bash
cd /var/www/chronicle/backend

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Test backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001
# Press Ctrl+C to stop after testing
```

### Step 6: Install SystemD Service

```bash
# Copy service file
sudo cp /var/www/chronicle/chronicle.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable chronicle
sudo systemctl start chronicle

# Check status
sudo systemctl status chronicle

# View logs
sudo journalctl -u chronicle -f
```

### Step 7: Configure Nginx

```bash
# Copy Nginx config
sudo cp /var/www/chronicle/nginx-chronicle.conf /etc/nginx/sites-available/chronicle

# Enable site
sudo ln -s /etc/nginx/sites-available/chronicle /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

### Step 8: Set Up DNS

Before SSL will work, you need to point the subdomain to your server:

1. Go to your domain registrar (where you bought ritualstack.io)
2. Add an A record:
   - **Name/Host:** chronicle
   - **Type:** A
   - **Value:** [Your server IP address]
   - **TTL:** 3600 (or automatic)

Wait 5-30 minutes for DNS to propagate, then test:
```bash
nslookup chronicle.ritualstack.io
```

### Step 9: Install SSL Certificate (Let's Encrypt)

```bash
# Install certbot if not already installed
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d chronicle.ritualstack.io

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose redirect HTTP to HTTPS (recommended: Yes)

# Certbot will automatically:
# ✅ Get SSL certificate
# ✅ Update Nginx config
# ✅ Set up auto-renewal
```

### Step 10: Test Everything

```bash
# Check backend is running
curl http://localhost:8001/docs

# Check frontend serves
curl http://localhost/

# Check from outside
curl https://chronicle.ritualstack.io/

# Test API
curl https://chronicle.ritualstack.io/api/events/

# Test Whisper
curl -X POST https://chronicle.ritualstack.io/api/transcribe/test
```

---

## 🔧 Useful Commands

### Managing the Backend Service

```bash
# Start
sudo systemctl start chronicle

# Stop
sudo systemctl stop chronicle

# Restart
sudo systemctl restart chronicle

# View status
sudo systemctl status chronicle

# View logs (live)
sudo journalctl -u chronicle -f

# View recent logs
sudo journalctl -u chronicle -n 100
```

### Managing Nginx

```bash
# Test config
sudo nginx -t

# Reload (without downtime)
sudo systemctl reload nginx

# Restart
sudo systemctl restart nginx

# View logs
sudo tail -f /var/log/nginx/chronicle-access.log
sudo tail -f /var/log/nginx/chronicle-error.log
```

### Updating the App

```bash
# Build new version locally
cd /home/tom/lnx_mac_int_drv/dev/chron/frontend
npm run build

# Package and upload
cd ..
tar -czf chronicle-update.tar.gz frontend/dist backend
scp chronicle-update.tar.gz xdrabbit_ritualstack@ritualstack.io:/tmp/

# On server
ssh xdrabbit_ritualstack@ritualstack.io
cd /var/www/chronicle
sudo tar -xzf /tmp/chronicle-update.tar.gz
sudo systemctl restart chronicle
```

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
sudo journalctl -u chronicle -n 50

# Common issues:
# - Missing Python packages: cd backend && source .venv/bin/activate && pip install -r requirements.txt
# - Port already in use: sudo netstat -tlnp | grep 8001
# - Permission issues: sudo chown -R xdrabbit_ritualstack:www-data /var/www/chronicle
```

### Frontend shows 404

```bash
# Check Nginx config
sudo nginx -t

# Check file permissions
ls -la /var/www/chronicle/frontend/dist/

# Should see index.html and assets/
```

### API requests fail

```bash
# Check backend is running
curl http://localhost:8001/docs

# Check Nginx proxy
sudo tail -f /var/log/nginx/chronicle-error.log

# Check firewall
sudo ufw status
sudo ufw allow 80
sudo ufw allow 443
```

### SSL certificate issues

```bash
# Renew manually
sudo certbot renew

# Check auto-renewal timer
sudo systemctl status certbot.timer
```

---

## 📊 Server Requirements

### Minimum:
- **CPU:** 1 core
- **RAM:** 512 MB (1 GB recommended for Whisper)
- **Disk:** 2 GB
- **OS:** Ubuntu 20.04+ / Debian 10+

### Software:
- Python 3.8+
- Nginx
- Certbot
- Git (optional)

---

## 🎉 Success Checklist

- [ ] Backend running: `sudo systemctl status chronicle` shows "active (running)"
- [ ] Nginx serving: `https://chronicle.ritualstack.io` loads the app
- [ ] API working: `https://chronicle.ritualstack.io/api/docs` shows FastAPI docs
- [ ] SSL active: Browser shows padlock icon
- [ ] Can create events
- [ ] Can upload/transcribe audio
- [ ] Timeline visualization displays events

---

## 📞 Need Help?

Check these in order:
1. Backend logs: `sudo journalctl -u chronicle -f`
2. Nginx error log: `sudo tail -f /var/log/nginx/chronicle-error.log`
3. Browser console (F12) for frontend errors
4. Test backend directly: `curl http://localhost:8001/docs`

**Your specific setup:**
- SSH: `ssh xdrabbit_ritualstack@ritualstack.io`
- Backend path: `/var/www/chronicle/backend`
- Frontend path: `/var/www/chronicle/frontend/dist`
- Service: `chronicle.service`
- Logs: `sudo journalctl -u chronicle -f`
