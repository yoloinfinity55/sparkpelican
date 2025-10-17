---
title: Complete Guide - How to Create New Blog Posts in SparkPelican
date: 2025-10-17T10:00:00.000Z
layout: post.njk
description: >-
  Learn all the methods for creating blog posts in SparkPelican, from simple command-line scripts to API integration and manual creation. This comprehensive guide covers every approach.
author: "Infinity Spark"
readingTime: "8 min read"
tags: ["Tutorial", "Blogging", "Pelican", "Content Creation", "Guide"]
---

# Complete Guide: How to Create New Blog Posts in SparkPelican

Creating blog posts in SparkPelican is straightforward and flexible, with multiple methods to suit different workflows. Whether you prefer simple command-line scripts, powerful task automation, API integration, or manual control, SparkPelican has you covered.

## Method 1: Command Line Script (Easiest)

### Step 1: Basic Usage
```bash
python process_youtube_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Step 2: Verify the post was created
- Check `content/posts/` directory for the new `.md` file
- The file will have front matter with title, date, author, and tags

**Example output:**
```
🔄 Processing YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ
📹 Video ID: dQw4w9WgXcQ
📝 Extracting transcript...
✅ Transcript extracted (2847 characters)
🤖 Generating blog post...
✅ Blog post generated
💾 Post saved to: 2025-10-17-never-gonna-give-you-up.md
🎉 Video processing completed successfully!
```

## Method 2: Invoke Tasks (Recommended)

### Step 1: Generate post with custom options
```bash
invoke api-generate --youtube-url="https://www.youtube.com/watch?v=VIDEO_ID" --title="Custom Title" --category="Technology" --tags="AI,Tutorial"
```

**Available parameters:**
- `--youtube-url`: The YouTube video URL (required)
- `--title`: Custom title for the post (optional)
- `--category`: Post category (default: "General")
- `--tags`: Comma-separated list of tags (optional)

### Step 2: Build the site to include your new post
```bash
invoke build
```

### Step 3: Preview your changes locally
```bash
invoke serve
```

**Example with custom options:**
```bash
invoke api-generate \
  --youtube-url="https://www.youtube.com/watch?v=VIDEO_ID" \
  --title="Advanced AI Tutorial" \
  --category="Technology" \
  --tags="AI,Machine Learning,Python"
```

## Method 3: Manual Creation (Full Control)

### Step 1: Create a new markdown file
Create a file in `content/posts/` with the naming convention: `YYYY-MM-DD-post-title.md`

**Example filename:** `2025-10-17-my-awesome-post.md`

### Step 2: Add front matter metadata
```markdown
---
title: Your Post Title Here
date: 2025-10-17T10:00:00.000Z
layout: post.njk
description: Brief description of your post content
author: "Your Name"
readingTime: "5 min read"
tags: ["Tag1", "Tag2", "Tag3"]
---
```

### Step 3: Write your content
Add your blog post content in markdown format below the front matter.

**Required front matter fields:**
- `title`: The post title
- `date`: Publication date in ISO format
- `layout`: Always `post.njk` for blog posts
- `description`: Brief summary for SEO
- `author`: Author name
- `readingTime`: Estimated reading time
- `tags`: Array of relevant tags

## Method 4: FastAPI Server (For Integration)

### Step 1: Start the API server
```bash
invoke api-server
```

**Server endpoints:**
- Health check: `http://localhost:8001/health`
- Generate post: `http://localhost:8001/generate`
- Validate posts: `http://localhost:8001/validate`
- API documentation: `http://localhost:8001/docs`

### Step 2: Generate post via API
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

**API response:**
```json
{
  "message": "Post generated successfully",
  "filename": "2025-10-17-post-title.md",
  "title": "Generated Post Title",
  "category": "Technology",
  "tags": ["AI", "Tutorial"]
}
```

## Quality Assurance Steps

### Step 1: Validate titles
```bash
invoke validate-titles
```

**What it checks:**
- No quotes in titles
- Proper formatting
- Consistency across all posts

### Step 2: Fix any title issues (if needed)
```bash
invoke api-validate-posts --fix
```

### Step 3: Validate API compatibility
```bash
invoke api-validate-posts
```

## Environment Setup

