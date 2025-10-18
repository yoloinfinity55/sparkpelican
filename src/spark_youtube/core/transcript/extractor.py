"""
YouTube Transcript Extraction Module

Handles YouTube subtitle extraction with fallback to audio transcription.
Supports multiple languages and provides robust error handling.
"""

import asyncio
import logging
import re
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlparse, parse_qs

try:
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
    YOUTUBE_TRANSCRIPT_AVAILABLE = True
except ImportError:
    YOUTUBE_TRANSCRIPT_AVAILABLE = False

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    from langdetect import detect, LangDetectError
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

logger = logging.getLogger(__name__)

# Import config only when needed to avoid API key requirement for basic functionality
_config = None

def _get_config():
    """Get config only when needed."""
    global _config
    if _config is None:
        from spark_youtube.config.settings import get_config
        _config = get_config()
    return _config

class TranscriptError(Exception):
    """Custom exception for transcript-related errors."""
    pass

class LanguageDetector:
    """Handles language detection for transcripts."""

    def __init__(self):
        """Initialize language detector."""
        if not LANGDETECT_AVAILABLE:
            logger.warning("langdetect not available, language detection may be limited")

    def detect_language(self, text: str) -> str:
        """
        Detect the primary language of the text.

        Args:
            text: Text to analyze

        Returns:
            Language code (e.g., 'en', 'zh-cn')
        """
        if not text or len(text.strip()) < 10:
            return 'en'  # Default fallback

        # Remove common YouTube metadata that might confuse detection
        clean_text = self._clean_text_for_detection(text)

        try:
            if LANGDETECT_AVAILABLE:
                detected = detect(clean_text)
                return self._normalize_language_code(detected)
        except LangDetectError as e:
            logger.warning(f"Language detection failed: {e}")

        # Fallback: simple heuristics
        return self._heuristic_language_detection(clean_text)

    def _clean_text_for_detection(self, text: str) -> str:
        """Clean text to improve language detection accuracy."""
        # Remove timestamps, URLs, and common YouTube artifacts
        text = re.sub(r'\d{1,2}:\d{2}(?::\d{2})?', '', text)  # Remove timestamps
        text = re.sub(r'https?://[^\s]+', '', text)  # Remove URLs
        text = re.sub(r'\[.*?\]', '', text)  # Remove bracketed content
        text = re.sub(r'[<>]', '', text)  # Remove angle brackets

        return text.strip()

    def _normalize_language_code(self, lang_code: str) -> str:
        """Normalize language codes to supported formats."""
        # Map various Chinese language codes to zh-cn
        chinese_codes = ['zh', 'zh-cn', 'zh-tw', 'zh-hans', 'zh-hant']
        if lang_code.lower() in chinese_codes:
            return 'zh-cn'  # Default to simplified Chinese

        return lang_code.lower()

    def _heuristic_language_detection(self, text: str) -> str:
        """Simple heuristic-based language detection."""
        if not text:
            return 'en'

        # Count Chinese characters
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text)

        if total_chars > 0:
            chinese_ratio = chinese_chars / total_chars
            if chinese_ratio > 0.1:  # If >10% Chinese characters
                return 'zh-cn'

        return 'en'  # Default to English

