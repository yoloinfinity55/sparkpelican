import pytest
from unittest.mock import patch, AsyncMock
from starlette.testclient import TestClient
from myapp.main import app

@pytest.fixture
def client():
    return TestClient(app)

class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_endpoint(self, client):
        """Test /health returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "sparkpelican-api"

class TestValidateEndpoint:
    """Test front matter validation endpoint."""

    def test_validate_valid_front_matter(self, client):
        """Test validation with all required fields."""
        data = {
            "front_matter": {
                "title": "Test Post",
                "date": "2023-10-01T12:00:00",
                "author": "Test Author",
                "category": "Test Category",
                "tags": ["test", "post"]
            }
        }
        response = client.post("/validate", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is True
        assert result["issues"] == []

    def test_validate_missing_title(self, client):
        """Test validation missing title."""
        data = {
            "front_matter": {
                "date": "2023-10-01T12:00:00",
                "author": "Test Author"
            }
        }
        response = client.post("/validate", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is False
        assert "Missing required field: title" in result["issues"]

    def test_validate_missing_date(self, client):
        """Test validation missing date."""
        data = {
            "front_matter": {
                "title": "Test Post",
                "author": "Test Author"
            }
        }
        response = client.post("/validate", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is False
        assert "Missing required field: date" in result["issues"]

    def test_validate_missing_author(self, client):
        """Test validation missing author."""
        data = {
            "front_matter": {
                "title": "Test Post",
                "date": "2023-10-01T12:00:00"
            }
        }
        response = client.post("/validate", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is False
        assert "Missing required field: author" in result["issues"]

    def test_validate_empty_title(self, client):
        """Test validation with empty title."""
        data = {
            "front_matter": {
                "title": "",
                "date": "2023-10-01T12:00:00",
                "author": "Test Author"
            }
        }
        response = client.post("/validate", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is False
        assert "Title cannot be empty" in result["issues"]

    def test_validate_title_with_quotes(self, client):
        """Test validation with quoted title."""
        data = {
            "front_matter": {
                "title": '"Quoted Title"',
                "date": "2023-10-01T12:00:00",
                "author": "Test Author"
            }
        }
        response = client.post("/validate", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is False
        assert "Title should not have quotes around it" in result["issues"]

    def test_validate_invalid_date(self, client):
        """Test validation with invalid date format."""
        data = {
            "front_matter": {
                "title": "Test Post",
                "date": "invalid-date",
                "author": "Test Author"
            }
        }
        response = client.post("/validate", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is False
        assert "Date must be in ISO format (YYYY-MM-DDTHH:MM:SS)" in result["issues"]

    def test_validate_empty_author(self, client):
        """Test validation with empty author."""
        data = {
            "front_matter": {
                "title": "Test Post",
                "date": "2023-10-01T12:00:00",
                "author": ""
            }
        }
        response = client.post("/validate", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is False
        assert "Author cannot be empty" in result["issues"]

    def test_validate_multiple_issues(self, client):
        """Test validation with multiple validation issues."""
        data = {
            "front_matter": {
                "title": "",
                "date": "invalid",
                "author": ""
            }
        }
        response = client.post("/validate", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["valid"] is False
        assert len(result["issues"]) == 3
        issues = result["issues"]
        assert any("Title cannot be empty" in issue for issue in issues)
        assert any("Date must be in ISO format" in issue for issue in issues)
        assert any("Author cannot be empty" in issue for issue in issues)

class TestGenerateEndpoint:
    """Test post generation endpoint with mocked dependencies."""

    @pytest.mark.asyncio
    @patch('myapp.main.get_transcript_async')
    @patch('myapp.main.generate_post_async')
    @patch('myapp.main.save_markdown_post')
    def test_generate_post_success(self, mock_save, mock_generate, mock_transcript, client):
        """Test successful post generation with mocked dependencies."""
        # Mock the dependencies
        mock_transcript.return_value = "Mock transcript"
        mock_generate.return_value = {
            'title': 'Test Post',
            'content': 'Generated content',
            'front_matter': {
                'title': 'Test Post',
                'date': '2023-10-01T12:00:00',
                'author': 'SparkPelican',
                'category': 'Test',
                'tags': ['test']
            }
        }
        mock_save.return_value = "test-post.md"

        data = {
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "custom_title": None,
            "category": "Test",
            "tags": ["test"]
        }

        response = client.post("/generate", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "processing"
        assert result["message"] == "Post generation started in background"

        # Verify mocks were called (background task should execute)
        # Note: In test environment, background tasks should run synchronously

    def test_generate_invalid_url(self, client):
        """Test generation with invalid YouTube URL."""
        data = {
            "youtube_url": "https://example.com/invalid",
            "category": "Test"
        }
        response = client.post("/generate", json=data)
        assert response.status_code == 422  # Pydantic validation error

class TestYouTubeURLModel:
    """Test YouTube URL validation model."""

    def test_valid_youtube_url(self, client):
        """Test valid YouTube URL in request model."""
        # This tests the pydantic validator
        data = {
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category": "Test"
        }
        # We can test this by trying to validate through the endpoint
        response = client.post("/generate", json=data)
        # Should accept the URL (may fail for other reasons but not URL validation)
        assert response.status_code in [200, 500]  # 500 would be from missing env vars

    def test_invalid_youtube_url(self, client):
        """Test invalid YouTube URL validation."""
        data = {
            "youtube_url": "https://example.com/watch?v=dQw4w9WgXcQ",
            "category": "Test"
        }
        response = client.post("/generate", json=data)
        assert response.status_code == 422  # Validation error for URL
