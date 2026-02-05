#!/usr/bin/env bash
# Build script for Render

set -e

echo "Installing FFmpeg..."
apt-get update -qq && apt-get install -y -qq ffmpeg > /dev/null 2>&1

echo "FFmpeg installed successfully"
ffmpeg -version | head -1