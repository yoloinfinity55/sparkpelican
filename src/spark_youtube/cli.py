#!/usr/bin/env python3
"""
SparkYouTube AI Blog System - Command Line Interface

User-friendly CLI for the complete SparkYouTube workflow.
Provides simple commands for processing videos and managing content.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from spark_youtube.processor import SparkYouTubeProcessor
from spark_youtube.config.settings import get_config

class SparkYouTubeCLI:
    """Command-line interface for SparkYouTube."""

    def __init__(self):
        """Initialize CLI."""
        self.processor = SparkYouTubeProcessor()
        self.config = get_config()

    def create_url_file(self, urls: List[str], filename: str = "urls.txt") -> None:
        """Create a URL file for batch processing."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# YouTube URLs for batch processing\n")
                f.write("# One URL per line\n\n")
                for url in urls:
                    f.write(f"{url}\n")

            print(f"✅ Created URL file: {filename}")
            print(f"📝 Added {len(urls)} URLs")

        except Exception as e:
            print(f"❌ Error creating URL file: {e}")
            sys.exit(1)

    def show_environment_setup(self) -> None:
        """Show environment setup instructions."""
        print("🔧 Environment Setup Instructions")
        print("=" * 40)

        print("\n1. Set your Gemini API Key:")
        print("   export GEMINI_API_KEY='your_gemini_api_key_here'")

        print("\n2. Install required dependencies:")
        print("   pip install -r requirements.txt")

        print("\n3. Verify installation:")
        print("   python src/spark_youtube/processor.py validate")

        print("\n4. Process your first video:")
        print("   python src/spark_youtube/processor.py single 'YOUTUBE_URL'")

    def show_project_structure(self) -> None:
        """Show the expected project structure."""
        print("📁 Expected Project Structure")
        print("=" * 40)

        structure = """
spark_youtube/
├── src/spark_youtube/
│   ├── config/
│   │   └── settings.py          # Configuration management
│   ├── core/
│   │   ├── transcript/
│   │   │   └── extractor.py     # YouTube transcript extraction
│   │   ├── ai/
│   │   │   └── generator.py     # AI content generation
│   │   └── integrator/
│   │       └── pelican.py       # Pelican blog integration
│   ├── processor.py             # Main processing orchestrator
│   └── cli.py                   # Command-line interface
├── content/
│   ├── posts/                   # Generated blog posts (.md files)
│   └── thumbnails/              # Downloaded video thumbnails
├── logs/                        # Processing logs
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
        """

        print(structure)

    def interactive_setup(self) -> None:
        """Interactive setup guide."""
        print("🚀 SparkYouTube Interactive Setup")
        print("=" * 40)

        # Check if API key is set
        if not self.config.gemini_api_key:
            print("\n❌ Gemini API Key not found!")
            print("Please set your API key:")
            print("   export GEMINI_API_KEY='your_key_here'")
            return

        print("\n✅ API Key found")

        # Check directories
        dirs_to_check = [
            ("Content", self.config.content_dir),
            ("Thumbnails", self.config.thumbnails_dir),
            ("Logs", self.config.logs_dir)
        ]

        all_dirs_ok = True
        for name, dir_path in dirs_to_check:
            if dir_path.exists():
                print(f"✅ {name} directory: {dir_path}")
            else:
                print(f"❌ {name} directory missing: {dir_path}")
                all_dirs_ok = False

        if all_dirs_ok:
            print("\n🎉 Setup complete! You can now process YouTube videos.")
            print("\nQuick start:")
            print("  python src/spark_youtube/processor.py single 'YOUTUBE_URL'")
        else:
            print("\n⚠️  Please create the missing directories listed above.")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SparkYouTube AI Blog System - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quick Start:
  # Setup environment
  python src/spark_youtube/cli.py setup

  # Process single video
  python src/spark_youtube/cli.py single "https://www.youtube.com/watch?v=VIDEO_ID"

  # Process multiple videos
  python src/spark_youtube/cli.py batch urls.txt

  # Show statistics
  python src/spark_youtube/cli.py stats

