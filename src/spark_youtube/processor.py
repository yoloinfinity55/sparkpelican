#!/usr/bin/env python3
"""
SparkYouTube AI Blog System - Main Processor

Orchestrates the complete workflow from YouTube URL to Pelican blog post.
Integrates transcript extraction, AI generation, and Pelican integration.
"""

import asyncio
import logging
import argparse
from typing import Dict, Any, Optional, List
from pathlib import Path

from spark_youtube.config.settings import get_config
from spark_youtube.core.transcript.extractor import extract_transcript, download_thumbnail, extract_video_id
from spark_youtube.core.ai.generator import generate_post_data
from spark_youtube.core.integrator.pelican import save_markdown_post, get_post_stats

logger = logging.getLogger(__name__)
config = get_config()

class VideoProcessingError(Exception):
    """Custom exception for video processing errors."""
    pass

class SparkYouTubeProcessor:
    """Main processor for the SparkYouTube AI Blog System."""

    def __init__(self):
        """Initialize the processor."""
        self.config = config
        logger.info("🚀 SparkYouTube Processor initialized")

    async def process_single_video(
        self,
        youtube_url: str,
        custom_title: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Process a single YouTube video into a blog post.

        Args:
            youtube_url: YouTube video URL
            custom_title: Optional custom title override
            category: Optional category override
            tags: Optional tags override
            force_regenerate: Force regeneration even if post exists

        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"🎬 Processing video: {youtube_url}")

            # Step 1: Extract video ID
            video_id = extract_video_id(youtube_url)
            logger.info(f"📹 Video ID: {video_id}")

            # Step 2: Check for existing post (unless forcing regeneration)
            if not force_regenerate:
                from spark_youtube.core.integrator.pelican import PelicanIntegrator
                integrator = PelicanIntegrator()
                existing_post = integrator.check_existing_post(video_id)
                if existing_post:
                    logger.info(f"📄 Post already exists for video {video_id}")
                    return {
                        'success': True,
                        'video_id': video_id,
                        'status': 'already_exists',
                        'post_path': existing_post,
                        'message': f'Post already exists: {existing_post}'
                    }

            # Step 3: Extract transcript and detect language
            logger.info("📝 Extracting transcript...")
            transcript, detected_language = await extract_transcript(youtube_url)
            logger.info(f"✅ Transcript extracted ({len(transcript)} chars, language: {detected_language})")

            # Step 4: Download thumbnail
            logger.info("📷 Downloading thumbnail...")
            youtube_title, thumbnail_path = await download_thumbnail(youtube_url)
            if youtube_title:
                logger.info(f"📺 Video title: {youtube_title}")
            if thumbnail_path:
                logger.info(f"🖼️  Thumbnail saved: {thumbnail_path}")

            # Step 5: Generate AI content
            logger.info("🤖 Generating blog post with AI...")
            post_data = await generate_post_data(
                transcript=transcript,
                video_id=video_id,
                language=detected_language,
                custom_title=custom_title,
                category=category,
                tags=tags,
                youtube_title=youtube_title,
                youtube_thumbnail=thumbnail_path
            )
            logger.info(f"✅ Blog post generated: {post_data['title']}")

            # Step 6: Save to Pelican content directory
            logger.info("💾 Saving blog post...")
            saved_path = await save_markdown_post(post_data, self.config.content_dir)
            logger.info(f"✅ Post saved: {saved_path}")

            return {
                'success': True,
                'video_id': video_id,
                'status': 'created',
                'post_path': saved_path,
                'title': post_data['title'],
                'language': detected_language,
                'category': post_data['category'],
                'tags': post_data['tags'],
                'message': f'Successfully created post: {post_data["title"]}'
            }

        except Exception as e:
            error_msg = f"Failed to process video {youtube_url}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'video_id': extract_video_id(youtube_url) if 'youtube' in str(e).lower() else 'unknown',
                'status': 'error',
                'error': str(e),
                'message': error_msg
            }

    async def process_batch_videos(
        self,
        video_urls: List[str],
        delay: float = 3.0,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Process multiple YouTube videos in batch.

        Args:
            video_urls: List of YouTube video URLs
            delay: Delay between processing each video (seconds)
            **kwargs: Additional arguments passed to process_single_video

        Returns:
            List of processing results
        """
        logger.info(f"📦 Starting batch processing of {len(video_urls)} videos")

        results = []

        for i, url in enumerate(video_urls, 1):
            logger.info(f"🎬 Processing video {i}/{len(video_urls)}: {url}")

            try:
                result = await self.process_single_video(url, **kwargs)
                results.append(result)

                # Show progress
                if result['success']:
                    logger.info(f"✅ Video {i}: {result.get('title', 'Unknown')}")
                else:
                    logger.error(f"❌ Video {i}: {result.get('error', 'Unknown error')}")

                # Delay between videos (except for the last one)
                if i < len(video_urls) and delay > 0:
                    logger.info(f"⏳ Waiting {delay}s before next video...")
                    await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"❌ Video {i} failed: {str(e)}")
                results.append({
                    'success': False,
                    'video_id': 'unknown',
                    'status': 'error',
                    'error': str(e),
                    'message': f'Batch processing failed for video {i}'
                })

        # Summary
        successful = sum(1 for r in results if r['success'])
        logger.info(f"📊 Batch processing complete: {successful}/{len(results)} successful")

        return results

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        try:
            post_stats = get_post_stats()

            return {
                'total_posts': post_stats['total_posts'],
                'posts_by_category': post_stats['posts_by_category'],
                'posts_by_language': post_stats['posts_by_language'],
                'content_dir': str(self.config.content_dir),
                'logs_dir': str(self.config.logs_dir)
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'error': str(e)}

    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate that the environment is properly configured.

        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []

        # Check API key
        if not self.config.gemini_api_key:
            issues.append("GEMINI_API_KEY environment variable not set")

        # Check required directories
        for dir_name, dir_path in [
            ('content', self.config.content_dir),
            ('thumbnails', self.config.thumbnails_dir),
            ('logs', self.config.logs_dir)
        ]:
            if not dir_path.exists():
                issues.append(f"Required directory missing: {dir_path}")
            elif not os.access(dir_path, os.W_OK):
                issues.append(f"Directory not writable: {dir_path}")

        # Check optional dependencies
        try:
            import youtube_transcript_api
        except ImportError:
            warnings.append("youtube-transcript-api not installed (official subtitles unavailable)")

        try:
            import yt_dlp
        except ImportError:
            warnings.append("yt_dlp not installed (thumbnails and audio fallback unavailable)")

        try:
            from langdetect import detect
        except ImportError:
            warnings.append("langdetect not installed (language detection may be limited)")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

def main():
    """Main entry point with command-line interface."""
    parser = argparse.ArgumentParser(
        description="SparkYouTube AI Blog System - Main Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/spark_youtube/processor.py single "https://www.youtube.com/watch?v=VIDEO_ID"
  python src/spark_youtube/processor.py batch urls.txt --delay 5
  python src/spark_youtube/processor.py validate
  python src/spark_youtube/processor.py stats
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Single video command
    single_parser = subparsers.add_parser('single', help='Process a single YouTube video')
    single_parser.add_argument('url', help='YouTube video URL')
    single_parser.add_argument('--title', help='Custom title (optional)')
    single_parser.add_argument('--category', default='General', help='Post category')
    single_parser.add_argument('--tags', nargs='*', help='Custom tags')
    single_parser.add_argument('--force', action='store_true', help='Force regeneration if post exists')

    # Batch processing command
    batch_parser = subparsers.add_parser('batch', help='Process multiple YouTube videos')
    batch_parser.add_argument('file', help='File containing YouTube URLs (one per line)')
    batch_parser.add_argument('--delay', type=float, default=3.0, help='Delay between videos (seconds)')
    batch_parser.add_argument('--category', default='General', help='Post category')
    batch_parser.add_argument('--tags', nargs='*', help='Custom tags')

    # Validation command
    subparsers.add_parser('validate', help='Validate environment configuration')

    # Stats command
    subparsers.add_parser('stats', help='Show processing statistics')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize processor
    processor = SparkYouTubeProcessor()

    async def run_async():
        try:
            if args.command == 'single':
                result = await processor.process_single_video(
                    args.url,
                    custom_title=args.title,
                    category=args.category,
                    tags=args.tags,
                    force_regenerate=args.force
                )

                if result['success']:
                    print(f"✅ Success: {result['message']}")
                    if 'post_path' in result:
                        print(f"📄 Post saved: {result['post_path']}")
                    return 0
                else:
                    print(f"❌ Failed: {result['message']}")
                    return 1

            elif args.command == 'batch':
                # Read URLs from file
                try:
                    with open(args.file, 'r', encoding='utf-8') as f:
                        urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
                except Exception as e:
                    print(f"❌ Error reading URL file: {e}")
                    return 1

                if not urls:
                    print("❌ No valid URLs found in file")
                    return 1

                print(f"📦 Processing {len(urls)} videos from {args.file}")

                results = await processor.process_batch_videos(
                    urls,
                    delay=args.delay,
                    category=args.category,
                    tags=args.tags
                )

                # Summary
                successful = sum(1 for r in results if r['success'])
                print(f"\n📊 Batch Results: {successful}/{len(results)} successful")

                for i, result in enumerate(results, 1):
                    status = "✅" if result['success'] else "❌"
                    message = result.get('message', 'Unknown error')
                    print(f"  {status} Video {i}: {message}")

                return 0 if successful == len(results) else 1

            elif args.command == 'validate':
                validation = processor.validate_environment()

                if validation['valid']:
                    print("✅ Environment validation passed!")
                    if validation['warnings']:
                        print("\n⚠️  Warnings:")
                        for warning in validation['warnings']:
                            print(f"  • {warning}")
                    return 0
                else:
                    print("❌ Environment validation failed:")
                    for issue in validation['issues']:
                        print(f"  • {issue}")
                    return 1

            elif args.command == 'stats':
                stats = processor.get_processing_stats()

                if 'error' in stats:
                    print(f"❌ Error getting stats: {stats['error']}")
                    return 1

                print("📊 Processing Statistics:")
                print(f"  Total posts: {stats['total_posts']}")
                print(f"  Content directory: {stats['content_dir']}")
                print(f"  Logs directory: {stats['logs_dir']}")

                if stats['posts_by_category']:
                    print("\n📂 Posts by category:")
                    for category, count in stats['posts_by_category'].items():
                        print(f"  • {category}: {count}")

                if stats['posts_by_language']:
                    print("\n🌐 Posts by language:")
                    for language, count in stats['posts_by_language'].items():
                        print(f"  • {language}: {count}")

                return 0

        except KeyboardInterrupt:
            print("\n⚠️  Processing interrupted by user")
            return 130
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return 1

    return asyncio.run(run_async())

if __name__ == "__main__":
    import sys
    sys.exit(main())
