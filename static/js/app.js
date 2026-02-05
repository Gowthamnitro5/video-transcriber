// Video Transcriber App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const fileIcon = document.getElementById('fileIcon');
    const removeFileBtn = document.getElementById('removeFile');
    const optionsSection = document.getElementById('optionsSection');
    const actionButtons = document.getElementById('actionButtons');
    const transcribeBtn = document.getElementById('transcribeBtn');
    const uploadSection = document.getElementById('uploadSection');
    const processingSection = document.getElementById('processingSection');
    const resultsSection = document.getElementById('resultsSection');
    const errorSection = document.getElementById('errorSection');
    const progressText = document.getElementById('progressText');
    const transcriptionText = document.getElementById('transcriptionText');
    const newTranscriptionBtn = document.getElementById('newTranscriptionBtn');
    const tryAgainBtn = document.getElementById('tryAgainBtn');
    const errorMessage = document.getElementById('errorMessage');
    const languageSelect = document.getElementById('languageSelect');
    const loadingOverlay = document.getElementById('loadingOverlay');

    let selectedFile = null;
    let transcriptionFiles = {};

    // Load supported languages
    loadLanguages();

    // File Drop Zone Events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // File Input Change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Remove File
    removeFileBtn.addEventListener('click', () => {
        resetFileSelection();
    });

    // Transcribe Button
    transcribeBtn.addEventListener('click', startTranscription);

    // New Transcription Button
    newTranscriptionBtn.addEventListener('click', () => {
        resetAll();
        showSection(uploadSection);
    });

    // Try Again Button
    tryAgainBtn.addEventListener('click', () => {
        showSection(uploadSection);
    });

    // Handle file selection
    function handleFileSelect(file) {
        const allowedTypes = [
            'video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska', 'video/webm',
            'audio/mpeg', 'audio/wav', 'audio/x-m4a', 'audio/ogg', 'audio/flac',
            'audio/mp3', 'audio/mp4'
        ];
        
        const allowedExtensions = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'mp3', 'wav', 'm4a', 'ogg', 'flac'];
        const fileExtension = file.name.split('.').pop().toLowerCase();
        
        if (!allowedExtensions.includes(fileExtension)) {
            showError('Invalid file type. Please upload a video or audio file.');
            return;
        }

        if (file.size > 500 * 1024 * 1024) {
            showError('File size too large. Maximum size is 500MB.');
            return;
        }

        selectedFile = file;
        
        // Update file info display
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        
        // Set appropriate icon
        if (file.type.startsWith('video') || ['mp4', 'avi', 'mov', 'mkv', 'webm'].includes(fileExtension)) {
            fileIcon.className = 'fas fa-file-video';
        } else {
            fileIcon.className = 'fas fa-file-audio';
        }

        // Show file info and options
        fileInfo.style.display = 'flex';
        optionsSection.style.display = 'grid';
        actionButtons.style.display = 'block';
        
        // Hide drop zone
        dropZone.style.display = 'none';
    }

    // Reset file selection
    function resetFileSelection() {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.style.display = 'none';
        optionsSection.style.display = 'none';
        actionButtons.style.display = 'none';
        dropZone.style.display = 'block';
    }

    // Reset all
    function resetAll() {
        resetFileSelection();
        transcriptionText.textContent = '';
        transcriptionFiles = {};
    }

    // Start transcription
    async function startTranscription() {
        if (!selectedFile) {
            showError('Please select a file first.');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('language', languageSelect.value);
        formData.append('task', document.getElementById('taskSelect').value);

        showSection(processingSection);
        updateProgress('Uploading file...');

        try {
            const response = await fetch('/transcribe', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                displayResults(data);
            } else {
                showError(data.error || 'Transcription failed. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            showError('Network error. Please check your connection and try again.');
        }
    }

    // Display transcription results
    function displayResults(data) {
        const transcription = data.transcription;
        transcriptionFiles = data.files;

        // Update stats
        document.getElementById('durationStat').textContent = formatDuration(transcription.duration);
        document.getElementById('languageStat').textContent = transcription.language.toUpperCase();
        document.getElementById('segmentsStat').textContent = transcription.segments.length;

        // Display transcription text
        transcriptionText.textContent = transcription.text;

        // Update download links
        document.getElementById('downloadDoc').href = `/download/${transcriptionFiles.document}`;
        document.getElementById('downloadSrt').href = `/download/${transcriptionFiles.subtitles}`;
        document.getElementById('downloadJson').href = `/download/${transcriptionFiles.json}`;

        showSection(resultsSection);
    }

    // Update progress text
    function updateProgress(text) {
        progressText.textContent = text;
    }

    // Show specific section
    function showSection(section) {
        uploadSection.style.display = 'none';
        processingSection.style.display = 'none';
        resultsSection.style.display = 'none';
        errorSection.style.display = 'none';
        
        section.style.display = 'block';
    }

    // Show error
    function showError(message) {
        errorMessage.textContent = message;
        showSection(errorSection);
    }

    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Format duration
    function formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }

    // Load supported languages
    async function loadLanguages() {
        try {
            const response = await fetch('/supported-languages');
            const languages = await response.json();
            
            Object.entries(languages).forEach(([code, name]) => {
                if (code !== 'auto') {
                    const option = document.createElement('option');
                    option.value = code;
                    option.textContent = name;
                    languageSelect.appendChild(option);
                }
            });
        } catch (error) {
            console.error('Failed to load languages:', error);
        }
    }
});