### Step 1: Install dependencies
```bash
pip install -r requirements.txt
npm install
```

### Step 2: Set your Gemini API key
```bash
export GEMINI_API_KEY="your_google_gemini_api_key_here"
```

**Verify API key is set:**
```bash
echo $GEMINI_API_KEY
```

## Development Workflow

### Step 1: Generate your post
Choose any method above to create your blog post.

### Step 2: Build and serve locally
```bash
invoke build
invoke serve
```

### Step 3: Preview at http://localhost:8001
Open your browser and navigate to `http://localhost:8001` to see your site with the new post.

### Step 4: Make edits to your post file if needed
- Edit the markdown file directly in `content/posts/`
- Update front matter or content as needed

### Step 5: Rebuild to see changes
```bash
invoke rebuild
```

## Troubleshooting Common Issues

### Problem: "GEMINI_API_KEY not set"
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Verify it's set:**
```bash
echo $GEMINI_API_KEY
# Should show your API key
```

### Problem: Title validation errors
```bash
invoke api-validate-posts --fix
```

**Manual fix process:**
1. Check the error message for specific issues
2. Edit the problematic post files
3. Run validation again

### Problem: Port conflicts
```bash
# Kill process using port 8001
lsof -ti:8001 | xargs kill -9

# Or use different port
invoke api-server --port=8002
```

### Problem: YouTube transcript not available
**Common causes:**
- Video doesn't have captions/subtitles
- Video is private or restricted
- Video ID is incorrect

**Solutions:**
- Choose videos with captions enabled
- Verify the video URL is correct
- Try a different video

## Best Practices

### Content Quality
1. **Choose videos with clear audio** and good captions for better AI generation
2. **Review generated content** before publishing - AI isn't perfect
3. **Use descriptive titles** that clearly indicate the post content
4. **Add relevant tags** to help with organization and SEO

### Performance
1. **Use background processing** for large batches of videos
2. **Monitor API rate limits** for Gemini API (usually 60 requests per minute)
3. **Cache transcripts** when possible to avoid re-processing
4. **Batch similar operations** together

### Workflow Efficiency
1. **Validate titles** before building to catch issues early
2. **Test locally** before deploying to production
3. **Use consistent naming** for post files
4. **Keep front matter** updated and accurate

## Advanced Usage

### Batch Processing Multiple Videos
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

### Custom Post Templates
You can modify the AI generation prompts in `myapp/ai_generator.py`:

```python
# Customize the generation prompt
custom_prompt = f"""
Generate a blog post based on this transcript: {transcript}
Style: Technical tutorial
Length: 800-1200 words
Include code examples and practical steps
Focus on: {category}
"""
```

## File Structure Reference

```
sparkpelican/
├── content/posts/              # Your blog posts live here
│   ├── YYYY-MM-DD-title.md    # Individual post files
│   └── ...
├── pelicanconf.py             # Site configuration
├── tasks.py                   # Available commands
├── process_youtube_video.py   # Simple generation script
├── myapp/                     # FastAPI application
└── requirements.txt           # Python dependencies
```

## Quick Reference Commands

```bash
# Generate post from YouTube
python process_youtube_video.py "YOUTUBE_URL"

# Generate with custom options
invoke api-generate --youtube-url="URL" --title="Title" --tags="tag1,tag2"

# Build site
invoke build

# Serve locally
invoke serve

# Validate posts
invoke validate-titles

# Fix validation issues
invoke api-validate-posts --fix

# Start API server
invoke api-server
```

## Getting Help

### Documentation
- **API Documentation:** `http://localhost:8001/docs`
- **Project Repository:** [GitHub](https://github.com/yoloinfinity55/sparkpelican)
- **Pelican Documentation:** [Official Site](https://docs.getpelican.com/)

### Common Next Steps
1. **Review generated posts** in `content/posts/`
2. **Customize content** as needed
3. **Build and preview** your site
4. **Deploy to production** when ready

This comprehensive guide covers every method for creating blog posts in SparkPelican, from the simplest approaches for beginners to advanced integration options for developers. Choose the method that best fits your workflow and start creating content efficiently!

---

*This guide was created using SparkPelican's AI-powered content generation system. For more information about SparkPelican, visit the [GitHub repository](https://github.com/yoloinfinity55/sparkpelican).*
