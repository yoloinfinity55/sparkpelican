---
title: Complete Guide to Using SparkPelican: AI-Powered Blog Post Generation
date: 2025-10-15T06:37:00.000Z
layout: post.njk
description: >-
  Learn how to use SparkPelican to automatically generate blog posts from YouTube videos using AI. This comprehensive guide covers installation, configuration, and all usage methods.
author: "Infinity Spark"
readingTime: "15 min read"
tags: ["AI", "Pelican", "YouTube", "Automation", "Tutorial"]
---

# Complete Guide to Using SparkPelican: AI-Powered Blog Post Generation

SparkPelican is an innovative AI-powered blog post generation system that automatically creates blog posts from YouTube videos. It combines YouTube transcript extraction, AI content generation, and Pelican static site generation to create a seamless content creation workflow.

## What Makes SparkPelican Special?

SparkPelican revolutionizes content creation by:
- **Automatically extracting transcripts** from YouTube videos
- **Using Google Gemini AI** to generate high-quality blog posts
- **Seamlessly integrating** with Pelican static site generator
- **Providing multiple usage methods** for different workflows
- **Including built-in validation** and quality checks

## Prerequisites

Before getting started with SparkPelican, ensure you have:

- **Python 3.8+** installed on your system
- **Node.js and npm** for CSS building (Tailwind CSS)
- **Git** for version control
- **Google Gemini API Key** for AI content generation

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yoloinfinity55/sparkpelican.git
cd sparkpelican
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Node.js Dependencies

```bash
npm install
```

### Step 4: Set Environment Variables

```bash
export GEMINI_API_KEY="your_google_gemini_api_key_here"
```

## Quick Start

### Method 1: Command Line Script (Easiest)

Generate a blog post from any YouTube video with a single command:

```bash
python process_youtube_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

This script will:
1. Extract the transcript from the YouTube video
2. Generate AI content using Gemini
3. Save a properly formatted markdown file to `content/posts/`

### Method 2: Using Invoke Tasks (Recommended)

For more control and additional features:

```bash
# Generate a post with custom options
invoke api-generate --youtube-url="https://www.youtube.com/watch?v=VIDEO_ID" --title="Custom Title" --category="Technology" --tags="AI,Tutorial"

# Build the site
invoke build

# Serve locally
invoke serve
```

### Method 3: FastAPI Server (For Integration)

Start the API server for web-based usage:

```bash
invoke api-server
```

Then make POST requests to `http://localhost:8001/generate` with your YouTube URL.

## Understanding the Architecture

SparkPelican consists of several key components:

### Core Components

**FastAPI Backend** (`myapp/main.py`)
- REST API server with endpoints for post generation and validation
- Background processing for video content
- CORS middleware for web integration

**Pelican Integration** (`pelicanconf.py`)
- Static site generator configuration
- Custom theme integration
- Feed and pagination settings

**Task Automation** (`tasks.py`)
- Invoke-based command system
- Build, serve, and deployment tasks
- Title validation and fixing

## Usage Methods in Detail

### Command Line Script

The `process_youtube_video.py` script provides the simplest entry point:

```bash
python process_youtube_video.py "YOUTUBE_URL"
```

**Features:**
- Automatic transcript extraction
- AI content generation with Gemini
- Markdown file creation in `content/posts/`
- Automatic title and slug generation
- Error handling and logging

### Invoke Tasks

The `tasks.py` file provides a comprehensive task system:

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

**Quality Assurance:**
```bash
invoke validate-titles                    # Check title formatting
invoke api-validate-posts                 # Validate API compatibility
invoke api-validate-posts --fix           # Auto-fix title issues
```

### FastAPI Server

For programmatic access or web integration:

```bash
invoke api-server --host=0.0.0.0 --port=8001 --reload
```

**Available endpoints:**
- `GET /health` - Health check
- `POST /generate` - Generate post from YouTube URL
- `POST /validate` - Validate front matter
- `GET /docs` - Interactive API documentation

## API Integration Examples

### Generate Post via API

```bash
curl -X POST "http://localhost:8001/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "custom_title": "Optional custom title",
    "category": "Technology",
    "tags": ["AI", "Tutorial"]
  }'
```

### Validate Front Matter

```bash
curl -X POST "http://localhost:8001/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "front_matter": {
      "title": "Post Title",
      "date": "2024-01-01T00:00:00",
      "author": "Author Name"
    }
  }'
```

