"""
YouTube Transcript Extraction Module

Provides async functions to extract transcripts from YouTube videos.
Uses youtube-transcript-api for reliable transcript retrieval.
"""

import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import logging

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
