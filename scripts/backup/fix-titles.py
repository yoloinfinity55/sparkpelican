#!/usr/bin/env python3
"""
Title Auto-Fix Script for Pelican Blog Posts

This script automatically fixes title formatting issues in all Markdown files
in the content/posts/ directory by removing quotes around titles in front matter.

Usage:
    python scripts/fix-titles.py

Returns:
    0 if all fixes applied successfully, 1 if any errors occurred
"""

import os
import re
import sys
from pathlib import Path

def fix_title_format():
    """Fix title formatting in all markdown files."""
    content_dir = Path('content/posts')
    files_fixed = []
    errors = []

    if not content_dir.exists():
        print(f"❌ Content directory not found: {content_dir}")
        return False

    # Find all markdown files
    markdown_files = list(content_dir.glob('*.md'))

    if not markdown_files:
        print("❌ No markdown files found in content/posts/")
        return False

    print(f"🔧 Fixing titles in {len(markdown_files)} markdown files...")

    for file_path in markdown_files:
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            original_content = content

            # Pattern to match title with quotes: title: "Some Title"
            # Replace with: title: Some Title
            title_pattern = r'^(title:\s*)"(.*?)"(.*)$'

            lines = content.split('\n')
            modified = False

            for i, line in enumerate(lines):
                if re.match(title_pattern, line.strip()):
                    # Extract parts: title:, content, rest of line
                    parts = re.match(title_pattern, line.strip())
                    if parts:
                        # Reconstruct line without quotes around title
                        fixed_line = f'{parts.group(1)}{parts.group(2)}{parts.group(3)}'
                        lines[i] = fixed_line
                        modified = True
                        print(f"   ✅ Fixed: {file_path.name} (line {i+1})")

            if modified:
                # Write back the fixed content
                fixed_content = '\n'.join(lines)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(fixed_content)
                files_fixed.append(file_path.name)

        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {str(e)}"
            print(f"   ❌ {error_msg}")
            errors.append(error_msg)

    # Report results
    if files_fixed:
        print(f"\n✅ Successfully fixed {len(files_fixed)} files:")
        for file in files_fixed:
            print(f"   • {file}")

    if errors:
        print(f"\n❌ Errors occurred in {len(errors)} files:")
        for error in errors:
            print(f"   • {error}")
        return False

    if not files_fixed and not errors:
        print("✅ No title formatting issues found!")

    return len(errors) == 0

def main():
    """Main function."""
    print("🚀 Pelican Blog Title Auto-Fix")
    print("=" * 40)

    success = fix_title_format()

    if success:
        print("\n✅ All title formatting issues have been fixed!")
        print("💡 Run 'python scripts/validate-titles.py' to verify all titles are correct.")
        sys.exit(0)
    else:
        print("\n❌ Some errors occurred during fixing. Please review manually.")
        sys.exit(1)

if __name__ == "__main__":
    main()
