#!/usr/bin/env python3
"""
Comprehensive Content Management Script for Pelican Blog Posts

This script consolidates multiple content management functions:
- Title format validation and fixing
- File naming standardization
- Backup and restore capabilities
- Batch operations

Usage:
    python scripts/content_manager.py [COMMAND] [OPTIONS]

Commands:
    validate     Validate title formatting and file naming
    fix-titles   Fix title formatting issues automatically
    rename       Standardize markdown file names
    backup       Create backups before making changes
    restore      Restore from backup
    all          Run all operations (backup -> fix -> rename)

Options:
    --dry-run    Show what would be changed without making changes
    --backup-dir Directory to store backups (default: scripts/backup)
    --content-dir Directory containing posts (default: content/posts)

Examples:
    python scripts/content_manager.py validate
    python scripts/content_manager.py fix-titles --dry-run
    python scripts/content_manager.py all --backup-dir ./my-backups
"""

import os
import re
import sys
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class ContentManager:
    """Comprehensive content management for Pelican blog posts."""

    def __init__(self, content_dir: str = "content/posts", backup_dir: str = "scripts/backup"):
        """Initialize the content manager."""
        self.content_dir = Path(content_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def extract_frontmatter_info(self, file_path: Path) -> Tuple[Optional[str], Optional[str]]:
        """Extract date and title from markdown file's frontmatter."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for frontmatter between --- markers
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
            if not frontmatter_match:
                return None, None

            frontmatter_text = frontmatter_match.group(1)
            date, title = None, None

            # Parse YAML-like frontmatter
            for line in frontmatter_text.split('\n'):
                line = line.strip()
                if line.startswith('date:'):
                    date_str = line.split(':', 1)[1].strip().strip('"\'')
                    # Parse ISO format
                    try:
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        date = dt.strftime('%Y-%m-%d')
                    except:
                        pass
                    # Try other formats
                    for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            date = dt.strftime('%Y-%m-%d')
                            break
                        except:
                            continue

                elif line.startswith('title:'):
                    title = line.split(':', 1)[1].strip().strip('"\'')
                    # Remove quotes if present
                    title = title.strip('"').strip("'")

            return date, title

        except Exception as e:
            print(f'Error reading {file_path}: {e}')
            return None, None

    def generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title."""
        if not title:
            return 'untitled'

        # Remove special characters and replace spaces with hyphens
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove non-word chars except spaces and hyphens
        slug = re.sub(r'[\s_]+', '-', slug)   # Replace spaces/underscores with hyphens
        slug = slug.strip('-')
        return slug[:50]  # Limit length

    def validate_titles(self, dry_run: bool = False) -> List[Dict]:
        """Validate title formatting in all markdown files."""
        issues = []

        if not self.content_dir.exists():
            print(f"❌ Content directory not found: {self.content_dir}")
            return issues

        markdown_files = list(self.content_dir.glob('*.md'))

        for file_path in markdown_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    # Check for quoted titles
                    if re.match(r'^\s*title:\s*".*?"', line.strip()):
                        title_value = re.search(r'^\s*title:\s*"([^"]+)"', line.strip()).group(1)
                        issues.append({
                            'file': file_path.name,
                            'line': line_num,
                            'type': 'quoted_title',
                            'current': line.strip(),
                            'fixed': f'title: {title_value}'
                        })

            except Exception as e:
                issues.append({
                    'file': file_path.name,
                    'line': 0,
                    'type': 'error',
                    'current': f'Error reading file: {str(e)}',
                    'fixed': 'Check file encoding and format'
                })

        return issues

    def fix_titles(self, dry_run: bool = False) -> int:
        """Fix title formatting issues."""
        issues = self.validate_titles(dry_run=True)
        title_issues = [issue for issue in issues if issue['type'] == 'quoted_title']

        if not title_issues:
            print("✅ No title formatting issues found!")
            return 0

        print(f"🔧 Fixing {len(title_issues)} title formatting issues...")

        fixed_count = 0

        for issue in title_issues:
            if not dry_run:
                try:
                    file_path = self.content_dir / issue['file']
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    fixed_content = content.replace(issue['current'], issue['fixed'], 1)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)

                    print(f"   ✅ Fixed: {issue['file']} (line {issue['line']})")
                    fixed_count += 1

                except Exception as e:
                    print(f"   ❌ Error fixing {issue['file']}: {e}")
            else:
                print(f"   🔄 Would fix: {issue['file']} (line {issue['line']})")

        return fixed_count

    def get_files_to_rename(self) -> List[Dict]:
        """Get list of markdown files that need renaming."""
        files_to_rename = []

        for md_file in self.content_dir.glob('*.md'):
            filename = md_file.name

            # Skip if already in correct format (YYYY-MM-DD-*.md)
            if re.match(r'^\d{4}-\d{2}-\d{2}-', filename):
                continue

            # Extract date and title
            date, title = self.extract_frontmatter_info(md_file)

            if not date:
                # Use current date for files without dates
                date = datetime.now().strftime('%Y-%m-%d')

            if not title:
                # Use filename (without extension) as title if no title in frontmatter
                title = filename.replace('.md', '')

            slug = self.generate_slug(title)
            new_filename = f'{date}-{slug}.md'

            if filename != new_filename:
                files_to_rename.append({
                    'current': filename,
                    'new': new_filename,
                    'path': md_file
                })

        return files_to_rename

    def rename_files(self, dry_run: bool = False) -> int:
        """Standardize markdown file names."""
        files_to_rename = self.get_files_to_rename()

        if not files_to_rename:
            print("✅ No files need renaming.")
            return 0

        print(f"📁 Renaming {len(files_to_rename)} files...")

        for file_info in sorted(files_to_rename, key=lambda x: x['current']):
            if not dry_run:
                try:
                    new_path = self.content_dir / file_info['new']
                    file_info['path'].rename(new_path)
                    print(f"   ✅ {file_info['current']} -> {file_info['new']}")
                except Exception as e:
                    print(f"   ❌ Error renaming {file_info['current']}: {e}")
            else:
                print(f"   🔄 Would rename: {file_info['current']} -> {file_info['new']}")

        return len(files_to_rename)

    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a backup of the content directory."""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"

        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)

        # Copy all markdown files
        for md_file in self.content_dir.glob('*.md'):
            shutil.copy2(md_file, backup_path / md_file.name)

        print(f"✅ Created backup: {backup_path}")
        return str(backup_path)

    def restore_backup(self, backup_name: str) -> bool:
        """Restore from a backup."""
        backup_path = self.backup_dir / backup_name

        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_path}")
            return False

        # Copy files back
        for backup_file in backup_path.glob('*.md'):
            shutil.copy2(backup_file, self.content_dir / backup_file.name)

        print(f"✅ Restored from backup: {backup_path}")
        return True

    def run_all_operations(self, dry_run: bool = False, create_backup: bool = True) -> Dict:
        """Run all operations: backup -> fix titles -> rename files."""
        results = {
            'backup_created': None,
            'titles_fixed': 0,
            'files_renamed': 0,
            'errors': []
        }

        # Create backup if requested
        if create_backup and not dry_run:
            try:
                results['backup_created'] = self.create_backup("pre_consolidation_backup")
            except Exception as e:
                results['errors'].append(f"Backup failed: {e}")
                return results

        # Fix titles
        try:
            results['titles_fixed'] = self.fix_titles(dry_run)
        except Exception as e:
            results['errors'].append(f"Title fixing failed: {e}")

        # Rename files
        try:
            results['files_renamed'] = self.rename_files(dry_run)
        except Exception as e:
            results['errors'].append(f"File renaming failed: {e}")

        return results

def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Pelican Content Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/content_manager.py validate
  python scripts/content_manager.py fix-titles --dry-run
  python scripts/content_manager.py all --backup-dir ./backups
  python scripts/content_manager.py backup my-backup-name
        """
    )

    parser.add_argument(
        'command',
        choices=['validate', 'fix-titles', 'rename', 'backup', 'restore', 'all'],
        help='Command to execute'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )

    parser.add_argument(
        '--backup-dir',
        default='scripts/backup',
        help='Directory to store backups (default: scripts/backup)'
    )

    parser.add_argument(
        '--content-dir',
        default='content/posts',
        help='Directory containing posts (default: content/posts)'
    )

    parser.add_argument(
        'backup_name',
        nargs='?',
        help='Backup name for restore command'
    )

    args = parser.parse_args()

    # Initialize manager
    manager = ContentManager(args.content_dir, args.backup_dir)

    print("🚀 Pelican Content Manager")
    print("=" * 40)

    try:
        if args.command == 'validate':
            issues = manager.validate_titles(args.dry_run)
            if issues:
                print(f"\n❌ Found {len(issues)} issues:")
                for issue in issues:
                    print(f"   {issue['file']}: {issue['current']}")
                    if 'fixed' in issue:
                        print(f"      Should be: {issue['fixed']}")
                return 1
            else:
                print("✅ All titles are properly formatted!")
                return 0

        elif args.command == 'fix-titles':
            fixed = manager.fix_titles(args.dry_run)
            if fixed > 0:
                print(f"\n✅ Fixed {fixed} title formatting issues!")
                if args.dry_run:
                    print("💡 Run without --dry-run to apply changes")
                return 0
            else:
                print("✅ No title formatting issues found!")
                return 0

        elif args.command == 'rename':
            renamed = manager.rename_files(args.dry_run)
            if renamed > 0:
                print(f"\n✅ Would rename {renamed} files!" if args.dry_run else f"\n✅ Renamed {renamed} files!")
                return 0
            else:
                print("✅ No files need renaming!")
                return 0

        elif args.command == 'backup':
            backup_name = args.backup_name or "manual_backup"
            manager.create_backup(backup_name)
            return 0

        elif args.command == 'restore':
            if not args.backup_name:
                print("❌ Backup name required for restore command")
                return 1
            success = manager.restore_backup(args.backup_name)
            return 0 if success else 1

        elif args.command == 'all':
            results = manager.run_all_operations(args.dry_run)

            if results['errors']:
                print("\n❌ Some errors occurred:")
                for error in results['errors']:
                    print(f"   • {error}")
                return 1

            print("\n✅ All operations completed successfully!")
            print(f"   • Titles fixed: {results['titles_fixed']}")
            print(f"   • Files renamed: {results['files_renamed']}")
            if results['backup_created']:
                print(f"   • Backup created: {results['backup_created']}")

            return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
