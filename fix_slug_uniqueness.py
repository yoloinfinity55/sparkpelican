#!/usr/bin/env python3
from pathlib import Path
import re

file_path = Path('myapp/ai_generator.py')
content = file_path.read_text()

# Find where the slug is generated and make it unique by adding video_id if duplicate
old_pattern = r'post_slug = slugify\(title\)'
new_pattern = '''post_slug = slugify(title)
            # Ensure uniqueness by checking content_dir if available
            # For now, append video_id suffix if slug might conflict
            post_slug = f"{post_slug}-{video_id[:8]}"'''

content = re.sub(old_pattern, new_pattern, content)

file_path.write_text(content)
print("✅ Updated slug generation to include video ID for uniqueness")
