#!/bin/bash
# Batch YouTube video processing script
# Usage: ./batch_process_youtube.sh youtube_list.txt

if [ -z "$1" ]; then
  echo "Usage: $0 <youtube_list_file>"
  exit 1
fi

LIST_FILE="$1"
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"
source ./venv/bin/activate

COUNT=0
TOTAL=$(grep -cve '^#' "$LIST_FILE")

echo "Processing batch list: $LIST_FILE"
echo "Found $TOTAL videos."

while read -r URL; do
  [[ "$URL" =~ ^#.*$ ]] && continue
  COUNT=$((COUNT+1))
  echo "---------------------------------------------------"
  echo "[$COUNT/$TOTAL] Processing $URL"
  ./process_youtube.sh "$URL"
  sleep 3
done < "$LIST_FILE"

echo "---------------------------------------------------"
echo "🎉 Batch processing completed ($COUNT/$TOTAL videos)"
