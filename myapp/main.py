#!/usr/bin/env python3
"""
FastAPI Backend for SparkPelican

This FastAPI application provides AI-powered blog post generation from YouTube videos,
with real-time validation and background processing capabilities.

Endpoints:
- POST /generate: Generate blog post from YouTube URL
- POST /validate: Validate post front matter
- GET /health: Health check endpoint
"""

import asyncio
from pathlib import Path
import re
import yaml
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse

# Import FastAPI components directly from the library
from myapp import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import uvicorn

from .youtube_transcript import get_transcript_async
from .ai_generator import generate_post_async
from .pelican_integrator import save_markdown_post

# Application configuration
CONTENT_DIR = Path("content/posts")
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="SparkPelican API",
    description="AI-powered blog post generation API for SparkPelican",
    version="1.0.0"
)

# CORS middleware for web UI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class YouTubeURL(BaseModel):
    """YouTube URL input model."""
    url: str = Field(..., description="YouTube video URL to process")

    @field_validator('url')
    @classmethod
    def validate_youtube_url(cls, v):
        """Validate YouTube URL format."""
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        if not youtube_regex.match(v):
            raise ValueError('Invalid YouTube URL')
        return v

class GenerateRequest(BaseModel):
    """Blog post generation request."""
    youtube_url: str = Field(..., description="YouTube video URL")
    custom_title: Optional[str] = Field(None, description="Custom title (optional)")
    category: str = Field("General", description="Post category")
    tags: List[str] = Field(default_factory=list, description="Post tags")

class GenerateResponse(BaseModel):
    """Generation response."""
    status: str = Field(..., description="Generation status")
    post_id: Optional[str] = Field(None, description="Generated post filename")
    message: str = Field(..., description="Status message")

class ValidateRequest(BaseModel):
    """Front matter validation request."""
    front_matter: Dict[str, str] = Field(..., description="YAML front matter to validate")

class ValidateResponse(BaseModel):
    """Validation response."""
    valid: bool = Field(..., description="Validation result")
    issues: List[str] = Field(default_factory=list, description="Validation issues")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "sparkpelican-api"}

@app.post("/generate", response_model=GenerateResponse)
async def generate_post(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a blog post from YouTube video.

    - Extracts transcript
    - Generates AI content
    - Saves to content/posts/ directory
    """
    try:
        # Extract video ID
        video_id = extract_video_id(request.youtube_url)

        # Add background task for processing
        background_tasks.add_task(
            process_video_generation,
            video_id=video_id,
            youtube_url=request.youtube_url,
            custom_title=request.custom_title,
            category=request.category,
            tags=request.tags
        )

        return GenerateResponse(
            status="processing",
            post_id=None,
            message="Post generation started in background"
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Generation failed: {str(e)}")

@app.post("/validate", response_model=ValidateResponse)
async def validate_front_matter(request: ValidateRequest):
    """Validate YAML front matter for a blog post."""
    issues = []

    front_matter = request.front_matter

    # Required fields
    required_fields = ["title", "date", "author"]
    for field in required_fields:
        if field not in front_matter:
            issues.append(f"Missing required field: {field}")

    # Title validation
    if "title" in front_matter and isinstance(front_matter["title"], str):
        title = front_matter["title"].strip()
        if not title:
            issues.append("Title cannot be empty")
        elif title.startswith('"') and title.endswith('"'):
            issues.append("Title should not have quotes around it")

    # Date validation
    if "date" in front_matter:
        try:
            datetime.fromisoformat(front_matter["date"])
        except ValueError:
            issues.append("Date must be in ISO format (YYYY-MM-DDTHH:MM:SS)")

    # Author validation
    if "author" in front_matter and not front_matter["author"].strip():
        issues.append("Author cannot be empty")

    # Slug validation (auto-generated if missing)
    if "slug" not in front_matter and "title" in front_matter:
        # Generate slug from title if missing
        pass

    return ValidateResponse(
        valid=len(issues) == 0,
        issues=issues
    )

async def process_video_generation(
    video_id: str,
    youtube_url: str,
    custom_title: Optional[str],
    category: str,
    tags: List[str]
):
    """Background task to process video and generate post."""
    try:
        # Step 1: Get transcript
        transcript = await get_transcript_async(youtube_url)

        # Step 2: Generate AI content
        post_data = await generate_post_async(
            transcript=transcript,
            video_id=video_id,
            custom_title=custom_title,
            category=category,
            tags=tags
        )

        # Step 3: Save to Pelican content directory
        await save_markdown_post(post_data, CONTENT_DIR)

        print(f"✅ Post generated successfully for video {video_id}")

    except Exception as e:
        print(f"❌ Error generating post for {video_id}: {str(e)}")

def extract_video_id(youtube_url: str) -> str:
    """Extract video ID from YouTube URL."""
    parsed_url = urlparse(youtube_url)
    video_id = None

    if 'youtu.be' in parsed_url.netloc:
        video_id = parsed_url.path[1:]
    elif 'youtube.com' in parsed_url.netloc:
        if '/embed/' in parsed_url.path:
            # Handle embed URLs like /embed/dQw4w9WgXcQ
            video_id = parsed_url.path.split('/embed/')[-1]
        else:
            # Handle regular URLs with query parameters
            query_params = dict(param.split('=') for param in parsed_url.query.split('&') if '=' in param)
            video_id = query_params.get('v')

    if not video_id:
        raise ValueError("Could not extract video ID from URL")

    return video_id

if __name__ == "__main__":
    uvicorn.run(
        "myapp.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
