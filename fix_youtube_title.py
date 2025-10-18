#!/usr/bin/env python3
from pathlib import Path
import re

file_path = Path('myapp/ai_generator.py')
content = file_path.read_text()

# Replace the title generation logic to use YouTube title directly
old_code = '''            if youtube_title:
                title = self._generate_proper_title(youtube_title)
            else:
                title = await self._generate_title_improved(transcript, custom_title)'''

new_code = '''            if youtube_title:
                # Use YouTube title directly - no transformation needed
                title = youtube_title.strip()
            else:
                # Only generate title if no YouTube title provided
                title = await self._generate_title_improved(transcript, custom_title)'''

if old_code in content:
    content = content.replace(old_code, new_code)
    file_path.write_text(content)
    print("✅ Fixed: Now uses YouTube title directly without transformation")
else:
    print("❌ Pattern not found")
