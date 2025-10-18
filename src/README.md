# 🚀 SparkYouTube AI Blog System

An intelligent, language-aware automation pipeline that converts YouTube videos into complete, SEO-ready blog posts using **Google Gemini AI**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-orange.svg)](https://ai.google.dev/)

## ✨ Features

- 🎬 **YouTube Video Processing** - Extract transcripts and metadata from YouTube videos
- 🤖 **AI-Powered Content Generation** - Create high-quality blog posts using Google Gemini AI
- 🌍 **Multi-Language Support** - Automatic language detection and content generation in Chinese/English
- 📝 **Pelican Integration** - Generate Pelican-compatible markdown files with proper front matter
- ⚡ **Batch Processing** - Process multiple videos with intelligent rate limiting
- 🔧 **Robust Error Handling** - Comprehensive logging and fallback mechanisms
- 📊 **Content Management** - Built-in tools for managing and organizing blog posts

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SparkYouTube AI Blog System                  │
├─────────────────────────────────────────────────────────────────┤
│  CLI Interface (cli.py)                                         │
│  ├── Interactive setup and configuration                        │
│  ├── Single/batch video processing                             │
│  └── Content management and statistics                         │
├─────────────────────────────────────────────────────────────────┤
│  Main Processor (processor.py)                                  │
│  ├── Orchestrates complete workflow                             │
│  ├── Handles single and batch processing                       │
│  └── Provides comprehensive error handling                     │
├─────────────────────────────────────────────────────────────────┤
│  Core Modules                                                   │
│  ├── 📝 Transcript (extractor.py) - YouTube data extraction     │
│  ├── 🤖 AI Generator (generator.py) - Content creation          │
│  └── 💾 Pelican Integrator (pelican.py) - Blog post saving     │
├─────────────────────────────────────────────────────────────────┤
│  Configuration (settings.py)                                    │
│  ├── Environment variable management                           │
│  ├── Path validation and directory creation                    │
│  └── Centralized configuration for all modules                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd spark_youtube

# Set your Gemini API Key (required)
export GEMINI_API_KEY="your_gemini_api_key_here"

# Install dependencies
pip install -r src/requirements.txt

# Verify setup
python src/spark_youtube/cli.py setup
```

### 2. Process Your First Video

```bash
# Single video processing
python src/spark_youtube/cli.py single "https://www.youtube.com/watch?v=VIDEO_ID"

# Or use the processor directly
python src/spark_youtube/processor.py single "https://www.youtube.com/watch?v=VIDEO_ID" --category "Technology"
```

### 3. Batch Processing

```bash
# Create a URL file
python src/spark_youtube/cli.py create-urls "https://youtube.com/watch?v=video1" "https://youtube.com/watch?v=video2"

# Process multiple videos
python src/spark_youtube/cli.py batch urls.txt --delay 5 --category "Tutorial"
```

## 📖 Usage Guide

### Command Line Interface

The system provides two main interfaces:

#### 🎯 **CLI (User-Friendly)**
```bash
python src/spark_youtube/cli.py <command> [options]

Commands:
  setup           Interactive setup guide
  single <url>    Process a single YouTube video
  batch <file>    Process multiple videos from file
  create-urls     Create URL file for batch processing
  stats           Show processing statistics
  validate        Validate environment configuration
  env             Show environment information
```

#### ⚙️ **Processor (Advanced)**
```bash
python src/spark_youtube/processor.py <command> [options]

Commands:
  single <url>    Process single video with full control
  batch <file>    Batch processing with custom settings
  validate        Environment validation
  stats           Detailed statistics
```

### Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `GEMINI_API_KEY` | *Required* | Your Google Gemini API key |
| `GEMINI_MODEL` | `models/gemini-2.5-flash` | AI model to use |
| `BATCH_DELAY` | `3.0` | Seconds between batch processing |
| `LOG_LEVEL` | `INFO` | Logging level |

### Example Workflows

#### Single Video Processing
```bash
python src/spark_youtube/cli.py single "https://youtu.be/dQw4w9WgXcQ" \
  --category "Technology" \
  --tags "AI" "machine-learning" "tutorial"
```

#### Batch Processing with Custom Settings
```bash
# Create URL file
echo "https://youtube.com/watch?v=video1" > my_videos.txt
echo "https://youtube.com/watch?v=video2" >> my_videos.txt

# Process with 5-second delay
python src/spark_youtube/cli.py batch my_videos.txt \
  --delay 5 \
  --category "Educational" \
  --tags "learning" "development"
```

## 🔧 Advanced Configuration

### Custom Settings

Create a `.env` file in your project root:

```bash
# .env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=models/gemini-2.5-flash
BATCH_DELAY=3.0
LOG_LEVEL=INFO

# Custom directories (optional)
CONTENT_DIR=content/posts
THUMBNAILS_DIR=content/thumbnails
LOGS_DIR=logs
```

### Directory Structure

The system expects the following structure:

```
your-project/
├── src/                          # Source code
│   ├── spark_youtube/            # Main package
│   ├── requirements.txt           # Dependencies
│   └── README.md                 # This file
├── content/                      # Generated content
│   ├── posts/                    # Blog posts (.md files)
│   └── thumbnails/               # Video thumbnails
├── logs/                         # Processing logs
├── pelicanconf.py               # Pelican configuration
└── themes/                       # Pelican themes
```

## 🛠️ Development

### Running Tests

```bash
# Basic functionality tests (no API key required)
python test_basic.py

# Full module tests (requires API key)
export GEMINI_API_KEY="your_key"
python test_modules.py
```

### Code Quality

```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/
```

### Adding New Features

The modular architecture makes it easy to extend:

1. **New Transcript Sources** - Add to `core/transcript/`
2. **New AI Providers** - Extend `core/ai/`
3. **New Output Formats** - Extend `core/integrator/`
4. **New CLI Commands** - Add to `cli.py`

## 📊 Monitoring and Statistics

### View Processing Statistics

```bash
# Basic stats
python src/spark_youtube/cli.py stats

# Detailed stats
python src/spark_youtube/cli.py stats --detailed
```

### Check Logs

```bash
# View recent logs
tail -f logs/spark_youtube.log

# Search for errors
grep "ERROR" logs/spark_youtube.log
```

## 🔍 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `GEMINI_API_KEY` not set | Run `export GEMINI_API_KEY="your_key"` |
| Directory not found | Run setup: `python src/spark_youtube/cli.py setup` |
| Transcript not available | Video may have disabled subtitles, audio fallback will be attempted |
| Language detection fails | System defaults to English, manual override available |

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Validate environment
python src/spark_youtube/cli.py validate

# Check detailed statistics
python src/spark_youtube/cli.py stats --detailed
```

## 🚀 Deployment

### With Pelican

```bash
# Generate static site
pelican content

# Preview locally
cd output
python3 -m http.server 8000

# Deploy to GitHub Pages
ghp-import output -b gh-pages
git push origin gh-pages
```

### Production Deployment

For production use, consider:

1. **Environment Variables** - Use proper secret management
2. **Rate Limiting** - Adjust batch delays based on API limits
3. **Monitoring** - Set up log aggregation and alerting
4. **Backup** - Regular backups of content and logs
5. **Updates** - Keep dependencies updated regularly

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `python test_basic.py`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** - For powering content generation
- **YouTube Transcript API** - For subtitle extraction
- **Pelican Static Site Generator** - For blog platform integration
- **Open Source Community** - For various tools and libraries

## 📞 Support

- 📧 **Email**: support@sparkyoutube.com
- 💬 **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 **Documentation**: [Project Wiki](https://github.com/your-repo/wiki)

---

**Made with ❤️ by the SparkYouTube Team**
