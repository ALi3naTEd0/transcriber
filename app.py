#!/usr/bin/env python3
"""
Streamlit Transcriber App
Transcribe videos and audio from multiple sources using OpenAI's Whisper
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
import yt_dlp
import whisper
from datetime import datetime
import time


class TranscriberApp:
    def __init__(self, model_size="large", device="auto"):
        """Initialize the transcriber"""
        # Auto-detect device if set to 'auto'
        if device == "auto":
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
            except:
                device = "cpu"
        
        self.device = device
        self.model = whisper.load_model(model_size, device=device)
        self.downloads_dir = Path("downloads")
        self.transcripts_dir = Path("transcripts")
        
        # Create directories if they don't exist
        self.downloads_dir.mkdir(exist_ok=True)
        self.transcripts_dir.mkdir(exist_ok=True)
    
    def download_audio(self, url, audio_quality="original", progress_callback=None):
        """Download audio from URL"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.downloads_dir / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        # Only convert to AAC if explicitly requested
        if audio_quality == 'aac':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'aac',
                'preferredquality': '192',
            }]
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info['title']
            
            # Get the actual downloaded filename
            downloaded_file = Path(ydl.prepare_filename(info))
            
            if audio_quality == 'aac':
                audio_file = downloaded_file.with_suffix('.m4a')
            else:
                audio_file = downloaded_file
            
            if not audio_file.exists():
                # Fallback: find the most recent audio file
                import glob
                base_name = downloaded_file.stem
                pattern = str(self.downloads_dir / f"{base_name}.*")
                files = glob.glob(pattern)
                audio_exts = {'.mp3', '.m4a', '.opus', '.webm', '.ogg', '.wav', '.flac', '.aac', '.mp4', '.mkv'}
                audio_files = [f for f in files if Path(f).suffix.lower() in audio_exts]
                if audio_files:
                    audio_file = Path(max(audio_files, key=os.path.getctime))
            
            return audio_file, video_title
    
    def transcribe_audio(self, audio_file, language=None):
        """Transcribe an audio file using Whisper"""
        use_fp16 = self.device == "cuda"
        transcribe_options = {"fp16": use_fp16}
        
        if language:
            transcribe_options["language"] = language
        
        result = self.model.transcribe(str(audio_file), **transcribe_options)
        return result
    
    def save_transcript(self, video_title, result, source_url):
        """Save the transcription to text files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title[:50]
        
        # Files
        txt_file = self.transcripts_dir / f"{safe_title}_{timestamp}.txt"
        srt_file = self.transcripts_dir / f"{safe_title}_{timestamp}_timestamps.txt"
        lyrics_file = self.transcripts_dir / f"{safe_title}_{timestamp}_lyrics.txt"
        
        # Save complete transcription
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"Transcription of: {video_title}\n")
            f.write(f"Source: {source_url}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Language: {result['language']}\n")
            f.write("=" * 80 + "\n\n")
            f.write(result['text'].strip())
        
        # Save with timestamps
        with open(srt_file, 'w', encoding='utf-8') as f:
            f.write(f"Transcription with timestamps of: {video_title}\n")
            f.write(f"Source: {source_url}\n")
            f.write("=" * 80 + "\n\n")
            
            for segment in result['segments']:
                start_time = self._format_timestamp(segment['start'])
                end_time = self._format_timestamp(segment['end'])
                text = segment['text'].strip()
                f.write(f"[{start_time} --> {end_time}]\n{text}\n\n")
        
        # Save lyrics format
        with open(lyrics_file, 'w', encoding='utf-8') as f:
            f.write(f"Transcription of: {video_title}\n")
            f.write(f"Source: {source_url}\n")
            f.write("=" * 80 + "\n\n")
            
            current_paragraph = []
            for i, segment in enumerate(result['segments']):
                text = segment['text'].strip()
                current_paragraph.append(text)
                
                is_long_pause = False
                if i + 1 < len(result['segments']):
                    next_segment = result['segments'][i + 1]
                    pause_duration = next_segment['start'] - segment['end']
                    is_long_pause = pause_duration > 1.5
                
                is_paragraph_full = len(current_paragraph) >= 6
                is_last_segment = i == len(result['segments']) - 1
                
                if is_long_pause or is_paragraph_full or is_last_segment:
                    paragraph_text = '\n'.join(current_paragraph)
                    f.write(f"{paragraph_text}\n\n")
                    current_paragraph = []
        
        return txt_file, srt_file, lyrics_file
    
    def _format_timestamp(self, seconds):
        """Format seconds to HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def main():
    st.set_page_config(
        page_title="Transcriber",
        page_icon="🎥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎥 Video & Audio Transcriber")
    st.markdown("*Powered by OpenAI Whisper AI*")
    
    # Initialize session state for transcription results
    if 'transcription_result' not in st.session_state:
        st.session_state.transcription_result = None
    if 'transcript_files' not in st.session_state:
        st.session_state.transcript_files = None
    if 'video_title' not in st.session_state:
        st.session_state.video_title = None
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model selection
        model_options = {
            "tiny": "tiny",
            "base": "base",
            "small": "small",
            "medium": "medium",
            "large": "large"
        }
        model_choice = st.selectbox(
            "Model Size",
            options=list(model_options.keys()),
            index=4,  # Default to large
            help="**tiny**: Fast, ~60% accuracy\n**base**: Balanced, ~70% accuracy\n**small**: Good, ~80% accuracy\n**medium**: Very good, ~90% accuracy\n**large**: Best, ~95%+ accuracy"
        )
        model_size = model_options[model_choice]
        
        # Device selection
        device = st.selectbox(
            "Device",
            options=["auto", "cuda", "cpu"],
            index=0,
            help="auto: automatically detect GPU, cuda: force GPU, cpu: force CPU"
        )
        
        # Audio quality
        quality_options = {
            "Original": "original",
            "AAC": "aac"
        }
        quality_choice = st.selectbox(
            "Audio Quality",
            options=list(quality_options.keys()),
            index=0,
            help="**Original**: No conversion, keeps original format\n**AAC**: Converts to AAC format (fast, smaller file size)\n\n*Only applies to video downloads, not uploaded files*"
        )
        audio_quality = quality_options[quality_choice]
        
        # Language
        language_options = {
            "Auto-detect": None,
            "English (en)": "en",
            "Spanish (es)": "es",
            "French (fr)": "fr",
            "German (de)": "de",
            "Italian (it)": "it",
            "Portuguese (pt)": "pt",
            "Russian (ru)": "ru",
            "Japanese (ja)": "ja",
            "Chinese (zh)": "zh",
            "Korean (ko)": "ko",
            "Arabic (ar)": "ar",
            "Hindi (hi)": "hi"
        }
        language_choice = st.selectbox(
            "Language (optional)",
            options=list(language_options.keys()),
            index=0
        )
        language = language_options[language_choice]
        
        # Keep audio
        keep_audio = st.checkbox("Keep downloaded audio file", value=False)
        
        # New transcription button
        if st.session_state.transcription_result is not None:
            st.markdown("---")
            if st.button("🔄 New Transcription", use_container_width=True):
                st.session_state.transcription_result = None
                st.session_state.transcript_files = None
                st.session_state.video_title = None
                st.rerun()
    
    # Main content area
    tab1, tab2 = st.tabs(["📥 Upload/URL", "ℹ️ Info"])
    
    with tab1:
        st.subheader("Input Source")
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["URL (YouTube, Vimeo, etc.)", "Upload File"],
            horizontal=True
        )
        
        audio_file = None
        video_title = None
        source_url = None
        
        if input_method == "URL (YouTube, Vimeo, etc.)":
            url = st.text_input(
                "Enter video URL",
                placeholder="https://www.youtube.com/watch?v=...",
                help="Supports 1000+ sites via yt-dlp"
            )
            
            if url and st.button("🚀 Start Transcription", type="primary", use_container_width=True):
                try:
                    with st.spinner("Initializing..."):
                        transcriber = TranscriberApp(model_size=model_size, device=device)
                    
                    # Download
                    with st.spinner("📥 Downloading audio..."):
                        audio_file, video_title = transcriber.download_audio(url, audio_quality)
                        st.success(f"✅ Downloaded: {video_title}")
                    
                    source_url = url
                    
                except Exception as e:
                    st.error(f"❌ Download error: {str(e)}")
                    st.stop()
        
        else:  # Upload File
            uploaded_file = st.file_uploader(
                "Upload video or audio file",
                type=['mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv', 'webm', 
                      'mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac'],
                help="Supports most video and audio formats"
            )
            
            if uploaded_file and st.button("🚀 Start Transcription", type="primary", use_container_width=True):
                try:
                    with st.spinner("Initializing..."):
                        transcriber = TranscriberApp(model_size=model_size, device=device)
                    
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        audio_file = Path(tmp_file.name)
                    
                    video_title = Path(uploaded_file.name).stem
                    source_url = f"Local file: {uploaded_file.name}"
                    st.success(f"✅ File loaded: {uploaded_file.name}")
                    
                except Exception as e:
                    st.error(f"❌ File error: {str(e)}")
                    st.stop()
        
        # Transcription
        if audio_file:
            try:
                # Transcribe
                with st.spinner("🎤 Transcribing audio... This may take several minutes."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Estimate time based on model
                    time_estimates = {
                        "tiny": "~30 seconds",
                        "base": "~1 minute",
                        "small": "~2-3 minutes",
                        "medium": "~5-10 minutes",
                        "large": "~10-15 minutes"
                    }
                    status_text.text(f"Estimated time: {time_estimates.get(model_size, 'several minutes')}")
                    
                    result = transcriber.transcribe_audio(audio_file, language)
                    progress_bar.progress(100)
                
                # Save files
                with st.spinner("💾 Saving transcription files..."):
                    txt_file, srt_file, lyrics_file = transcriber.save_transcript(
                        video_title, result, source_url
                    )
                
                # Store in session state
                st.session_state.transcription_result = result
                st.session_state.transcript_files = (txt_file, srt_file, lyrics_file)
                st.session_state.video_title = video_title
                
                # Cleanup
                if not keep_audio and source_url and source_url.startswith("http"):
                    if audio_file.exists():
                        audio_file.unlink()
                
                # Cleanup temp files for uploads
                if input_method == "Upload File" and audio_file.exists():
                    try:
                        audio_file.unlink()
                    except:
                        pass
                
            except Exception as e:
                st.error(f"❌ Transcription error: {str(e)}")
        
        # Display results if they exist in session state
        if st.session_state.transcription_result is not None:
            result = st.session_state.transcription_result
            txt_file, srt_file, lyrics_file = st.session_state.transcript_files
            
            st.success(f"✅ Transcription completed! Detected language: **{result['language']}**")
            
            # Display transcription
            st.subheader("📝 Transcription")
            with st.expander("View full transcription", expanded=True):
                st.text_area("Text", result['text'], height=300, key="transcription_display")
            
            st.success("✅ Files saved!")
            
            # Download buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="📄 Download Full Text",
                        data=f.read(),
                        file_name=txt_file.name,
                        mime="text/plain",
                        key="download_txt"
                    )
            
            with col2:
                with open(srt_file, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="⏱️ Download with Timestamps",
                        data=f.read(),
                        file_name=srt_file.name,
                        mime="text/plain",
                        key="download_srt"
                    )
            
            with col3:
                with open(lyrics_file, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="📖 Download Lyrics Format",
                        data=f.read(),
                        file_name=lyrics_file.name,
                        mime="text/plain",
                        key="download_lyrics"
                    )
    
    with tab2:
        st.subheader("ℹ️ About")
        st.markdown("""
        This app transcribes videos and audio files using **OpenAI's Whisper AI**.
        
        **Supported Sources:**
        - 🌐 YouTube and 1000+ video sites (via yt-dlp)
        - 📁 Local video files (MP4, MKV, AVI, MOV, etc.)
        - 🎵 Local audio files (MP3, WAV, M4A, FLAC, etc.)
        
        **Features:**
        - 🎯 Automatic language detection
        - 📊 Multiple model sizes (speed vs accuracy tradeoff)
        - ⚡ GPU acceleration support
        - 📝 Multiple output formats (plain text, timestamps, lyrics)
        - 🔄 No unnecessary audio conversion
        
        **Model Accuracy:**
        - **tiny**: Fast, ~60% accuracy
        - **base**: Balanced, ~70% accuracy
        - **small**: Good, ~80% accuracy
        - **medium**: Very good, ~90% accuracy
        - **large**: Best, ~95%+ accuracy
        
        **Performance (10-minute video):**
        | Model | CPU Time | GPU Time |
        |-------|----------|----------|
        | tiny  | ~5 min   | ~30 sec  |
        | base  | ~10 min  | ~1 min   |
        | small | ~30 min  | ~2 min   |
        | medium| ~1 hour  | ~5 min   |
        | large | ~2 hours | ~10 min  |
        
        ---
        
        *Powered by [OpenAI Whisper](https://github.com/openai/whisper) and [yt-dlp](https://github.com/yt-dlp/yt-dlp)*
        """)


if __name__ == "__main__":
    main()
