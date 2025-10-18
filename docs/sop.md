# 📜 SparkYouTube AI Blog System — Standard Operating Procedure (SOP v3.0)

> Last Updated: October 2025  
> Author: SparkLab Team  
> Applies to: `process_youtube_video.py`, `process_youtube.sh`, and `batch_process_youtube.sh`

---

## 🧩 1. Overview

This SOP defines the **daily operational workflow** for converting YouTube videos into blog posts using the **SparkYouTube AI Blog System**.  

The system:
- Extracts video subtitles (preferring official captions)
- Falls back to audio-to-text when needed
- Detects language (Chinese or English)
- Uses **Gemini AI** to generate content in the same language
- Saves posts to **Pelican content directory** with full metadata

---

## ⚙️ 2. Environment Setup

### Step 1. Activate Environment
```bash
cd /path/to/youtube-ai-blog
source venv/bin/activate
```

### Step 2. Export API Key
```bash
export GEMINI_API_KEY="your_real_gemini_key_here"
```

### Step 3. Verify Directory Structure
```bash
tree -L 2
```
Expected output:
```
.
├── process_youtube_video.py
├── myapp/
├── content/
│   └── posts/
├── logs/
└── youtube_list.txt
```

### Step 4. Create Folders (if missing)
```bash
mkdir -p content/posts content/thumbnails logs
```

---

## 🎬 3. Single Video Workflow

