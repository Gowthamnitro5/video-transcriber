#!/usr/bin/env bash
# Render start script

echo "Starting Video Transcriber..."
gunicorn -w 2 -b 0.0.0.0:$PORT app:app