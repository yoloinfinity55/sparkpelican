#!/usr/bin/env python3
from pathlib import Path

file_path = Path('myapp/youtube_transcript.py')
content = file_path.read_text()

# Fix the default output_dir parameter
content = content.replace(
    'async def download_youtube_thumbnail(youtube_url: str, output_dir: str = "images")',
    'async def download_youtube_thumbnail(youtube_url: str, output_dir: str = "content/images")'
)

file_path.write_text(content)
print("✅ Updated thumbnail path from 'images' to 'content/images'")
