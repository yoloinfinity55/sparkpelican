"""
YouTube Transcript Extraction Module

Provides async functions to extract transcripts from YouTube videos.
Uses youtube-transcript-api for reliable transcript retrieval.
"""

import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import logging
import json

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
        RequestBlocked  # Using RequestBlocked instead of TooManyRequests
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

    Args:
        youtube_url: YouTube video URL
        language: Preferred transcript language (default: English)

    Returns:
        Full transcript text

    Raises:
        TranscriptError: If transcript cannot be extracted
    """
    if not YOUTUBE_TRANSCRIPT_AVAILABLE:
        raise TranscriptError("youtube-transcript-api not installed")

    try:
        # Extract video ID
        video_id = extract_video_id(youtube_url)

        # Run transcript extraction in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        transcript_data = await loop.run_in_executor(
            None,
            _get_transcript_sync,
            video_id,
            language
        )

        # Combine all transcript segments
        transcript_parts = []
        for segment in transcript_data:
            transcript_parts.append(segment.text)

        return ' '.join(transcript_parts)

    except (TranscriptsDisabled, NoTranscriptFound) as e:
        raise TranscriptError(f"No transcript available for this video: {str(e)}")
    except VideoUnavailable as e:
        raise TranscriptError(f"Video unavailable: {str(e)}")
    except RequestBlocked as e:
        raise TranscriptError(f"Rate limited by YouTube: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error extracting transcript: {str(e)}")
        raise TranscriptError(f"Failed to extract transcript: {str(e)}")

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
                if transcript.language_code.startswith(language[:2]):  # Match language prefix
                    return transcript.fetch()

            # If no preferred language found, get first available
            for transcript in transcript_list:
                return transcript.fetch()

            raise NoTranscriptFound("No transcripts available")

    except NoTranscriptFound:
        raise NoTranscriptFound("No transcripts available")

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
        output_dir: Directory to save the thumbnail (default: content/images)

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
        import os
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
            # Return relative path for Pelican
            rel_path = os.path.relpath(local_path)
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
        # Fallback: simple detection based on common words/characters
        return _detect_language_fallback(transcript)

    try:
        # Use langdetect library for more accurate detection
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
        # Clean transcript for better detection
        clean_text = re.sub(r'[^\w\s\u4e00-\u9fff\uac00-\ud7af]', '', transcript)
        detected = detect(clean_text)

        # Map common language codes to more specific ones
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
        return 'en'  # Default to English if detection fails

def _detect_language_fallback(transcript: str) -> str:
    """Fallback language detection based on character analysis."""
    # Count Chinese characters (CJK Unified Ideographs)
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', transcript))

    # Count Korean characters (Hangul syllables)
    korean_chars = len(re.findall(r'[\uac00-\ud7af]', transcript))

    # Count Japanese characters (Hiragana, Katakana, Kanji)
    japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]', transcript))

    # Calculate percentages
    total_chars = len(transcript.replace(' ', ''))
    if total_chars == 0:
        return 'en'

    chinese_pct = chinese_chars / total_chars
    korean_pct = korean_chars / total_chars
    japanese_pct = japanese_chars / total_chars

    # Determine primary language based on character percentages
    if chinese_pct > 0.1:  # More than 10% Chinese characters
        return 'zh-cn'
    elif korean_pct > 0.1:  # More than 10% Korean characters
        return 'ko'
    elif japanese_pct > 0.1:  # More than 10% Japanese characters
        return 'ja'
    else:
        return 'en'  # Default to English
