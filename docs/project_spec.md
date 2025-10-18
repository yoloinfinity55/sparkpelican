# 🚀 SparkYouTube AI Blog System — Project Specification (v3.0)

## 📘 Overview
**SparkYouTube AI Blog System** is an intelligent, language-aware automation pipeline that converts YouTube videos into complete, SEO-ready blog posts using **Gemini AI**.

### 🎯 Core Goals
- Automatically extract YouTube subtitles (or audio if none exist)
- Detect transcript language (Chinese or English)
- Generate structured blog content with Gemini AI
- Save posts directly for **Pelican SSG**
- Support both single and batch processing workflows

---

## 🧩 System Architecture

```
youtube-ai-blog/
├── process_youtube_video.py        # Main async processor
├── process_youtube.sh              # Single video runner
├── batch_process_youtube.sh        # Batch runner
│
├── content/
│   └── posts/                      # Generated Pelican posts
│
├── logs/                           # Execution logs
│
├── myapp/
│   ├── youtube_transcript.py       # Transcript + audio fallback
│   ├── ai_generator.py             # Gemini AI integration
│   └── pelican_integrator.py       # Markdown + metadata writer
│
├── youtube_list.txt                # Batch input URLs
└── docs/
    ├── project_spec.md
    └── sop.md
```

---

## ⚙️ Core Modules

### `youtube_transcript.py`
- Extracts subtitles via `youtube-transcript-api`
- Falls back to audio-to-text (if subtitles unavailable)
- Auto-detects language using `langdetect`
- Downloads thumbnail to `content/thumbnails/`

### `ai_generator.py`
- Uses `google-generativeai` (Gemini API)
- Generates posts in detected language (Chinese or English)
- Outputs: title, summary, markdown body, metadata

### `pelican_integrator.py`
- Converts AI output → Pelican-compatible Markdown
- Adds metadata:
  - title, date, tags, category, thumbnail, language
- Saves to `content/posts/YYYY-MM-DD-title.md`

### `process_youtube_video.py`
- Orchestrates the workflow (async/await)
- Handles exceptions, logging, and language control

### `process_youtube.sh`
- Shell wrapper for individual video processing
- Logs output and checks environment setup

### `batch_process_youtube.sh`
- Processes a list of YouTube URLs sequentially
- Delays between runs to avoid API throttling

---

## 🧠 Technology Stack

| Layer | Tool / Library |
|-------|----------------|
| AI Engine | Google Gemini 1.5 Pro |
| Subtitles | youtube-transcript-api |
| Audio Fallback | yt_dlp + Gemini ASR |
| Language Detection | langdetect |
| Blog Format | Pelican Markdown (.md) |
| Control Scripts | Bash + Python (asyncio) |
| Deployment | Pelican → GitHub Pages |

---

## 🔑 Environment Configuration

Before running:
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
export BLOG_CONTENT_DIR="content/posts"
```

---

## 🧰 Installation Steps

```bash
# Clone the repository
git clone https://github.com/yourname/youtube-ai-blog.git
cd youtube-ai-blog

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**requirements.txt**
```
google-generativeai
yt_dlp
youtube-transcript-api
aiohttp
langdetect
googletrans==4.0.0-rc1
```

---

## 🧪 Example Usage

### Single Video
```bash
./process_youtube.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Batch Mode
```bash
./batch_process_youtube.sh youtube_list.txt
```

**youtube_list.txt**
```
https://www.youtube.com/watch?v=abc123
https://www.youtube.com/watch?v=def456
```

---

## 📦 Output Files

| Type | Path | Description |
|------|------|-------------|
| Blog Post | `content/posts/2025-10-17-title.md` | Pelican-ready markdown |
| Thumbnail | `content/thumbnails/video_id.jpg` | Saved thumbnail |
| Log File | `logs/20251017_120000.log` | Run log |

---

## 🧩 Future Extensions

| Feature | Description |
|----------|--------------|
| 🌍 Multi-language expansion | Add Japanese, Korean, Spanish |
| 🧠 Smart tagging | Auto-tag using semantic classification |
| 🪶 Image captioning | Auto-generate image alt text |
| 🔗 Related posts | Auto-link related content |
| 🛰️ Cron integration | Schedule automatic daily runs |

---

## 🧭 Author
**SparkYouTube AI Blog Project**  
© 2025 by SparkLab  
Maintainer: [Your Name]  
License: MIT