## Development Workflow

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
│   └── sparkpelican-theme/    # Custom theme with Tailwind CSS
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

### Customizing AI Generation

You can modify the AI prompts in `myapp/ai_generator.py`:

```python
# Customize the generation prompt
custom_prompt = f"""
Generate a blog post based on this transcript: {transcript}
Style: Technical tutorial
Length: 800-1200 words
Include code examples and practical steps
"""
```

## Deployment Options

### Development Server

```bash
# Live reload development
invoke livereload

# Basic development serving
invoke reserve  # Builds and serves
```

### Production Deployment

```bash
# Build for production
invoke preview

# Deploy to GitHub Pages
invoke gh-pages

# Custom deployment (modify tasks.py for your needs)
invoke publish
```

## Troubleshooting Common Issues

### 1. Missing API Key

**Error:** "GEMINI_API_KEY not set"
**Solution:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

### 2. Title Validation Errors

**Error:** "Title validation failed"
**Solution:**
```bash
invoke api-validate-posts --fix  # Auto-fix title formatting
```

### 3. YouTube Transcript Issues

**Error:** "YouTube transcript not available"
**Solutions:**
- Ensure the video has captions/subtitles enabled
- Check if the video is publicly accessible
- Try a different video URL
- Verify the video ID is correct

### 4. Port Conflicts

**Error:** "Port already in use"
**Solution:**
```bash
# Kill process using port 8001
lsof -ti:8001 | xargs kill -9

# Or use different port
invoke api-server --port=8002
```

## Advanced Usage

### Batch Processing Multiple Videos

Create a script to process multiple videos:

```python
import asyncio
from process_youtube_video import process_youtube_video

videos = [
    "https://youtube.com/watch?v=video1",
    "https://youtube.com/watch?v=video2",
    "https://youtube.com/watch?v=video3"
]

async def batch_process():
    for video_url in videos:
        success = await process_youtube_video(video_url)
        if success:
            print(f"✅ Processed: {video_url}")
        else:
            print(f"❌ Failed: {video_url}")

asyncio.run(batch_process())
```

### Custom Post Processing

Add custom logic in `myapp/pelican_integrator.py`:

```python
def custom_post_processing(post_data):
    # Add SEO metadata
    post_data['seo_description'] = generate_seo_description(post_data['content'])
    # Add reading time calculation
    post_data['reading_time'] = calculate_reading_time(post_data['content'])
    return post_data
```

### Integration with External Tools

SparkPelican's API can be integrated with:
- **Content management systems**
- **Social media automation tools**
- **Custom web applications**
- **CI/CD pipelines**

## Best Practices

### Content Quality
1. **Choose videos with clear audio** and good captions
2. **Review generated content** before publishing
3. **Customize AI prompts** for your specific use case
4. **Use descriptive titles** and proper tagging

### Performance
1. **Use background processing** for large batches
2. **Monitor API rate limits** for Gemini API
3. **Cache transcripts** when possible
4. **Batch similar operations** together

### Maintenance
1. **Regularly update dependencies**
2. **Monitor for API changes** in YouTube and Gemini
3. **Backup your content** regularly
4. **Keep your API keys secure**

## Getting Help

### Documentation
- **API Documentation:** `http://localhost:8001/docs`
- **Project Repository:** [GitHub](https://github.com/yoloinfinity55/sparkpelican)
- **Pelican Documentation:** [Official Site](https://docs.getpelican.com/)

### Community Support
- Check existing blog posts in `content/posts/`
- Review configuration files for examples
- Test with sample videos first

## Contributing

SparkPelican is an open-source project. Contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Test thoroughly
5. Submit a pull request

## Conclusion

SparkPelican provides a powerful yet easy-to-use solution for AI-powered content generation. Whether you're a developer looking to automate your blog workflow or a content creator wanting to leverage AI for post generation, SparkPelican offers the flexibility and features you need.

Start with the simple command-line script for immediate results, then explore the API and task system for more advanced workflows. The combination of YouTube transcript extraction, AI content generation, and Pelican integration makes SparkPelican a unique and valuable tool in the modern content creation landscape.

---

*This guide was automatically generated using SparkPelican's AI-powered content generation system. For more information about SparkPelican, visit the [GitHub repository](https://github.com/yoloinfinity55/sparkpelican).*
