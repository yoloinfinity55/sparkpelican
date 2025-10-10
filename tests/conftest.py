import pytest
import asyncio
from pathlib import Path
from starlette.testclient import TestClient

# Import the FastAPI app
from myapp.main import app

@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)

@pytest.fixture
def content_dir(tmp_path):
    """Temporary directory for content testing."""
    content_path = tmp_path / "content" / "posts"
    content_path.mkdir(parents=True, exist_ok=True)
    return content_path

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
