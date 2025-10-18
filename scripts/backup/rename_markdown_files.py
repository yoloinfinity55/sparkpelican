#!/usr/bin/env python3
"""
Script to standardize markdown file names to YYYY-MM-DD-title.md format
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

def extract_date_from_md(file_path):
    """Extract date from markdown file's frontmatter"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for frontmatter between --- markers
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not frontmatter_match:
            return None

        frontmatter_text = frontmatter_match.group(1)

        # Simple YAML-like parsing for date field
        for line in frontmatter_text.split('\n'):
            line = line.strip()
            if line.startswith('date:'):
                date_str = line.split(':', 1)[1].strip().strip('"\'')
                # Parse ISO format
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    return dt.strftime('%Y-%m-%d')
                except:
                    pass
                # Try other formats
                for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime('%Y-%m-%d')
                    except:
                        continue
    except Exception as e:
        print(f'Error reading {file_path}: {e}')
    return None

def extract_title_from_md(file_path):
    """Extract title from markdown file's frontmatter"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for frontmatter between --- markers
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not frontmatter_match:
            return None

        frontmatter_text = frontmatter_match.group(1)

        # Simple YAML-like parsing for title field
        for line in frontmatter_text.split('\n'):
            line = line.strip()
            if line.startswith('title:'):
                title = line.split(':', 1)[1].strip().strip('"\'')
                return title
    except Exception as e:
        print(f'Error reading title from {file_path}: {e}')
    return None

def generate_slug(title):
    """Generate URL-friendly slug from title"""
    if not title:
        return 'untitled'

    # Remove special characters and replace spaces with hyphens
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove non-word chars except spaces and hyphens
    slug = re.sub(r'[\s_]+', '-', slug)   # Replace spaces/underscores with hyphens
    slug = slug.strip('-')
    return slug[:50]  # Limit length

def get_files_to_rename():
    """Get list of markdown files that need renaming"""
    posts_dir = Path('content/posts')
    files_to_rename = []

    for md_file in posts_dir.glob('*.md'):
        filename = md_file.name

        # Skip if already in correct format (YYYY-MM-DD-*.md)
        if re.match(r'^\d{4}-\d{2}-\d{2}-', filename):
            continue

        # Extract date and title
        date = extract_date_from_md(md_file)
        title = extract_title_from_md(md_file)

        if not date:
            # Use current date for files without dates
            date = datetime.now().strftime('%Y-%m-%d')

        if not title:
            # Use filename (without extension) as title if no title in frontmatter
            title = filename.replace('.md', '')

        slug = generate_slug(title)
        new_filename = f'{date}-{slug}.md'

        if filename != new_filename:
            files_to_rename.append({
                'current': filename,
                'new': new_filename,
                'path': md_file
            })

    return files_to_rename

def main():
    """Main function"""
    print("Markdown files that will be renamed:")
    print("=" * 80)

    files_to_rename = get_files_to_rename()

    if not files_to_rename:
        print("No files need renaming.")
        return

    for file_info in sorted(files_to_rename, key=lambda x: x['current']):
        print(f"{file_info['current']:<60} -> {file_info['new']}")

    print(f"\nTotal files to rename: {len(files_to_rename)}")

    # Ask for confirmation
    response = input("\nProceed with renaming? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Operation cancelled.")
        return

    # Perform renaming
    renamed_count = 0
    posts_dir = Path('content/posts')

    for file_info in files_to_rename:
        try:
            new_path = posts_dir / file_info['new']
            file_info['path'].rename(new_path)
            print(f"✓ {file_info['current']} -> {file_info['new']}")
            renamed_count += 1
        except Exception as e:
            print(f"✗ Error renaming {file_info['current']}: {e}")

    print(f"\nSuccessfully renamed {renamed_count} files.")

if __name__ == "__main__":
    main()
