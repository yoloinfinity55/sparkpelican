#!/usr/bin/env python3
"""
Title Validation Script for Pelican Blog Posts
This script checks all Markdown files in the content/posts/ directory
to ensure titles in front matter don't have quotes around them.

Usage:
    python scripts/validate-titles.py

Returns:
    0 if all titles are valid, 1 if any issues found
"""
import os
import re
import sys
from pathlib import Path


def validate_title_format():
    """Check all markdown files for proper title format in front matter."""
    content_dir = Path('content/posts')
    issues_found = []
    
    if not content_dir.exists():
        print(f"❌ Content directory not found: {content_dir}")
        return False
    
    # Find all markdown files
    markdown_files = list(content_dir.glob('*.md'))
    
    if not markdown_files:
        print("❌ No markdown files found in content/posts/")
        return False
    
    print(f"🔍 Checking {len(markdown_files)} markdown files...")
    
    for file_path in markdown_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Look for title field in front matter
            # Pattern matches: title: "Some Title" (with quotes)
            title_pattern = r'^title:\s*"([^"]+)"'
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                if re.match(title_pattern, line.strip()):
                    # Extract title value
                    title_value = re.search(title_pattern, line.strip()).group(1)
                    issues_found.append({
                        'file': file_path.name,
                        'line': line_num,
                        'issue': f'Title has quotes: {line.strip()}',
                        'suggestion': f'Should be: title: {title_value}'
                    })
        
        except Exception as e:
            issues_found.append({
                'file': file_path.name,
                'line': 0,
                'issue': f'Error reading file: {str(e)}',
                'suggestion': 'Check file encoding and format'
            })
    
    # Report results
    if not issues_found:
        print("✅ All titles are properly formatted!")
        return True
    else:
        print(f"\n❌ Found {len(issues_found)} title formatting issues:")
        print("=" * 60)
        
        for issue in issues_found:
            print(f"\n📄 {issue['file']} (line {issue['line']}):")
            print(f"   Current: {issue['issue']}")
            print(f"   Fix to: {issue['suggestion']}")
        
        print(f"\n{'=' * 60}")
        print(f"💡 To fix automatically, run: python scripts/fix-titles.py")
        return False


def main():
    """Main function."""
    print("🚀 Pelican Blog Title Validation")
    print("=" * 40)
    
    success = validate_title_format()
    
    if not success:
        print("\n❌ Validation failed! Please fix the issues above.")
        sys.exit(1)
    else:
        print("\n✅ All validations passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()