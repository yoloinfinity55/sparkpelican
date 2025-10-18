#!/usr/bin/env python3
from pathlib import Path

file_path = Path('myapp/ai_generator.py')
content = file_path.read_text()

# Find and fix the frontmatter generation
# The issue is likely in how the frontmatter lines are joined
old_pattern = "return '\\n'.join(front_matter_lines)"
new_pattern = "return '\\n'.join(front_matter_lines) + '\\n'"

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    file_path.write_text(content)
    print("✅ Fixed frontmatter to add newline before closing ---")
else:
    print("⚠️  Pattern not found, checking alternative...")
    # Show what's actually there
    import re
    matches = re.findall(r"return.*front_matter_lines.*", content)
    for match in matches:
        print(f"Found: {match}")
