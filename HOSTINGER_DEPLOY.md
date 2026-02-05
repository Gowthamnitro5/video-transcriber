# Hostinger VPS Deployment Guide

## Your VPS Specs Are Perfect!

- 1 CPU Core
- 4GB RAM (Plenty for Whisper!)
- 50GB NVMe SSD
- 4TB Bandwidth

## Quick Deploy Steps

### Step 1: SSH into VPS
```bash
ssh root@YOUR_VPS_IP
```

### Step 2: Install Docker
```bash
apt update && apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker && systemctl enable docker
```

### Step 3: Clone and Deploy
```bash
git clone https://github.com/YOUR_USERNAME/video-transcriber.git
cd video-transcriber
docker build -t video-transcriber .
docker run -d --name video-transcriber -p 80:5000 -v $(pwd)/uploads:/app/uploads --restart always video-transcriber
```

### Step 4: Access
```
http://YOUR_VPS_IP
```

## Model Options (4GB RAM)

With 4GB RAM, you can use:
- base model (~150MB) - Recommended
- small model (~466MB) - Better accuracy
- medium model (~1.5GB) - High accuracy

Edit app.py line 29 to change model.

## Useful Commands

```bash
# View logs
docker logs -f video-transcriber

# Restart
docker restart video-transcriber

# Update
docker stop video-transcriber && docker rm video-transcriber
docker build -t video-transcriber .
docker run -d --name video-transcriber -p 80:5000 -v $(pwd)/uploads:/app/uploads --restart always video-transcriber
```