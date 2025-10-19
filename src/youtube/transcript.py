"""
YouTube Transcript Extraction Module

Provides async functions to extract transcripts from YouTube videos.
Uses youtube-transcript-api for reliable transcript retrieval.
Falls back to audio transcription using Gemini when subtitles unavailable.
"""

import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import logging
import json
import os
import tempfile

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
        RequestBlocked
    )
    YOUTUBE_TRANSCRIPT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: youtube-transcript-api import failed: {e}")
    YOUTUBE_TRANSCRIPT_AVAILABLE = False
    NoTranscriptFound = Exception
    TranscriptsDisabled = Exception
    VideoUnavailable = Exception
    RequestBlocked = Exception

# Add missing import for re module
import re

# Try to import requests for metadata fetching
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Try to import langdetect for language detection
try:
    from langdetect import detect, LangDetectError
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

# Try to import PIL for image processing
try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Try to import yt-dlp for audio extraction
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("Warning: yt-dlp not available. Audio fallback will not work.")

# Try to import google.generativeai for audio transcription
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google-generativeai not available. Audio transcription will not work.")

logger = logging.getLogger(__name__)

class TranscriptError(Exception):
    """Custom exception for transcript extraction errors."""
    pass

async def get_transcript_async(
    youtube_url: str,
    language: str = 'en'
) -> str:
    """
    Extract transcript from YouTube video asynchronously.
    Falls back to audio transcription if subtitles are unavailable.

    Args:
        youtube_url: YouTube video URL
        language: Preferred transcript language (default: English)

    Returns:
        Full transcript text

    Raises:
        TranscriptError: If transcript cannot be extracted
    """
    # First try subtitle extraction
    try:
        if YOUTUBE_TRANSCRIPT_AVAILABLE:
            video_id = extract_video_id(youtube_url)
            loop = asyncio.get_event_loop()
            transcript_data = await loop.run_in_executor(
                None,
                _get_transcript_sync,
                video_id,
                language
            )
            
            # Combine all transcript segments
            transcript_parts = [segment.text for segment in transcript_data]
            transcript = ' '.join(transcript_parts)
            print(f"✅ Transcript extracted from subtitles ({len(transcript)} characters)")
            return transcript
            
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        print(f"ℹ️  No subtitles available: {str(e)}")
        # Fall through to audio transcription
    except Exception as e:
        logger.warning(f"Subtitle extraction failed: {str(e)}")
        # Fall through to audio transcription
    
    # Fallback: Audio transcription
    print("⚠️  Falling back to audio transcription...")
    if not YT_DLP_AVAILABLE or not GENAI_AVAILABLE:
        raise TranscriptError(
            "Audio transcription unavailable. Install yt-dlp and google-generativeai:\n"
            "pip install yt-dlp google-generativeai"
        )
    
    try:
        transcript = await _transcribe_audio_async(youtube_url)
        print(f"✅ Transcript extracted from audio ({len(transcript)} characters)")
        return transcript
    except Exception as e:
        raise TranscriptError(f"Both subtitle and audio transcription failed: {str(e)}")

def _get_transcript_sync(video_id: str, language: str) -> list:
    """Synchronous transcript extraction helper."""
    if not YOUTUBE_TRANSCRIPT_AVAILABLE:
        raise TranscriptError("youtube-transcript-api not installed")

    try:
        # Create API instance
        ytt_api = YouTubeTranscriptApi()

        # Get transcript list
        transcript_list = ytt_api.list(video_id)

        # Try to find transcript in preferred language
        try:
            transcript = transcript_list.find_transcript([language])
            return transcript.fetch()
        except NoTranscriptFound:
            # Try manually created transcripts first
            try:
                transcript = transcript_list.find_manually_created_transcript()
                if transcript:
                    return transcript.fetch()
            except NoTranscriptFound:
                pass

            # Try any available transcript
            for transcript in transcript_list:
                if transcript.language_code.startswith(language[:2]):
                    return transcript.fetch()

            # If no preferred language found, get first available
            for transcript in transcript_list:
                return transcript.fetch()

            raise NoTranscriptFound("No transcripts available")

    except NoTranscriptFound:
        raise NoTranscriptFound("No transcripts available")

