# Production Deployment Configuration

## 🔧 Configure API URL Before Deployment

Before building for production, update the API URL in the frontend.

### Option 1: Environment Variables (Recommended)

Create `.env.production` in the frontend directory:

```bash
cd /home/tom/lnx_mac_int_drv/dev/chron/frontend
cat > .env.production << 'EOF'
VITE_API_URL=https://chronicle.ritualstack.io/api
# OR for path-based deployment:
# VITE_API_URL=https://ritualstack.io/chronicle/api
EOF
```

Then update `frontend/src/services/api.js`:

```javascript
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### Option 2: Direct Configuration

Edit `frontend/src/services/api.js` and change:

```javascript
// Development
const BASE_URL = 'http://192.168.0.15:8000';

// Production
const BASE_URL = 'https://chronicle.ritualstack.io/api';
```

## 🚀 Quick Deploy

```bash
# 1. Configure API URL (choose one method above)

# 2. Run deployment script
cd /home/tom/lnx_mac_int_drv/dev/chron
./deploy.sh

# 3. Follow prompts
# - Confirm server details
# - Script will build, package, and upload

# 4. On server, configure Nginx (see DEPLOYMENT.md)

# 5. Set up SSL
sudo certbot --nginx -d chronicle.ritualstack.io
```

## 📝 Server Requirements

- **Python 3.8+**
- **Nginx or Apache**
- **SSL certificate** (Let's Encrypt)
- **SSH access**
- **Root or sudo privileges** (for systemd service)

## 🔍 Testing After Deployment

1. Check backend: `https://chronicle.ritualstack.io/api/docs`
2. Check frontend: `https://chronicle.ritualstack.io/`
3. Test voice transcription: `/transcribe/test`
4. Check logs: `journalctl -u chronicle -f`

## 🐛 Troubleshooting

**Backend not starting:**
```bash
ssh user@ritualstack.io
sudo journalctl -u chronicle -n 50
```

**Frontend 404 errors:**
- Check Nginx config: `/etc/nginx/sites-available/chronicle`
- Test config: `sudo nginx -t`
- Reload: `sudo systemctl reload nginx`

**API Connection Failed:**
- Verify CORS settings in backend
- Check firewall: `sudo ufw status`
- Verify backend port: `sudo netstat -tlnp | grep 8001`

## 📦 File Structure on Server

```
/var/www/chronicle/
├── frontend/
│   └── dist/           # Built static files
├── backend/
│   ├── main.py
│   ├── .venv/          # Python virtual environment
│   ├── requirements.txt
│   └── chronicle.db    # SQLite database
└── chronicle-YYYYMMDD_HHMMSS.tar.gz  # Deployment packages
```

## 🔐 Security Checklist

- [ ] SSL certificate installed
- [ ] Firewall configured (allow 80, 443)
- [ ] Database file permissions set correctly
- [ ] API keys/secrets in environment variables
- [ ] Disable debug mode in production
- [ ] Regular backups of chronicle.db
