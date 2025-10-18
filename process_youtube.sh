#!/bin/bash
# Single YouTube video processing script
# Usage: ./process_youtube.sh "YOUTUBE_URL"

if [ -z "$1" ]; then
  echo "Usage: $0 <youtube_url>"
  exit 1
fi

YOUTUBE_URL="$1"
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/process_$TIMESTAMP.log"

echo "🚀 Processing video: $YOUTUBE_URL" | tee -a "$LOG_FILE"

source ./venv/bin/activate

python3 process_youtube_video.py "$YOUTUBE_URL" 2>&1 | tee -a "$LOG_FILE"

echo "🎉 Finished processing $YOUTUBE_URL" | tee -a "$LOG_FILE"