async def _transcribe_audio_async(youtube_url: str) -> str:
    """
    Download audio from YouTube video and transcribe using Gemini.
    
    Args:
        youtube_url: YouTube video URL
        
    Returns:
        Transcribed text
    """
    video_id = extract_video_id(youtube_url)
    temp_audio_file = None
    
    try:
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            temp_audio_file = tmp.name
        
        # Download audio
        print("🎵 Downloading audio...")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            _download_audio_sync,
            youtube_url,
            temp_audio_file
        )
        
        # Check if file was created and has content
        if not os.path.exists(temp_audio_file) or os.path.getsize(temp_audio_file) == 0:
            raise TranscriptError("Audio download failed - file not created or empty")
        
        print(f"✅ Audio downloaded ({os.path.getsize(temp_audio_file) / 1024 / 1024:.1f} MB)")
        
        # Transcribe with Gemini
        print("🤖 Transcribing audio with Gemini AI...")
        transcript = await loop.run_in_executor(
            None,
            _transcribe_with_gemini_sync,
            temp_audio_file
        )
        
        return transcript
        
    finally:
        # Clean up temporary file
        if temp_audio_file and os.path.exists(temp_audio_file):
            try:
                os.remove(temp_audio_file)
                logger.info(f"Cleaned up temporary audio file: {temp_audio_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {e}")

def _download_audio_sync(youtube_url: str, output_path: str):
    """Download audio from YouTube video using yt-dlp."""
    # Remove .mp3 extension for yt-dlp template
    output_template = output_path.replace('.mp3', '')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
    except Exception as e:
        raise TranscriptError(f"Failed to download audio: {str(e)}")

def _transcribe_with_gemini_sync(audio_file_path: str) -> str:
    """Transcribe audio file using Gemini API - alternative approach without file upload."""
    import base64
    
    # Configure Gemini API
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise TranscriptError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    
    try:
        print("📤 Preparing audio for Gemini...")
        
        # Read audio file as bytes
        with open(audio_file_path, 'rb') as f:
            audio_bytes = f.read()
        
        # Use the simpler API with inline audio data
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create the audio part
        audio_part = {
            "inline_data": {
                "mime_type": "audio/mp3",
                "data": base64.b64encode(audio_bytes).decode('utf-8')
            }
        }
        
        prompt = "Transcribe this audio file completely and accurately. Include all spoken words. Return only the transcript text, nothing else."
        
        print("🤖 Transcribing with Gemini 2.0 Flash...")
        response = model.generate_content([prompt, audio_part])
        
        if not response or not response.text:
            raise TranscriptError("Empty response from Gemini")
        
        transcript = response.text
        print(f"✅ Transcription complete ({len(transcript)} characters)")
        
        return transcript.strip()
        
    except Exception as e:
        raise TranscriptError(f"Gemini transcription failed: {str(e)}")


def extract_video_id(youtube_url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    url_patterns = [
        r'(?:v=|\/|youtu\.be\/|embed\/|shorts\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
    ]

    for pattern in url_patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract video ID from URL: {youtube_url}")

async def get_available_transcript_languages(youtube_url: str) -> Dict[str, Any]:
    """
    Get available transcript languages for a YouTube video.

    Returns:
        Dict with 'available' key containing list of language codes
    """
    if not YOUTUBE_TRANSCRIPT_AVAILABLE:
        return {"available": [], "error": "youtube-transcript-api not installed"}

    try:
        video_id = extract_video_id(youtube_url)
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)

        languages = []
        for transcript in transcript_list:
            languages.append({
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_generated": transcript.is_generated,
                "is_translatable": transcript.is_translatable
            })

        return {"available": languages}

    except Exception as e:
        return {"available": [], "error": str(e)}

async def get_video_metadata(youtube_url: str) -> Dict[str, Any]:
    """
    Get YouTube video metadata including title and thumbnail.

    Args:
        youtube_url: YouTube video URL

    Returns:
        Dict containing video metadata

    Raises:
        TranscriptError: If metadata cannot be retrieved
    """
    if not REQUESTS_AVAILABLE:
        raise TranscriptError("requests library not available for metadata fetching")

    try:
        video_id = extract_video_id(youtube_url)

        # Use YouTube oEmbed API to get video metadata
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            _fetch_oembed_data,
            oembed_url
        )

        if response:
            return {
                "title": response.get("title", ""),
                "thumbnail_url": response.get("thumbnail_url", ""),
                "author_name": response.get("author_name", ""),
                "video_id": video_id
            }
        else:
            # Fallback: construct thumbnail URL from video ID
            return {
                "title": "",
                "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                "author_name": "",
                "video_id": video_id
            }

    except Exception as e:
        logger.error(f"Error fetching video metadata: {str(e)}")
        video_id = extract_video_id(youtube_url)
        return {
            "title": "",
            "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            "author_name": "",
            "video_id": video_id
        }

def _fetch_oembed_data(oembed_url: str) -> Optional[Dict[str, Any]]:
    """Synchronous oEmbed API call."""
    try:
        response = requests.get(oembed_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"oEmbed API call failed: {str(e)}")
        return None

