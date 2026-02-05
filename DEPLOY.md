# Deployment Guide

## Option 1: Render (Recommended - FREE)

### Steps:

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

2. **Sign up on Render**: https://render.com

3. **Create New Web Service**
   - Connect your GitHub repo
   - Select "Python" environment
   - Build Command: `./build.sh`
   - Start Command: `./start.sh`
   - Instance Type: Free

4. **Add Environment Variables**:
   - `PYTHON_VERSION`: `3.9.0`
   - `FLASK_ENV`: `production`

5. **Deploy!** Render will automatically build and deploy.

**Note**: Free tier has 512MB RAM which is tight for Whisper. Use `tiny` model for better performance:
```python
# In app.py line 36
model = whisper.load_model("tiny")  # Instead of "base"
```

---

## Option 2: Railway (FREE)

1. Sign up: https://railway.app
2. Install Railway CLI:
```bash
npm install -g @railway/cli
```
3. Deploy:
```bash
railway login
railway init
railway up
```

---

## Option 3: Docker (Any VPS/Cloud)

### Local Docker:
```bash
docker build -t video-transcriber .
docker run -p 5000:5000 video-transcriber
```

### Deploy to DigitalOcean/Hetzner/AWS:

1. **Create a VPS** (2GB+ RAM recommended)

2. **SSH into server**:
```bash
ssh root@YOUR_SERVER_IP
```

3. **Install Docker**:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

4. **Clone and run**:
```bash
git clone YOUR_REPO_URL
cd video-transcriber
docker build -t video-transcriber .
docker run -d -p 80:5000 --restart always video-transcriber
```

5. **Access at**: `http://YOUR_SERVER_IP`

---

## Option 4: Heroku (NOT Recommended)

Heroku's free tier has limitations:
- 30-second build timeout (Whisper model download may fail)
- Slug size limit (model + ffmpeg may exceed 500MB)
- Requires buildpacks for FFmpeg

If you still want to try:
1. Add `heroku.yml` and `runtime.txt`
2. Use larger paid dyno

---

## Important Deployment Notes

### 1. Model Size Issues
Whisper models are large:
- `tiny`: ~39MB ✅ Good for free tiers
- `base`: ~150MB ⚠️ May cause issues on free tiers
- `small`+: Too large for most free tiers

Change model in `app.py`:
```python
model = whisper.load_model("tiny")  # For free deployment
```

### 2. Memory Requirements
- Minimum: 512MB RAM
- Recommended: 1GB+ RAM

### 3. Disk Space
Model is downloaded on first run (~150MB for base)

### 4. Timeout Issues
Large files may timeout on free tiers. Set in `app.py`:
```python
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB limit
```

### 5. Security for Production
Add to `app.py` before deployment:
```python
import secrets
app.secret_key = secrets.token_hex(32)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
```

---

## Quick Deployment Checklist

- [ ] Push code to GitHub
- [ ] Choose platform (Render recommended)
- [ ] Set Python version to 3.9
- [ ] Configure environment variables
- [ ] Change model to `tiny` if using free tier
- [ ] Set file upload limit (50MB for free tiers)
- [ ] Deploy and test

## Troubleshooting

**"Build timeout"**: Model download takes too long
- Use `tiny` model
- Or use Docker with pre-downloaded model

**"Memory exceeded"**: 
- Upgrade to paid tier
- Use `tiny` model
- Process shorter videos

**"No module named whisper"**:
- Add `openai-whisper` to requirements.txt (already done)

---

## Recommended: Render (FREE)

**Pros:**
- Free tier available
- Auto-deploys from GitHub
- Easy FFmpeg installation
- Persistent disk for uploads

**Cons:**
- 512MB RAM (use `tiny` model)
- Spins down after 15 min inactivity (30s cold start)

**URL after deploy**: `https://your-app-name.onrender.com`