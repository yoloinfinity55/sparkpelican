#!/usr/bin/env python3
"""
YouTube Video Processing Script

This script processes a YouTube video URL to:
1. Extract the transcript
2. Generate a blog post using AI
3. Save the post to the Pelican content directory

Usage:
    python process_youtube_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the myapp directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'myapp'))

from youtube_transcript import get_transcript_async, extract_video_id, get_video_title_and_thumbnail, detect_transcript_language, download_youtube_thumbnail
from ai_generator import generate_post_async
from pelican_integrator import save_markdown_post

async def process_youtube_video(youtube_url: str):
    """Process a YouTube video and generate a blog post."""
    try:
        print(f"🔄 Processing YouTube video: {youtube_url}")

        # Step 1: Extract video ID
        video_id = extract_video_id(youtube_url)
        print(f"📹 Video ID: {video_id}")

        # Step 2: Get transcript
        print("📝 Extracting transcript...")
        transcript = await get_transcript_async(youtube_url)
        print(f"✅ Transcript extracted ({len(transcript)} characters)")

        # Step 3: Download video thumbnail locally
        print("📷 Downloading thumbnail...")
        youtube_title, local_thumbnail_path = await download_youtube_thumbnail(youtube_url)
        if youtube_title:
            print(f"📺 Video title: {youtube_title}")
        if local_thumbnail_path:
            print(f"🖼️  Thumbnail saved to: {local_thumbnail_path}")

        # Step 4: Detect transcript language
        print("🌐 Detecting language...")
        detected_language = await detect_transcript_language(transcript)
        print(f"🗣️  Detected language: {detected_language}")

        # Step 5: Generate AI content
        print("🤖 Generating blog post...")
        post_data = await generate_post_async(
            transcript=transcript,
            video_id=video_id,
            custom_title=None,
            category="General",
            tags=["youtube", "video", "content"],
            youtube_title=youtube_title,
            youtube_thumbnail=local_thumbnail_path,
            language=detected_language
        )
        print("✅ Blog post generated")

        # Step 6: Save to content directory
        content_dir = Path("content/posts")
        content_dir.mkdir(parents=True, exist_ok=True)

        await save_markdown_post(post_data, content_dir)
        print(f"💾 Post saved to: {post_data.get('filename', 'unknown')}")

        return True

    except Exception as e:
        print(f"❌ Error processing video: {str(e)}")
        return False

def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python process_youtube_video.py 'YOUTUBE_URL'")
        sys.exit(1)

    youtube_url = sys.argv[1]

    # Run the async process
    result = asyncio.run(process_youtube_video(youtube_url))

    if result:
        print("🎉 Video processing completed successfully!")
    else:
        print("💥 Video processing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
