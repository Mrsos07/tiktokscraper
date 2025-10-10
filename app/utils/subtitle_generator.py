"""
Subtitle Generator - Extract audio and generate Arabic subtitles
"""
import subprocess
from pathlib import Path
from typing import Optional
from app.core.logging import log


def extract_audio(video_path: Path, audio_path: Path) -> bool:
    """Extract audio from video using ffmpeg"""
    try:
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # No video
            '-acodec', 'pcm_s16le',
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',  # Mono
            '-y',  # Overwrite
            str(audio_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    except Exception as e:
        log.error(f"Error extracting audio: {e}")
        return False


def generate_arabic_subtitle(video_path: Path) -> Optional[Path]:
    """
    Generate Arabic subtitle for video
    
    Args:
        video_path: Path to video file
        
    Returns:
        Path to generated .srt file or None
    """
    try:
        log.info(f"🎬 Generating Arabic subtitle for {video_path.name}")
        
        # Use yt-dlp to get auto-generated captions if available
        import yt_dlp
        
        video_id = video_path.stem
        subtitle_path = video_path.parent / f"{video_id}.ar.srt"
        
        # Try to get captions from TikTok
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ar', 'en'],
            'skip_download': True,
            'outtmpl': str(video_path.parent / video_id),
        }
        
        # Get video URL from filename (assuming it's stored in metadata)
        # For now, we'll use Whisper to transcribe
        
        log.info("   Using Whisper for transcription...")
        
        # Extract audio first
        audio_path = video_path.parent / f"{video_id}.wav"
        if not extract_audio(video_path, audio_path):
            log.error("   Failed to extract audio")
            return None
        
        # Use Whisper to transcribe
        try:
            import whisper
            
            log.info("   Loading Whisper model...")
            model = whisper.load_model("base")
            
            log.info("   Transcribing audio...")
            result = model.transcribe(
                str(audio_path),
                language='ar',  # Force Arabic
                task='translate'  # Translate to Arabic if not already
            )
            
            # Generate SRT file
            log.info("   Generating SRT file...")
            with open(subtitle_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(result['segments'], 1):
                    start = format_timestamp(segment['start'])
                    end = format_timestamp(segment['end'])
                    text = segment['text'].strip()
                    
                    f.write(f"{i}\n")
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{text}\n\n")
            
            # Clean up audio file
            audio_path.unlink(missing_ok=True)
            
            log.info(f"   ✅ Subtitle saved: {subtitle_path.name}")
            return subtitle_path
            
        except ImportError:
            log.warning("   Whisper not installed, skipping subtitle generation")
            audio_path.unlink(missing_ok=True)
            return None
            
    except Exception as e:
        log.error(f"   ❌ Error generating subtitle: {e}")
        return None


def format_timestamp(seconds: float) -> str:
    """Format seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def embed_subtitle(video_path: Path, subtitle_path: Path, output_path: Path) -> bool:
    """
    Embed subtitle into video using ffmpeg
    
    Args:
        video_path: Original video
        subtitle_path: SRT subtitle file
        output_path: Output video with embedded subtitle
        
    Returns:
        True if successful
    """
    try:
        log.info(f"   📝 Embedding subtitle into video...")
        
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vf', f"subtitles={str(subtitle_path)}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3'",
            '-c:a', 'copy',
            '-y',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            log.info(f"   ✅ Video with subtitle: {output_path.name}")
            return True
        else:
            log.error(f"   ❌ ffmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        log.error(f"   ❌ Error embedding subtitle: {e}")
        return False
