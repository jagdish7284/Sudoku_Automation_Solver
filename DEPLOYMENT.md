# Deployment Guide

Production deployment strategies for Sudoku Automation System. Choose the platform that best fits your needs.

---

## Table of Contents

1. [Backend Deployment](#backend-deployment)
2. [Frontend Deployment](#frontend-deployment)
3. [Full-Stack Integration](#full-stack-integration)
4. [Domain & SSL Setup](#domain--ssl-setup)
5. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Backend Deployment

### Option 1: Railway.app (Recommended - Easiest) ⭐

**Why Railway?** Simple Git integration, automatic deployments, great free tier.

#### Setup Steps:

1. **Create Railway Account**
   - Visit [railway.app](https://railway.app)
   - Sign in with GitHub

2. **Connect Repository**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize and select your repository

3. **Configure Environment**
   - Add environment variables from `.env.example`
   - Set `PORT` environment variable (if needed)

4. **Set Start Command**
   - In settings, set "Start Command":
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

5. **Deploy**
   - Push to `main` branch
   - Railway automatically deploys
   - Your API is live! 🎉

**URL Pattern**: `https://your-project.up.railway.app`

**Pricing**: Free tier available, pay-as-you-go after

---

### Option 2: Heroku (Classic - Legacy)

#### Setup:

```bash
# Install Heroku CLI
# Visit: https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create app
heroku create sudoku-automation

# Add buildpack
heroku buildpacks:add heroku/python

# Set environment variables
heroku config:set DEBUG=false
heroku config:set LOG_LEVEL=INFO

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

**URL Pattern**: `https://sudoku-automation.herokuapp.com`

**Note**: Heroku free tier discontinued (use Railway instead)

---

### Option 3: AWS EC2 (Professional)

#### Instance Setup:

```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.10 python3-pip python3-venv nginx supervisor

# Clone repository
git clone https://github.com/yourusername/sudoku-automation.git
cd sudoku-automation/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Install Gunicorn (production server)
pip install gunicorn
```

#### Configure Gunicorn:

Create `/etc/systemd/system/sudoku-automation.service`:

```ini
[Unit]
Description=Sudoku Automation API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/sudoku-automation/backend
Environment="PATH=/home/ubuntu/sudoku-automation/backend/venv/bin"
ExecStart=/home/ubuntu/sudoku-automation/backend/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    main:app

[Install]
WantedBy=multi-user.target
```

#### Configure Nginx:

Create `/etc/nginx/sites-available/sudoku-automation`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/ubuntu/sudoku-automation/frontend;
    }
}
```

#### Start Services:

```bash
# Enable and start Sudoku service
sudo systemctl daemon-reload
sudo systemctl enable sudoku-automation
sudo systemctl start sudoku-automation

# Enable and restart Nginx
sudo systemctl enable nginx
sudo systemctl restart nginx

# Set up SSL with Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

**Benefits**: Full control, scalable, professional

---

### Option 4: DigitalOcean (Balanced)

Similar to AWS, with simplified interface:

```bash
# Create droplet with Python preset
# SSH in and follow AWS EC2 steps above

# DigitalOcean App Platform (easiest):
# 1. Connect GitHub repo
# 2. Specify Python 3.10 runtime
# 3. Set start command
# 4. Deploy!
```

---

### Option 5: Google Cloud Run (Serverless)

#### Create `Dockerfile`:

```dockerfile
FROM python:3.10

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### Deploy:

```bash
gcloud run deploy sudoku-automation \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

**Benefits**: Serverless, automatic scaling, pay-per-use

---

## Frontend Deployment

### Option 1: Vercel (Recommended) ⭐

**Why Vercel?** Optimized for web, automatic deployments, fast CDN.

#### Setup:

1. **Create Vercel Account**
   - Visit [vercel.com](https://vercel.com)
   - Sign up with GitHub

2. **Import Project**
   - Click "Import Project"
   - Select your GitHub repository
   - Configure:
     - **Project Name**: sudoku-automation
     - **Framework Preset**: Other
     - **Root Directory**: `frontend`

3. **Deploy**
   - Click "Deploy"
   - Your site is live! 🚀

4. **Configure API URL**
   - Environment Variables tab
   - Add: `REACT_APP_API_URL=https://your-backend.up.railway.app`

**URL Pattern**: `https://sudoku-automation.vercel.app`

**Pricing**: Free tier available, $20/mo for unlimited

---

### Option 2: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy frontend
cd frontend
netlify deploy --prod --dir .
```

Or drag & drop `frontend/` folder on netlify.com

**URL Pattern**: `https://sudoku-automation.netlify.app`

---

### Option 3: GitHub Pages

#### Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Frontend

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./frontend
```

**URL Pattern**: `https://yourusername.github.io/sudoku-automation`

**Limitations**: Static sites only, slower CDN

---

## Full-Stack Integration

### Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────────────────┐
│  Vercel (Frontend)              │
│  - Next.js / Static files       │
│  - Automatic deployments        │
│  - CDN globally distributed     │
└──────────┬──────────────────────┘
           │ API calls
           ▼ (HTTPS)
┌─────────────────────────────────┐
│  Railway/Heroku (Backend)       │
│  - FastAPI application          │
│  - Python environment           │
│  - Auto-scaling                 │
└─────────────────────────────────┘
```

### Backend-Frontend Communication

**Update frontend config** to point to backend:

In `frontend/script.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 
    'https://sudoku-automation.up.railway.app';

async function solvePuzzle(board) {
    const response = await fetch(`${API_BASE_URL}/api/solve/manual`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ board })
    });
    return response.json();
}
```

Set environment variable on Vercel:
```
REACT_APP_API_URL = https://sudoku-automation.up.railway.app
```

---

## Domain & SSL Setup

### Custom Domain on Vercel

1. Go to Project Settings
2. Domains section
3. Add your domain (e.g., `sudoku.yourdomain.com`)
4. Configure DNS:
   - Point to Vercel nameservers
   - Or add CNAME record pointing to Vercel

### SSL Certificate (Automatic)

- Vercel: Automatic with Let's Encrypt ✅
- Netlify: Automatic with Let's Encrypt ✅
- AWS EC2: Use Certbot (shown above) ✅
- Railway: Automatic HTTPS ✅

### Environment Variables for Production

**Backend (.env on Railway/Heroku)**:
```env
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=["https://sudoku-automation.vercel.app", "https://sudoku.yourdomain.com"]
MAX_IMAGE_SIZE_MB=5
CONFIDENCE_THRESHOLD=0.75
```

**Frontend (Vercel Environment Variables)**:
```
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_ENVIRONMENT=production
```

---

## Monitoring & Maintenance

### Logging

#### Backend Logs:

```bash
# Railway
railway logs

# Heroku
heroku logs --tail

# AWS EC2
sudo journalctl -u sudoku-automation -f

# Google Cloud Run
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sudoku-automation" --limit 50
```

#### Frontend Logs:

```bash
# Vercel
vercel logs

# Netlify
netlify logs:functions
```

### Error Tracking (Optional)

Add Sentry for error monitoring:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    integrations=[FastApiIntegration()],
    environment="production"
)
```

### Performance Monitoring

Add metrics collection:

```bash
# Backend: Add prometheus metrics
pip install prometheus-client

# Frontend: Monitor with Vercel Analytics
# (Automatic on Vercel)
```

### Uptime Monitoring

Use free services:
- [UptimeRobot](https://uptimerobot.com)
- [Pingdom](https://www.pingdom.com)
- [Better Uptime](https://betterstack.com/better-uptime)

Set up alerts for downtime.

---

## Deployment Checklist

### Before Production
- [ ] All tests passing
- [ ] No console errors in browser
- [ ] Backend API responds correctly
- [ ] Environment variables secured
- [ ] CORS properly configured
- [ ] SSL certificate active
- [ ] Database backups configured
- [ ] Error logging enabled

### After Deployment
- [ ] Verify website is accessible
- [ ] Test manual solving feature
- [ ] Test image upload feature
- [ ] Check execution times
- [ ] Verify error messages display
- [ ] Test on mobile browser
- [ ] Check backend logs for errors
- [ ] Monitor initial traffic

### Ongoing
- [ ] Daily log reviews
- [ ] Weekly performance checks
- [ ] Monthly backup verification
- [ ] Quarterly dependency updates
- [ ] Security patches when available

---

## Recommended Deployment Stack

For best results with minimal cost:

```
Frontend:  Vercel (free tier + $20/mo)
Backend:   Railway (free tier + pay-as-you-go)
Domain:    Namecheap (~$1-5/year)
Monitoring: UptimeRobot (free tier)
Analytics: Vercel Analytics (included)
```

**Total Monthly Cost**: $20 + Railway usage (typically $5-15)

---

## Scaling Considerations

### Backend Scaling

As traffic grows:
1. Railway: Auto-scales with requests
2. AWS: Add more EC2 instances behind load balancer
3. Google Cloud Run: Serverless auto-scaling

### Frontend Scaling

Vercel/Netlify handle automatically with CDN.

### Database (Future)

When adding database:
- Use managed services (Railway PostgreSQL, AWS RDS)
- Enable automatic backups
- Set up read replicas for scale

### Image Processing

For high traffic:
- Add caching for common images
- Use Lambda/Cloud Functions for processing
- Implement request queuing

---

**Last Updated**: April 4, 2026
**Status**: Production Ready ✅