class TranscriptExtractor:
    """Main transcript extraction class."""

    def __init__(self):
        """Initialize transcript extractor."""
        self.language_detector = LanguageDetector()

        if not YOUTUBE_TRANSCRIPT_AVAILABLE:
            logger.warning("youtube-transcript-api not available")

        if not YT_DLP_AVAILABLE:
            logger.warning("yt_dlp not available - audio fallback disabled")

    def extract_video_id(self, url: str) -> str:
        """
        Extract video ID from YouTube URL.

        Args:
            url: YouTube URL

        Returns:
            Video ID string

        Raises:
            TranscriptError: If URL is invalid or video ID cannot be extracted
        """
        try:
            parsed_url = urlparse(url)
            video_id = None

            if 'youtu.be' in parsed_url.netloc:
                video_id = parsed_url.path[1:]
            elif 'youtube.com' in parsed_url.netloc or 'youtube-nocookie.com' in parsed_url.netloc:
                if '/embed/' in parsed_url.path:
                    video_id = parsed_url.path.split('/embed/')[-1]
                else:
                    query_params = parse_qs(parsed_url.query)
                    video_id = query_params.get('v', [None])[0]

            if not video_id:
                raise TranscriptError("Could not extract video ID from URL")

            # Clean up video ID (remove additional parameters)
            video_id = video_id.split('&')[0].split('?')[0]

            if len(video_id) != 11:
                raise TranscriptError(f"Invalid video ID format: {video_id}")

            return video_id

        except Exception as e:
            raise TranscriptError(f"Failed to extract video ID: {str(e)}")

    async def extract_transcript(self, url: str) -> Tuple[str, str]:
        """
        Extract transcript from YouTube video.

        Args:
            url: YouTube video URL

        Returns:
            Tuple of (transcript_text, detected_language)

        Raises:
            TranscriptError: If transcript cannot be extracted
        """
        video_id = self.extract_video_id(url)
        logger.info(f"Extracting transcript for video ID: {video_id}")

        # Try official subtitles first
        transcript_text = await self._try_official_subtitles(video_id)
        if transcript_text:
            language = self.language_detector.detect_language(transcript_text)
            logger.info(f"✅ Extracted official transcript ({len(transcript_text)} chars, language: {language})")
            return transcript_text, language

        # Try audio fallback if available
        if YT_DLP_AVAILABLE:
            transcript_text = await self._try_audio_transcription(video_id)
            if transcript_text:
                language = self.language_detector.detect_language(transcript_text)
                logger.info(f"✅ Extracted audio transcript ({len(transcript_text)} chars, language: {language})")
                return transcript_text, language

        raise TranscriptError(
            f"No transcript available for video {video_id}. "
            "Video may have disabled subtitles and audio extraction failed."
        )

    async def _try_official_subtitles(self, video_id: str) -> Optional[str]:
        """Try to extract official YouTube subtitles."""
        if not YOUTUBE_TRANSCRIPT_AVAILABLE:
            return None

        def _fetch_transcript():
            try:
                api = YouTubeTranscriptApi()
                transcript_list = api.list(video_id)
                
                # Try to find a transcript in the preferred languages
                try:
                    transcript = transcript_list.find_transcript(['en', 'zh-cn', 'zh-tw', 'ja', 'ko', 'es', 'fr', 'de'])
                    return transcript.fetch()
                except NoTranscriptFound:
                    # If not found, try to find a manually created one in any of those languages
                    try:
                        transcript = transcript_list.find_manually_created_transcript(['en', 'zh-cn', 'zh-tw', 'ja', 'ko', 'es', 'fr', 'de'])
                        return transcript.fetch()
                    except NoTranscriptFound:
                        # If still not found, get the first available transcript
                        for transcript in transcript_list:
                            return transcript.fetch()
                        return None

            except (TranscriptsDisabled, NoTranscriptFound):
                # Let the outer try/except handle these
                raise
            except Exception as e:
                logger.warning(f"Unhandled error in transcript fetching thread: {e}")
                return None

        try:
            transcript_data = await asyncio.get_event_loop().run_in_executor(
                None, _fetch_transcript
            )
            if transcript_data:
                return self._format_transcript(transcript_data)

        except TranscriptsDisabled:
            logger.info("Subtitles are disabled for this video")
        except NoTranscriptFound:
            logger.info("No transcript found for this video")
        except Exception as e:
            logger.warning(f"Error extracting official subtitles: {e}")

        return None

    async def _try_audio_transcription(self, video_id: str) -> Optional[str]:
        """Try to extract transcript from audio using yt_dlp + Gemini."""
        if not YT_DLP_AVAILABLE:
            return None

        try:
            logger.info("Attempting audio transcription...")

            # This would require integration with a speech-to-text service
            # For now, we'll return None and let the main processor handle this
            # In a full implementation, you would:
            # 1. Use yt_dlp to download audio
            # 2. Use a speech-to-text service (like Google Speech-to-Text or OpenAI Whisper)
            # 3. Return the transcribed text

            logger.warning("Audio transcription not yet implemented")
            return None

        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            return None

    def _format_transcript(self, transcript_data: list) -> str:
        """Format raw transcript data into readable text."""
        if not transcript_data:
            return ""

        # Combine transcript segments
        segments = []
        for segment in transcript_data:
            text = segment.text.strip()
            if text:
                segments.append(text)

        # Join and clean up
        full_text = ' '.join(segments)
        full_text = re.sub(r'\s+', ' ', full_text)  # Normalize whitespace
        full_text = full_text.strip()

        return full_text

    async def download_thumbnail(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Download video thumbnail.

        Args:
            url: YouTube video URL

        Returns:
            Tuple of (video_title, local_thumbnail_path)
        """
        video_id = self.extract_video_id(url)

        try:
            if YT_DLP_AVAILABLE:
                return await self._download_with_yt_dlp(video_id)
            else:
                logger.warning("yt_dlp not available for thumbnail download")
                return None, None

        except Exception as e:
            logger.error(f"Thumbnail download failed: {e}")
            return None, None

    async def _download_with_yt_dlp(self, video_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Download thumbnail using yt_dlp."""
        try:
            def _sync_download():
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
                    return info.get('title'), info.get('thumbnail')

            video_title, thumbnail_url = await asyncio.get_event_loop().run_in_executor(None, _sync_download)

            if thumbnail_url:
                # Download thumbnail to local directory
                import urllib.request
                config = _get_config()
                thumbnail_path = config.thumbnails_dir / f'{video_id}.jpg'

                urllib.request.urlretrieve(thumbnail_url, thumbnail_path)
                logger.info(f"✅ Downloaded thumbnail: {thumbnail_path}")

                return video_title, str(thumbnail_path)

        except Exception as e:
            logger.error(f"yt_dlp thumbnail download failed: {e}")

        return None, None

# Convenience functions
async def extract_transcript(url: str) -> Tuple[str, str]:
    """Extract transcript and language from YouTube URL."""
    extractor = TranscriptExtractor()
    return await extractor.extract_transcript(url)

async def download_thumbnail(url: str) -> Tuple[Optional[str], Optional[str]]:
    """Download video thumbnail."""
    extractor = TranscriptExtractor()
    return await extractor.download_thumbnail(url)

def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    extractor = TranscriptExtractor()
    return extractor.extract_video_id(url)
