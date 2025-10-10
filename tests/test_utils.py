import pytest
from myapp.main import extract_video_id

class TestExtractVideoId:
    """Test cases for extract_video_id function."""

    def test_standard_youtube_url(self):
        """Test standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_youtube_url_with_params(self):
        """Test YouTube URL with additional parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_youtube_url_with_playlist(self):
        """Test YouTube URL with playlist parameter."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmRdnEQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_youtu_be_url(self):
        """Test youtu.be shortened URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_youtu_be_url_with_params(self):
        """Test youtu.be URL with parameters."""
        url = "https://youtu.be/dQw4w9WgXcQ?t=30"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_embed_url(self):
        """Test embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_invalid_url_no_video_id(self):
        """Test URL without video ID."""
        url = "https://www.youtube.com/watch"
        with pytest.raises(ValueError, match="Could not extract video ID from URL"):
            extract_video_id(url)

    def test_invalid_url_not_youtube(self):
        """Test non-YouTube URL."""
        url = "https://example.com/video?v=abc123"
        with pytest.raises(ValueError, match="Could not extract video ID from URL"):
            extract_video_id(url)

    def test_malformed_url(self):
        """Test malformed URL."""
        url = "not-a-url-at-all"
        with pytest.raises(ValueError, match="Could not extract video ID from URL"):
            extract_video_id(url)