Examples:
  python src/spark_youtube/cli.py single "https://youtu.be/dQw4w9WgXcQ" --category "Technology"
  python src/spark_youtube/cli.py batch my_videos.txt --delay 5 --category "Tutorial"
  python src/spark_youtube/cli.py create-urls "url1" "url2" "url3" --file my_urls.txt
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Interactive setup guide')
    setup_parser.add_argument('--show-structure', action='store_true', help='Show project structure')

    # Single video command
    single_parser = subparsers.add_parser('single', help='Process a single YouTube video')
    single_parser.add_argument('url', help='YouTube video URL')
    single_parser.add_argument('--title', help='Custom title (optional)')
    single_parser.add_argument('--category', default='General', help='Post category (default: General)')
    single_parser.add_argument('--tags', nargs='*', default=[], help='Custom tags (space-separated)')
    single_parser.add_argument('--force', action='store_true', help='Force regeneration if post exists')

    # Batch processing command
    batch_parser = subparsers.add_parser('batch', help='Process multiple YouTube videos')
    batch_parser.add_argument('file', help='File containing YouTube URLs (one per line)')
    batch_parser.add_argument('--delay', type=float, default=3.0, help='Delay between videos in seconds (default: 3)')
    batch_parser.add_argument('--category', default='General', help='Post category (default: General)')
    batch_parser.add_argument('--tags', nargs='*', default=[], help='Custom tags (space-separated)')

    # URL file creation command
    create_parser = subparsers.add_parser('create-urls', help='Create a URL file for batch processing')
    create_parser.add_argument('urls', nargs='+', help='YouTube URLs to add to file')
    create_parser.add_argument('--file', default='urls.txt', help='Output filename (default: urls.txt)')

    # Statistics command
    stats_parser = subparsers.add_parser('stats', help='Show processing statistics')
    stats_parser.add_argument('--detailed', action='store_true', help='Show detailed statistics')

    # Validation command
    subparsers.add_parser('validate', help='Validate environment and configuration')

    # Environment info command
    subparsers.add_parser('env', help='Show environment information')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize CLI
    cli = SparkYouTubeCLI()

    try:
        if args.command == 'setup':
            if args.show_structure:
                cli.show_project_structure()
            else:
                cli.interactive_setup()

        elif args.command == 'single':
            # Run single video processing
            async def process_single():
                result = await cli.processor.process_single_video(
                    args.url,
                    custom_title=args.title,
                    category=args.category,
                    tags=args.tags if args.tags else None,
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

            return asyncio.run(process_single())

        elif args.command == 'batch':
            # Run batch processing
            async def process_batch():
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

                results = await cli.processor.process_batch_videos(
                    urls,
                    delay=args.delay,
                    category=args.category,
                    tags=args.tags if args.tags else None
                )

                # Summary
                successful = sum(1 for r in results if r['success'])
                print(f"\n📊 Batch Results: {successful}/{len(results)} successful")

                for i, result in enumerate(results, 1):
                    status = "✅" if result['success'] else "❌"
                    message = result.get('message', 'Unknown error')
                    print(f"  {status} Video {i}: {message}")

                return 0 if successful == len(results) else 1

            return asyncio.run(process_batch())

        elif args.command == 'create-urls':
            cli.create_url_file(args.urls, args.file)
            print(f"\n💡 Now you can process these URLs with:")
            print(f"   python src/spark_youtube/cli.py batch {args.file}")
            return 0

        elif args.command == 'stats':
            stats = cli.processor.get_processing_stats()

            if 'error' in stats:
                print(f"❌ Error getting stats: {stats['error']}")
                return 1

            print("📊 Processing Statistics:")
            print(f"  Total posts: {stats['total_posts']}")
            print(f"  Content directory: {stats['content_dir']}")
            print(f"  Logs directory: {stats['logs_dir']}")

            if args.detailed:
                if stats['posts_by_category']:
                    print("\n📂 Posts by category:")
                    for category, count in stats['posts_by_category'].items():
                        print(f"  • {category}: {count}")

                if stats['posts_by_language']:
                    print("\n🌐 Posts by language:")
                    for language, count in stats['posts_by_language'].items():
                        print(f"  • {language}: {count}")

            return 0

        elif args.command == 'validate':
            validation = cli.processor.validate_environment()

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

        elif args.command == 'env':
            print("🔧 Environment Information")
            print("=" * 40)

            print(f"📁 Project root: {cli.config.project_root}")
            print(f"📁 Content directory: {cli.config.content_dir}")
            print(f"📁 Thumbnails directory: {cli.config.thumbnails_dir}")
            print(f"📁 Logs directory: {cli.config.logs_dir}")
            print(f"📁 Output directory: {cli.config.output_dir}")

            print(f"\n🤖 Gemini model: {cli.config.gemini_model}")
            print(f"⚙️  Batch delay: {cli.config.batch_delay}s")
            print(f"🔄 Max retries: {cli.config.max_retries}")

            api_key_status = "✅ Set" if cli.config.gemini_api_key else "❌ Missing"
            print(f"🔑 API Key: {api_key_status}")

            return 0

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
