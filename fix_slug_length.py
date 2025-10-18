#!/usr/bin/env python3
from pathlib import Path
import re

file_path = Path('myapp/ai_generator.py')
content = file_path.read_text()

# Find the slug generation and add length limit
old_code = '''            # Create post slug from the proper title for filename
            post_slug = slugify(title)
            # Ensure uniqueness by checking content_dir if available
            # For now, append video_id suffix if slug might conflict
            post_slug = f"{post_slug}-{video_id[:8]}"'''

new_code = '''            # Create post slug from the proper title for filename
            post_slug = slugify(title)
            # Truncate slug if too long (max 100 chars before video ID)
            # This prevents "File name too long" errors, especially for Chinese titles
            if len(post_slug) > 100:
                post_slug = post_slug[:100]
            # Ensure uniqueness by appending video_id suffix
            post_slug = f"{post_slug}-{video_id[:8]}"'''

if old_code in content:
    content = content.replace(old_code, new_code)
    file_path.write_text(content)
    print("✅ Fixed: Added slug length limit (max 100 chars)")
else:
    print("❌ Pattern not found")
    # Show what's there
    import re
    match = re.search(r'post_slug = slugify.*?video_id\[:8\]\}"', content, re.DOTALL)
    if match:
        print(f"Found:\n{match.group(0)[:200]}")
