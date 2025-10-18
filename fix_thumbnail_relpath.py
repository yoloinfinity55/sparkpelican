#!/usr/bin/env python3
from pathlib import Path

file_path = Path('myapp/youtube_transcript.py')
content = file_path.read_text()

# Fix the relative path calculation
old_code = '''        if success:
            # Return relative path for Pelican
            rel_path = os.path.relpath(local_path)
            return title, rel_path'''

new_code = '''        if success:
            # Return relative path for Pelican (relative to content directory)
            # Convert content/images/file.jpg -> images/file.jpg
            rel_path = os.path.relpath(local_path)
            if rel_path.startswith('content/'):
                rel_path = rel_path.replace('content/', '', 1)
            return title, rel_path'''

content = content.replace(old_code, new_code)

file_path.write_text(content)
print("✅ Fixed thumbnail path to be relative to content directory")
