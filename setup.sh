#!/bin/bash

echo "=========================================="
echo "Video Transcriber Setup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "  Version: $PYTHON_VERSION"

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo ""
    echo "❌ FFmpeg is not installed."
    echo ""
    echo "Please install FFmpeg:"
    echo "  macOS:    brew install ffmpeg"
    echo "  Ubuntu:   sudo apt install ffmpeg"
    echo "  Windows:  Download from https://ffmpeg.org/download.html"
    exit 1
fi

echo "✓ FFmpeg found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "  Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip -q

# Install requirements
echo ""
echo "Installing Python packages..."
echo "  (This may take a few minutes...)"
pip install -r requirements.txt -q

echo "✓ All packages installed"

# Create uploads directory
echo ""
echo "Setting up directories..."
mkdir -p uploads
echo "✓ Uploads directory ready"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     python app.py"
echo ""
echo "  3. Open your browser and go to:"
echo "     http://localhost:5000"
echo ""
echo "Note: The first run will download the Whisper model (~150MB)"
echo "=========================================="