### Command:
```bash
./process_youtube.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Behind the Scenes:
1. Extracts video ID  
2. Tries to fetch official subtitles via `youtube-transcript-api`  
3. If missing, downloads audio and transcribes using Gemini  
4. Detects language (Chinese or English)  
5. Generates a full blog post using Gemini 1.5 Pro  
6. Creates Pelican Markdown post with metadata and thumbnail  

### Example Output:
```
🚀 Processing YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ
📹 Video ID: dQw4w9WgXcQ
📝 Extracting transcript...
✅ Transcript extracted (4512 chars)
🌐 Detecting language...
🗣️  Detected language: en
📷 Downloading thumbnail...
✅ Thumbnail saved: content/thumbnails/dQw4w9WgXcQ.jpg
🤖 Generating blog post with Gemini...
✅ Blog post generated
💾 Saved: content/posts/2025-10-17-ai-revolution-gemini.md
🎉 Done — English post created!
```

---

## ⚡ 4. Batch Workflow

### Command:
```bash
./batch_process_youtube.sh youtube_list.txt
```

### `youtube_list.txt` Format:
```
https://www.youtube.com/watch?v=abc123
https://www.youtube.com/watch?v=xyz789
# Lines starting with # are ignored
```

Each video is processed sequentially with a 3-second delay.

### Example Output:
```
Processing batch list: youtube_list.txt
Found 2 videos.
---------------------------------------------------
[1/2] Processing abc123 ...
✅ Saved: content/posts/2025-10-17-ai-and-creativity.md
[2/2] Processing xyz789 ...
✅ Saved: content/posts/2025-10-17-how-gemini-thinks.md
---------------------------------------------------
🎉 Batch completed successfully (2/2)
```

All logs are stored in `/logs/` as timestamped `.log` files.

---

## 🧠 5. Language Behavior

| Detected Transcript Language | Output Blog Language | Gemini Prompt Context |
|-------------------------------|----------------------|------------------------|
| `zh` / `zh-cn` / `zh-tw` | Chinese (Simplified or Traditional) | Write full article in professional Chinese |
| `en` | English | Write full article in English |
| Unknown / Mixed | English (default) | Use English fallback unless high Chinese score |

The system uses `langdetect` + Gemini content heuristics to confirm.  
Chinese transcripts trigger bilingual-safe Markdown (UTF-8 encoded).

---

## 📦 6. Output Verification

After each run, verify:
1. ✅ Markdown file exists in `content/posts/`
2. ✅ Thumbnail exists in `content/thumbnails/`
3. ✅ Metadata block includes:
   ```markdown
   Title: ...
   Date: ...
   Category: ...
   Language: en / zh
   Thumbnail: ...
   ```
4. ✅ File encoding is UTF-8
5. ✅ Pelican build succeeds (`pelican content`)

---

## 🧯 7. Error Recovery Procedures

| Error Message | Likely Cause | Recommended Fix |
|----------------|--------------|------------------|
| ❌ *Transcript not found* | Video has no captions | Enable audio-to-text fallback; check internet connection |
| ❌ *Gemini API Key missing* | Environment not set | Run `export GEMINI_API_KEY="..."` |
| ❌ *Thumbnail download failed* | Network or 404 error | Use placeholder image (`/content/thumbnails/default.jpg`) |
| ❌ *Blog save failed* | Missing permissions | `chmod -R 755 content/` |
| 💥 *Process failed mid-run* | Exception in Python | Check `logs/*.log` for traceback |
| 🔁 *Language misdetected* | Mixed subtitles | Force language override in script if necessary |

---

## 🧱 8. Integration with Pelican

Once posts are generated:
```bash
pelican content
```

To preview locally:
```bash
cd output
python3 -m http.server 8000
```
Visit: **http://localhost:8000**

To deploy to GitHub Pages:
```bash
ghp-import output -b gh-pages
git push origin gh-pages
```

---

## 🧰 9. Maintenance

### Monthly Tasks
```bash
pip install --upgrade google-generativeai yt_dlp youtube-transcript-api
```

### Clean Old Logs
```bash
rm -rf logs/*
```

### Verify Pelican Output Directory
Ensure `/output` is clean before each build:
```bash
rm -rf output/
pelican content
```

---

## 🧩 10. QA Checklist

| Check | Expected Result |
|--------|-----------------|
| 🟢 API key active | Gemini connection successful |
| 🟢 Network online | yt_dlp and transcript API fetch succeed |
| 🟢 Subtitle extraction works | English or Chinese detected |
| 🟢 AI response valid | Blog post has clear sections |
| 🟢 Markdown saved | File readable, correct encoding |
| 🟢 Thumbnail image OK | 1280x720 or smaller |
| 🟢 Pelican build passes | No front-matter errors |

---

## 🧠 11. Troubleshooting Tips

- **Gemini timeout:** Try smaller transcripts (chunk the text).  
- **Language mismatch:** Force translation using `googletrans`.  
- **YouTube unavailable:** Use VPN or mirror source.  
- **Batch interruptions:** Resume from last processed line using:
  ```bash
  tail -n +5 youtube_list.txt > remaining.txt
  ./batch_process_youtube.sh remaining.txt
  ```

---

## 🧭 12. Versioning

| Component | Version | Notes |
|------------|----------|-------|
| SparkYouTube | v3.0 | Stable |
| Gemini API | 1.5 Pro | Text generation |
| yt_dlp | 2025.09.01 | Latest verified |
| Pelican | 5.x | Markdown build tested |

---

## 🧩 13. Future SOP Additions

| Planned Upgrade | Description |
|------------------|--------------|
| Auto-cron job | Daily scheduled batch run |
| Web dashboard | Monitor processing status |
| Multi-language prompt tuning | Gemini adaptive translation |
| Logging to SQLite | Persistent job tracking |
| Post-audit summary | Generate daily reports |

---

## ✅ 14. Quick Summary

| Step | Action | Command |
|------|---------|----------|
| 1️⃣ | Activate environment | `source venv/bin/activate` |
| 2️⃣ | Export Gemini key | `export GEMINI_API_KEY="..."` |
| 3️⃣ | Run single video | `./process_youtube.sh "<url>"` |
| 4️⃣ | Run batch list | `./batch_process_youtube.sh youtube_list.txt` |
| 5️⃣ | Check outputs | `ls content/posts/` |
| 6️⃣ | Build & deploy | `pelican content && ghp-import output -b gh-pages && git push origin gh-pages` |

---

## 🪶 End of SOP
