#!/usr/bin/env python3
from pathlib import Path

file_path = Path('myapp/youtube_transcript.py')
content = file_path.read_text()

# Replace the model name
content = content.replace(
    "GenerativeModel('gemini-1.5-pro')",
    "GenerativeModel('gemini-1.5-pro-latest')"
)

# Write back
file_path.write_text(content)
print("✅ Updated gemini-1.5-pro to gemini-1.5-pro-latest")

# Verify
if 'gemini-1.5-pro-latest' in content:
    print("✅ Verification passed")
else:
    print("❌ Verification failed")
