# Transcriber 🎥→📝

Versatile Python program to transcribe videos from multiple sources using OpenAI's Whisper AI.

## 🚀 Features

- **Multiple video sources supported:**
  - YouTube and 1000+ video sites (via yt-dlp: YouTube, Vimeo, Dailymotion, TikTok, etc.)
  - Local video files (MP4, MKV, AVI, MOV, FLV, WebM, etc.)
  - Local audio files (MP3, WAV, M4A, FLAC, OGG, AAC, etc.)
- **Easy-to-use GUI** with drag-and-drop support
- Accurate transcription using Whisper AI
- Automatic language detection
- Configurable audio quality for downloads
- Generates transcriptions with and without timestamps
- Multiple model sizes (from tiny to large)
- Both GUI and command-line interfaces

## 📋 Requirements

- Python 3.8 or higher
- FFmpeg (required for audio processing)

### Installing FFmpeg

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Linux (Fedora):**
```bash
sudo dnf install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## 🔧 Installation

1. Clone or download this project

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

**Note:** The first time you run the program, Whisper will download the selected model (may take a few minutes).

## 💻 Usage

### Streamlit Web App (Recommended):
```bash
streamlit run app.py
```

The Streamlit app provides:
- Modern web interface accessible from any browser
- Easy file upload with drag-and-drop
- URL input for YouTube and 1000+ video sites
- Dropdowns for all settings (model, device, quality, language)
- Real-time progress tracking
- Instant download of transcription files
- **Easy deployment** to Streamlit Cloud, Hugging Face, or any platform

### Desktop GUI (Alternative):
```bash
python transcriber.py --gui
```

The Tkinter GUI provides:
- Native desktop application
- Works offline
- All the same features as Streamlit

### Command-Line Usage:

**Transcribe from YouTube or other sites:**
```bash
python transcriber.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Transcribe a local video file:**
```bash
python transcriber.py "/path/to/video.mp4"
```

**Transcribe with options:**
```bash
python transcriber.py "VIDEO_URL_OR_FILE" --model small --device cuda --language en --keep-audio
```

### Available options:

- `--gui`: Launch graphical user interface

- `--model <size>`: Whisper model size
  - `tiny`: Faster, less accurate (~1GB RAM, ~32x speed)
  - `base`: Speed/accuracy balance (~1GB RAM, ~16x speed)
  - `small`: Good accuracy (~2GB RAM, ~6x speed)
  - `medium`: Very good accuracy (~5GB RAM, ~2x speed)
  - `large`: Maximum accuracy (~10GB RAM, GPU recommended) [**Default**]

- `--device <type>`: Processing device
  - `auto`: Automatically detect and use GPU if available [**Default**]
  - `cuda`: Force GPU (NVIDIA CUDA)
  - `cpu`: Force CPU only

- `--language <code>`: Specify language (optional)
  - Examples: `en`, `es`, `fr`, `de`, `it`, `pt`, `ru`, `ja`, `zh`
  - If not specified, Whisper detects it automatically

- `--keep-audio`: Keep downloaded audio file (only for URLs)

## 📂 File Structure

The program creates two folders:

```
transcriber/
├── downloads/          # Audio files (temporary)
└── transcripts/        # Generated transcriptions
    ├── video_title_TIMESTAMP.txt
    ├── video_title_TIMESTAMP_timestamps.txt
    └── video_title_TIMESTAMP_lyrics.txt
```

## 📝 Examples

**Launch GUI:**
```bash
python transcriber.py --gui
```

**Transcribe a YouTube video:**
```bash
python transcriber.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Transcribe from Vimeo:**
```bash
python transcriber.py "https://vimeo.com/123456789"
```

**Transcribe a local video file:**
```bash
python transcriber.py "my_video.mp4" --model medium
```

**Transcribe with more accurate model:**
```bash
python transcriber.py "https://youtu.be/VIDEO_ID" --model large
```

**Force GPU acceleration:**
```bash
python transcriber.py "video.mp4" --device cuda
```

**Transcribe specifying Spanish language:**
```bash
python transcriber.py "https://www.youtube.com/watch?v=VIDEO_ID" --language es
```

**Keep the audio file:**
```bash
python transcriber.py "https://www.youtube.com/watch?v=VIDEO_ID" --keep-audio
```

## 🎯 Output Formats

The program generates three transcription files:

1. **Complete transcription** (`_TIMESTAMP.txt`):
   - Continuous text without timestamps
   - Video metadata
   - Ideal for reading

2. **Transcription with timestamps** (`_TIMESTAMP_timestamps.txt`):
   - Segmented text with time markers
   - Format: `[HH:MM:SS --> HH:MM:SS]`
   - Useful for temporal reference

3. **Lyrics format** (`_TIMESTAMP_lyrics.txt`):
   - Text grouped in paragraphs
   - Natural reading flow
   - Ideal for song lyrics or speeches

## ⚡ Performance

Approximate times for a 10-minute video:

| Model  | Time (CPU) | Time (GPU) | RAM   | VRAM  | Accuracy     |
|:-------|:-----------|:-----------|:------|:------|:-------------|
| tiny   | ~5min      | ~30s       | ~1GB  | ~1GB  | ⭐⭐⭐         |
| base   | ~10min     | ~1min      | ~1GB  | ~1GB  | ⭐⭐⭐⭐       |
| small  | ~30min     | ~2min      | ~2GB  | ~2GB  | ⭐⭐⭐⭐⭐     |
| medium | ~1h        | ~5min      | ~5GB  | ~5GB  | ⭐⭐⭐⭐⭐⭐   |
| large  | ~2h        | ~10min     | ~10GB | ~10GB | ⭐⭐⭐⭐⭐⭐⭐ |

**Note:** GPU significantly improves speed. The `large` model is recommended for best accuracy but requires a GPU for practical use.

## � Deployment

### Deploy to Streamlit Cloud (Free):

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set main file to `app.py`
5. Deploy! 🎉

### Deploy to Hugging Face Spaces:

1. Create a new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Choose "Streamlit" as the SDK
3. Upload your files or connect to GitHub
4. Your app will be live in minutes!

### Local Network Access:

Share your local instance on your network:
```bash
streamlit run app.py --server.address 0.0.0.0
```

Access from other devices at: `http://YOUR_IP:8501`

## 🛠️ Troubleshooting

**Error: "ffmpeg not found"**
- Make sure you have FFmpeg installed (see requirements section)

**Memory error**
- Use a smaller model (`--model tiny` or `--model base`)

**Error downloading video**
- Verify the URL is correct and the video is public
- Some videos may have download restrictions

**Streamlit app slow on first model load**
- This is normal - Whisper downloads the model on first use
- Subsequent uses will be much faster

## 📄 License

This project is open source and available for personal and educational use.

## 🤝 Contributing

Contributions are welcome! Feel free to improve the code.

## 🙏 Acknowledgments

- [Whisper](https://github.com/openai/whisper) - OpenAI
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloading
- [FFmpeg](https://ffmpeg.org/) - Audio processing
