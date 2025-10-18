#!/usr/bin/env python3
from pathlib import Path

file_path = Path('myapp/ai_generator.py')
content = file_path.read_text()

# Fix the frontmatter assembly - add newline before closing ---
old_line = '            full_content = f"---\\n{front_matter}---\\n\\n{summary}\\n\\n{content}"'
new_line = '            full_content = f"---\\n{front_matter}\\n---\\n\\n{summary}\\n\\n{content}"'

if old_line in content:
    content = content.replace(old_line, new_line)
    file_path.write_text(content)
    print("✅ Fixed: Added newline before closing --- in frontmatter")
else:
    print("❌ Pattern not found. Showing what's there:")
    import re
    match = re.search(r'full_content = f"---.*', content)
    if match:
        print(f"Found: {match.group(0)}")
