#!/bin/bash
set -e

echo "🚀 Starting SparkPelican structure migration..."

# --- STEP 1: Create new folders ---
mkdir -p src/{ai,youtube,pelican,utils}
mkdir -p content/{drafts,thumbnails}
mkdir -p config
mkdir -p logs
mkdir -p scripts

# --- STEP 2: Move existing code into the new structure ---
if [ -d "myapp" ]; then
    echo "📦 Moving files from myapp/ to src/..."
    mv myapp/ai_generator.py src/ai/ || true
    mv myapp/youtube_transcript.py src/youtube/transcript.py || true
    mv myapp/pelican_integrator.py src/pelican/integrator.py || true
    rm -rf myapp
fi

# --- STEP 3: Move Pelican configs ---
if [ -f "pelicanconf.py" ]; then
    mv pelicanconf.py config/
fi
if [ -f "publishconf.py" ]; then
    mv publishconf.py config/
fi

# --- STEP 4: Create placeholder utilities ---
cat > src/utils/logger.py <<'EOF'
import logging, os

def get_logger(name="sparkpelican", log_file="logs/app.log"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
EOF

cat > src/config.py <<'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_DIR, "..", "content")
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
EOF

# --- STEP 5: Create main entrypoint ---
cat > src/main.py <<'EOF'
"""
Main automation entrypoint for SparkPelican.
Example:
    python -m src.main process_youtube "https://youtube.com/watch?v=..."
"""
import sys
from src.utils.logger import get_logger

logger = get_logger()

def main():
    logger.info("SparkPelican automation starting...")
    if len(sys.argv) > 1:
        task = sys.argv[1]
        logger.info(f"Running task: {task}")
        # future: add subcommands like 'process_youtube', 'generate_ai_post', etc.
    else:
        logger.info("No task specified.")
        print("Usage: python -m src.main [task]")

if __name__ == "__main__":
    main()
EOF

# --- STEP 6: Move shell scripts ---
for f in process_youtube.sh batch_process_youtube.sh; do
  if [ -f "$f" ]; then
    mv "$f" scripts/
  fi
done

# --- STEP 7: Create .env if missing ---
if [ ! -f ".env" ]; then
    echo "Creating default .env file..."
    cat > .env <<'EOF'
# Environment variables for SparkPelican
GEMINI_API_KEY="your_gemini_key_here"
YOUTUBE_API_KEY="your_youtube_key_here"
EOF
fi

echo "✅ Migration completed successfully!"
echo "Next steps:"
echo "1. Update imports inside your Python files if needed (I can generate that patch)."
echo "2. Commit the new structure:"
echo "     git add . && git commit -m 'Restructure project to src-based layout'"