async def get_video_title_and_thumbnail(youtube_url: str) -> tuple[str, str]:
    """
    Convenience function to get just the title and thumbnail URL.

    Args:
        youtube_url: YouTube video URL

    Returns:
        Tuple of (title, thumbnail_url)
    """
    metadata = await get_video_metadata(youtube_url)
    return metadata.get("title", ""), metadata.get("thumbnail_url", "")

async def download_youtube_thumbnail(youtube_url: str, output_dir: str = "content/images") -> tuple[str, str]:
    """
    Download YouTube video thumbnail and save it locally.

    Args:
        youtube_url: YouTube video URL
        output_dir: Directory to save the thumbnail (default: images)

    Returns:
        Tuple of (title, local_thumbnail_path)

    Raises:
        TranscriptError: If thumbnail cannot be downloaded
    """
    if not REQUESTS_AVAILABLE:
        raise TranscriptError("requests library not available for thumbnail download")

    try:
        # Get video metadata first
        metadata = await get_video_metadata(youtube_url)
        title = metadata.get("title", "")
        thumbnail_url = metadata.get("thumbnail_url", "")

        if not thumbnail_url:
            video_id = extract_video_id(youtube_url)
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

        # Extract video ID for filename
        video_id = extract_video_id(youtube_url)

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Create filename
        safe_title = re.sub(r'[^\w\-_\.]', '_', title[:50]) if title else video_id
        filename = f"{video_id}_{safe_title}.jpg"
        local_path = os.path.join(output_dir, filename)

        # Download thumbnail
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(
            None,
            _download_image,
            thumbnail_url,
            local_path
        )

        if success:
            # Return relative path for Pelican (relative to content directory)
            # Convert content/images/file.jpg -> images/file.jpg
            rel_path = os.path.relpath(local_path)
            if rel_path.startswith('content/'):
                rel_path = rel_path.replace('content/', '', 1)
            return title, rel_path
        else:
            # Fallback to original URL if download fails
            return title, thumbnail_url

    except Exception as e:
        logger.error(f"Error downloading thumbnail: {str(e)}")
        video_id = extract_video_id(youtube_url)
        return "", f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

def _download_image(image_url: str, local_path: str) -> bool:
    """Synchronous image download helper."""
    try:
        response = requests.get(image_url, timeout=10, stream=True)
        response.raise_for_status()

        # Check if the response is actually an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            logger.warning(f"URL does not point to an image: {content_type}")
            return False

        # Save image
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Successfully downloaded thumbnail to: {local_path}")
        return True

    except Exception as e:
        logger.warning(f"Failed to download image from {image_url}: {str(e)}")
        return False

async def detect_transcript_language(transcript: str) -> str:
    """
    Detect the primary language of a transcript.

    Args:
        transcript: The transcript text to analyze

    Returns:
        ISO language code (e.g., 'en', 'zh-cn', 'ko', etc.)
    """
    if not LANGDETECT_AVAILABLE:
        return _detect_language_fallback(transcript)

    try:
        detected_lang = await asyncio.get_event_loop().run_in_executor(
            None,
            _detect_language_sync,
            transcript
        )
        return detected_lang
    except Exception as e:
        logger.warning(f"Language detection failed: {str(e)}")
        return _detect_language_fallback(transcript)

def _detect_language_sync(transcript: str) -> str:
    """Synchronous language detection helper."""
    try:
        clean_text = re.sub(r'[^\w\s\u4e00-\u9fff\uac00-\ud7af]', '', transcript)
        detected = detect(clean_text)

        language_map = {
            'en': 'en',
            'zh': 'zh-cn',
            'zh-cn': 'zh-cn',
            'zh-tw': 'zh-tw',
            'ko': 'ko',
            'ja': 'ja',
            'es': 'es',
            'fr': 'fr',
            'de': 'de',
            'pt': 'pt',
            'ru': 'ru',
            'ar': 'ar',
            'hi': 'hi'
        }

        return language_map.get(detected, detected)
    except LangDetectError:
        return 'en'

def _detect_language_fallback(transcript: str) -> str:
    """Fallback language detection based on character analysis."""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', transcript))
    korean_chars = len(re.findall(r'[\uac00-\ud7af]', transcript))
    japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]', transcript))

    total_chars = len(transcript.replace(' ', ''))
    if total_chars == 0:
        return 'en'

    chinese_pct = chinese_chars / total_chars
    korean_pct = korean_chars / total_chars
    japanese_pct = japanese_chars / total_chars

    if chinese_pct > 0.1:
        return 'zh-cn'
    elif korean_pct > 0.1:
        return 'ko'
    elif japanese_pct > 0.1:
        return 'ja'
    else:
        return 'en'