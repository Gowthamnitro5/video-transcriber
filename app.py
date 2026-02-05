from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import whisper
import os
import tempfile
import ffmpeg
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'mp3', 'wav', 'm4a', 'ogg', 'flac'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load Whisper model (using base model for good balance)
# Options: tiny, base, small, medium, large
# With 4GB RAM on Hostinger VPS, we can use "base" or "small" model
print("Loading Whisper model...")
model = whisper.load_model("base")
print("Model loaded successfully!")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_audio(video_path, audio_path):
    """Extract audio from video file using ffmpeg"""
    try:
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, acodec='pcm_s16le', ac=1, ar=16000)
            .overwrite_output()
            .run(quiet=True)
        )
        return True
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return False

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def generate_srt(segments):
    """Generate SRT subtitle content from segments"""
    srt_content = []
    for i, segment in enumerate(segments, 1):
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        text = segment['text'].strip()
        srt_content.append(f"{i}")
        srt_content.append(f"{start} --> {end}")
        srt_content.append(f"{text}")
        srt_content.append("")
    return "\n".join(srt_content)

def generate_document(transcription_result, filename):
    """Generate a formatted document with transcription details"""
    doc_content = []
    doc_content.append("=" * 80)
    doc_content.append("VIDEO TRANSCRIPTION REPORT")
    doc_content.append("=" * 80)
    doc_content.append(f"")
    doc_content.append(f"Filename: {filename}")
    doc_content.append(f"Transcription Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc_content.append(f"Language: {transcription_result.get('language', 'auto-detected').upper()}")
    doc_content.append(f"")
    doc_content.append("=" * 80)
    doc_content.append("FULL TRANSCRIPTION")
    doc_content.append("=" * 80)
    doc_content.append(f"")
    doc_content.append(transcription_result.get('text', '').strip())
    doc_content.append(f"")
    doc_content.append("=" * 80)
    doc_content.append("TIMESTAMPED SEGMENTS")
    doc_content.append("=" * 80)
    doc_content.append(f"")
    
    for segment in transcription_result.get('segments', []):
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        text = segment['text'].strip()
        doc_content.append(f"[{start} - {end}]")
        doc_content.append(f"{text}")
        doc_content.append(f"")
    
    doc_content.append("=" * 80)
    doc_content.append("END OF TRANSCRIPTION")
    doc_content.append("=" * 80)
    
    return "\n".join(doc_content)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400
        
        # Get options
        language = request.form.get('language', None)
        if language == 'auto':
            language = None
        
        task = request.form.get('task', 'transcribe')  # 'transcribe' or 'translate'
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], base_name)
        file.save(file_path)
        
        # Determine if it's a video file
        file_ext = filename.rsplit('.', 1)[1].lower()
        is_video = file_ext in {'mp4', 'avi', 'mov', 'mkv', 'webm'}
        
        # Initialize audio_path
        audio_path = None
        
        # If video, extract audio first
        if is_video:
            audio_path = os.path.join(tempfile.gettempdir(), f"{timestamp}_audio.wav")
            if not extract_audio(file_path, audio_path):
                return jsonify({'error': 'Failed to extract audio from video'}), 500
            process_path = audio_path
        else:
            process_path = file_path
        
        # Transcribe with Whisper
        print(f"Transcribing: {filename}")
        
        options = {
            'task': task,
            'verbose': False
        }
        if language:
            options['language'] = language
        
        result = model.transcribe(process_path, **options)
        
        # Clean up temporary audio file if created
        if is_video and audio_path is not None and os.path.exists(audio_path):
            os.remove(audio_path)
        
        # Prepare response
        transcription_data = {
            'text': result['text'],
            'language': result.get('language', 'unknown'),
            'segments': [
                {
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'].strip()
                }
                for seg in result['segments']
            ],
            'duration': result['segments'][-1]['end'] if result['segments'] else 0
        }
        
        # Save transcription to file
        txt_filename = f"{timestamp}_transcription.txt"
        txt_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(generate_document(transcription_data, filename))
        
        # Save SRT file
        srt_filename = f"{timestamp}_subtitles.srt"
        srt_path = os.path.join(app.config['UPLOAD_FOLDER'], srt_filename)
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(generate_srt(transcription_data['segments']))
        
        # Save JSON file
        json_filename = f"{timestamp}_data.json"
        json_path = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(transcription_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'transcription': transcription_data,
            'files': {
                'document': txt_filename,
                'subtitles': srt_filename,
                'json': json_filename
            }
        })
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({'error': f'Transcription failed: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/supported-languages')
def get_supported_languages():
    """Return list of supported languages"""
    languages = {
        'auto': 'Auto-detect',
        'en': 'English',
        'zh': 'Chinese',
        'de': 'German',
        'es': 'Spanish',
        'ru': 'Russian',
        'ko': 'Korean',
        'fr': 'French',
        'ja': 'Japanese',
        'pt': 'Portuguese',
        'tr': 'Turkish',
        'pl': 'Polish',
        'ca': 'Catalan',
        'nl': 'Dutch',
        'ar': 'Arabic',
        'sv': 'Swedish',
        'it': 'Italian',
        'id': 'Indonesian',
        'hi': 'Hindi',
        'fi': 'Finnish',
        'vi': 'Vietnamese',
        'he': 'Hebrew',
        'uk': 'Ukrainian',
        'el': 'Greek',
        'ms': 'Malay',
        'cs': 'Czech',
        'ro': 'Romanian',
        'da': 'Danish',
        'hu': 'Hungarian',
        'ta': 'Tamil',
        'no': 'Norwegian',
        'th': 'Thai',
        'ur': 'Urdu',
        'hr': 'Croatian',
        'bg': 'Bulgarian',
        'lt': 'Lithuanian',
        'la': 'Latin',
        'mi': 'Maori',
        'ml': 'Malayalam',
        'cy': 'Welsh',
        'sk': 'Slovak',
        'te': 'Telugu',
        'fa': 'Persian',
        'lv': 'Latvian',
        'bn': 'Bengali',
        'sr': 'Serbian',
        'az': 'Azerbaijani',
        'sl': 'Slovenian',
        'kn': 'Kannada',
        'et': 'Estonian',
        'mk': 'Macedonian',
        'br': 'Breton',
        'eu': 'Basque',
        'is': 'Icelandic',
        'hy': 'Armenian',
        'ne': 'Nepali',
        'mn': 'Mongolian',
        'bs': 'Bosnian',
        'kk': 'Kazakh',
        'sq': 'Albanian',
        'sw': 'Swahili',
        'gl': 'Galician',
        'mr': 'Marathi',
        'pa': 'Punjabi',
        'si': 'Sinhala',
        'km': 'Khmer',
        'sn': 'Shona',
        'yo': 'Yoruba',
        'so': 'Somali',
        'af': 'Afrikaans',
        'oc': 'Occitan',
        'ka': 'Georgian',
        'be': 'Belarusian',
        'tg': 'Tajik',
        'sd': 'Sindhi',
        'gu': 'Gujarati',
        'am': 'Amharic',
        'yi': 'Yiddish',
        'lo': 'Lao',
        'uz': 'Uzbek',
        'fo': 'Faroese',
        'ht': 'Haitian Creole',
        'ps': 'Pashto',
        'tk': 'Turkmen',
        'nn': 'Nynorsk',
        'mt': 'Maltese',
        'sa': 'Sanskrit',
        'lb': 'Luxembourgish',
        'my': 'Myanmar',
        'bo': 'Tibetan',
        'tl': 'Tagalog',
        'mg': 'Malagasy',
        'as': 'Assamese',
        'tt': 'Tatar',
        'haw': 'Hawaiian',
        'ln': 'Lingala',
        'ha': 'Hausa',
        'ba': 'Bashkir',
        'jw': 'Javanese',
        'su': 'Sundanese'
    }
    return jsonify(languages)

if __name__ == '__main__':
    print("Starting Video Transcriber Server...")
    print(f"Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    app.run(host='0.0.0.0', port=5001, debug=True)