# SparkPelican User Guide

## Overview

SparkPelican is an AI-powered blog post generation system that automatically creates blog posts from YouTube videos. It combines YouTube transcript extraction, AI content generation, and Pelican static site generation to create a seamless content creation workflow.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Quick Start](#quick-start)
5. [Usage Methods](#usage-methods)
6. [API Endpoints](#api-endpoints)
7. [Development](#development)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

Before using SparkPelican, ensure you have:

- **Python 3.8+** installed
- **Node.js and npm** for CSS building (Tailwind CSS)
- **Git** for version control
- **Google Gemini API Key** for AI content generation

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yoloinfinity55/sparkpelican.git
cd sparkpelican
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Node.js Dependencies

```bash
npm install
```

### 4. Set Environment Variables

Create a `.env` file or set the environment variable:

```bash
export GEMINI_API_KEY="your_google_gemini_api_key_here"
```

## Configuration

### Pelican Configuration

The main configuration is in `pelicanconf.py`:

```python
AUTHOR = 'Infinity Spark'
SITENAME = 'sparkpelican'
THEME = 'themes/sparkpelican-theme'
TIMEZONE = 'America/Toronto'
```

### API Configuration

The FastAPI backend runs on port 8001 by default. CORS is configured for:
- `http://localhost:8000`
- `http://localhost:3000`

## Quick Start

### Method 1: Using the Command Line Script

Generate a blog post from a YouTube video:

```bash
python process_youtube_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Method 2: Using Invoke Tasks

```bash
# Generate a post using the API task
invoke api-generate --youtube-url="https://www.youtube.com/watch?v=VIDEO_ID"

# Build the site
invoke build

# Serve locally
invoke serve
```

### Method 3: Using the FastAPI Server

```bash
# Start the API server
invoke api-server

# In another terminal, make a POST request
curl -X POST "http://localhost:8001/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "category": "Technology",
    "tags": ["AI", "Tutorial"]
  }'
```

## Usage Methods

### Command Line Script (`process_youtube_video.py`)

**Basic Usage:**
```bash
python process_youtube_video.py "YOUTUBE_URL"
```

**Features:**
- Extracts YouTube transcript
- Generates AI content using Gemini
- Saves markdown file to `content/posts/`
- Automatic title and slug generation

### Invoke Tasks (`tasks.py`)

**Post Generation:**
```bash
invoke api-generate --youtube-url="URL" --title="Custom Title" --category="Tech" --tags="AI,Machine Learning"
```

**Site Management:**
```bash
invoke build          # Build the site
invoke serve          # Serve locally on port 8001
invoke preview        # Build for production
invoke clean          # Remove generated files
```

**Validation:**
```bash
invoke validate-titles                    # Check title formatting
invoke api-validate-posts                 # Validate API compatibility
invoke api-validate-posts --fix           # Auto-fix title issues
```

### FastAPI Server

**Start the server:**
```bash
invoke api-server --host=0.0.0.0 --port=8001 --reload
```

**Available endpoints:**
- `GET /health` - Health check
- `POST /generate` - Generate post from YouTube URL
- `POST /validate` - Validate front matter
- `GET /docs` - Interactive API documentation

## API Endpoints

### Generate Post

**Endpoint:** `POST /generate`

**Request Body:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "custom_title": "Optional custom title",
  "category": "General",
  "tags": ["tag1", "tag2"]
}
```

**Response:**
```json
{
  "status": "processing",
  "post_id": null,
  "message": "Post generation started in background"
}
```

### Validate Front Matter

**Endpoint:** `POST /validate`

**Request Body:**
```json
{
  "front_matter": {
    "title": "Post Title",
    "date": "2024-01-01T00:00:00",
    "author": "Author Name"
  }
}
```

**Response:**
```json
{
  "valid": true,
  "issues": []
}
```

## Development

### Project Structure

```
sparkpelican/
├── content/                 # Pelican content directory
│   ├── pages/              # Static pages
│   └── posts/              # Blog posts (markdown files)
├── myapp/                  # FastAPI application
│   ├── main.py            # API server
│   ├── ai_generator.py    # AI content generation
│   ├── youtube_transcript.py  # YouTube integration
│   └── pelican_integrator.py  # Pelican integration
├── themes/                 # Pelican themes
│   └── sparkpelican-theme/    # Custom theme
├── scripts/                # Utility scripts
├── output/                 # Generated site (after build)
└── tasks.py               # Invoke tasks
```

### CSS Development

**Build CSS:**
```bash
npm run build:css
```

**Watch for changes:**
```bash
npm run watch:css
```

### Adding New Features

1. **New API Endpoints:** Add to `myapp/main.py`
2. **Content Processing:** Modify `myapp/ai_generator.py` or `myapp/youtube_transcript.py`
3. **Pelican Integration:** Update `myapp/pelican_integrator.py`
4. **Tasks:** Add new tasks to `tasks.py`

## Deployment

### Local Development Server

```bash
# Serve with live reload
invoke livereload

# Basic serving
invoke reserve  # Builds and serves
```

### Production Build

```bash
# Build for production
invoke preview

# Deploy to GitHub Pages
invoke gh-pages
```

### Custom Deployment

For custom deployment, modify the `publish` task in `tasks.py`:

```bash
invoke publish  # Uses rsync by default
```

## Troubleshooting

### Common Issues

**1. "GEMINI_API_KEY not set"**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**2. "Title validation failed"**
```bash
invoke api-validate-posts --fix  # Auto-fix title formatting
```

**3. "YouTube transcript not available"**
- Ensure the video has captions/subtitles
- Check if the video is publicly accessible
- Try a different video URL

**4. "Port already in use"**
```bash
# Kill process using port 8001
lsof -ti:8001 | xargs kill -9

# Or use different port
invoke api-server --port=8002
```

### Logs and Debugging

**API Server Logs:**
```bash
invoke api-server --reload  # Shows detailed logs
```

**Pelican Build Logs:**
```bash
invoke build  # Check for any build errors
```

**Title Validation:**
```bash
invoke validate-titles  # Detailed title validation output
```

### Getting Help

1. Check the API documentation: `http://localhost:8001/docs`
2. Review the generated markdown files in `content/posts/`
3. Check the Pelican settings in `pelicanconf.py`
4. Validate your environment variables

## Advanced Usage

### Custom AI Prompts

Modify `myapp/ai_generator.py` to customize the AI generation prompts:

```python
# In ai_generator.py
custom_prompt = f"""
Generate a blog post based on this transcript: {transcript}
Style: Technical tutorial
Length: 800-1200 words
"""
```

### Custom Post Processing

Add post-processing logic in `myapp/pelican_integrator.py`:

```python
# In pelican_integrator.py
def custom_post_processing(post_data):
    # Add custom processing here
    return post_data
```

### Batch Processing

Process multiple videos:

```python
# Create a batch script
videos = [
    "https://youtube.com/watch?v=video1",
    "https://youtube.com/watch?v=video2"
]

for video_url in videos:
    python process_youtube_video.py "{video_url}"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the SparkPelican ecosystem. Check the repository for specific license information.

---

For more information, visit the [GitHub repository](https://github.com/yoloinfinity55/sparkpelican).
