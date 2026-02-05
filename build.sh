#!/usr/bin/env bash
# Render build script

echo "Installing FFmpeg..."
apt-get update && apt-get install -y ffmpeg

echo "FFmpeg installed successfully"
ffmpeg -version