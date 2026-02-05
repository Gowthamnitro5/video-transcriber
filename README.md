# Video to Document Transcriber

A beautiful, user-friendly web application that transcribes video and audio files into text documents using OpenAI's Whisper speech recognition model.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)

## Features

- **Upload Video or Audio**: Support for MP4, AVI, MOV, MKV, WEBM, MP3, WAV, M4A, OGG, FLAC
- **Automatic Transcription**: Powered by OpenAI Whisper (local processing)
- **Language Detection**: Auto-detects language or choose from 99+ supported languages
- **Translation**: Option to translate non-English audio to English
- **Multiple Export Formats**:
  - Text Document (.txt) - Formatted with timestamps
  - Subtitles (.srt) - For video captions
  - JSON Data (.json) - For programmatic use
- **Real-time Processing**: Visual progress indicator during transcription
- **Privacy-Focused**: All processing done locally, no data sent to external APIs
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **Backend**: Python, Flask, OpenAI Whisper, FFmpeg
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI Model**: OpenAI Whisper (base model by default)

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.8+**
2. **FFmpeg** (required for video processing)

### Installing FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## Installation

1. **Clone or download this repository:**
```bash
cd video-transcriber
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**Note:** The first run will download the Whisper model (approximately 150MB for the base model).

## Usage

1. **Start the application:**
```bash
python app.py
```

2. **Open your browser and navigate to:**
```
http://localhost:5000
```

3. **Upload a video or audio file** by dragging and dropping or clicking to browse

4. **Select options** (language, task)

5. **Click "Start Transcription"** and wait for processing

6. **Download** your transcription in your preferred format

## Project Structure

```
video-transcriber/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── uploads/              # Uploaded files and transcriptions
├── static/
│   ├── css/
│   │   └── style.css     # Application styles
│   └── js/
│       └── app.js        # Frontend JavaScript
└── templates/
    └── index.html        # Main HTML template
```

## Configuration

### Whisper Model Size

Edit `app.py` to change the Whisper model size:

```python
# Line ~33
model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
```

- **tiny**: Fastest, lowest accuracy (~39MB)
- **base**: Good balance (default) (~150MB)
- **small**: Better accuracy (~466MB)
- **medium**: High accuracy (~1.5GB)
- **large**: Best accuracy (~3GB)

### Maximum File Size

Edit `app.py` to change the maximum upload size:

```python
# Line ~12
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
```

## Supported Languages

Whisper supports 99 languages including:
- English, Chinese, German, Spanish, Russian
- Korean, French, Japanese, Portuguese
- Turkish, Polish, Catalan, Dutch
- Arabic, Swedish, Italian, Indonesian
- Hindi, Finnish, Vietnamese, Hebrew
- And many more...

## API Endpoints

- `GET /` - Main web interface
- `POST /transcribe` - Upload and transcribe file
- `GET /download/<filename>` - Download transcription file
- `GET /supported-languages` - Get list of supported languages

## Example API Usage

```bash
# Transcribe a file
curl -X POST http://localhost:5000/transcribe \
  -F "file=@video.mp4" \
  -F "language=auto" \
  -F "task=transcribe"
```

## Troubleshooting

### "FFmpeg not found" error
- Ensure FFmpeg is installed and in your system PATH
- Try running `ffmpeg -version` in your terminal

### "Out of memory" error
- Use a smaller Whisper model (tiny or base)
- Transcribe shorter video segments
- Close other applications to free up RAM

### Slow transcription
- Use the "base" or "tiny" model for faster processing
- Ensure your system has sufficient CPU/GPU resources
- Consider using GPU acceleration if available

### Large file uploads fail
- Check `MAX_CONTENT_LENGTH` in app.py
- Ensure sufficient disk space in the `uploads/` folder

## Performance Tips

1. **Use GPU (if available)**: Whisper automatically uses GPU if PyTorch with CUDA is installed
2. **Choose appropriate model**: Base model works well for most use cases
3. **Convert to audio first**: Audio files process faster than video files
4. **Batch processing**: For multiple files, consider modifying the backend

## Security Considerations

- Uploaded files are stored in the `uploads/` directory
- Files are not automatically deleted after transcription
- Implement file cleanup for production use
- Consider adding authentication for production deployments

## License

This project is open source and available under the MIT License.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [FFmpeg](https://ffmpeg.org/) - Video/audio processing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Made with ❤️ using OpenAI Whisper and Flask**