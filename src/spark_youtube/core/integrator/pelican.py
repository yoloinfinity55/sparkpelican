"""
Pelican Integration Module

Handles saving AI-generated blog posts to Pelican content directory
with proper front matter formatting and metadata management.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from spark_youtube.config.settings import get_config

logger = logging.getLogger(__name__)
config = get_config()

class PelicanIntegrationError(Exception):
    """Custom exception for Pelican integration errors."""
    pass

class PelicanIntegrator:
    """Handles Pelican blog post creation and management."""

    def __init__(self):
        """Initialize Pelican integrator."""
        self.content_dir = config.content_dir
        self.content_dir.mkdir(parents=True, exist_ok=True)

    def validate_post_data(self, post_data: Dict[str, Any]) -> None:
        """
        Validate post data before saving.

        Args:
            post_data: Dictionary containing post information

        Raises:
            PelicanIntegrationError: If required fields are missing or invalid
        """
        required_fields = ['title', 'content', 'filename', 'category', 'tags']

        for field in required_fields:
            if field not in post_data:
                raise PelicanIntegrationError(f"Missing required field: {field}")

        # Validate filename format
        if not post_data['filename'].endswith('.md'):
            raise PelicanIntegrationError("Filename must end with .md")

        # Validate tags format
        if not isinstance(post_data['tags'], list):
            raise PelicanIntegrationError("Tags must be a list")

        logger.info(f"✅ Post data validation passed for: {post_data['title']}")

    def generate_filename(self, title: str, date_prefix: Optional[str] = None) -> str:
        """
        Generate Pelican-compatible filename.

        Args:
            title: Post title
            date_prefix: Optional date prefix (YYYY-MM-DD format)

        Returns:
            Filename in format: YYYY-MM-DD-title-slug.md
        """
        if not date_prefix:
            date_prefix = datetime.now().strftime("%Y-%m-%d")

        # Generate slug from title
        slug = self._generate_slug(title)

        return f"{date_prefix}-{slug}.md"

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title."""
        import re

        if not title:
            return 'untitled'

        # Convert to lowercase and replace spaces with hyphens
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special characters
        slug = re.sub(r'[\s_]+', '-', slug)   # Replace spaces/underscores with hyphens
        slug = slug.strip('-')

        return slug[:50]  # Limit length

    def create_front_matter(self, post_data: Dict[str, Any]) -> str:
        """
        Create Pelican front matter from post data.

        Args:
            post_data: Dictionary containing post metadata

        Returns:
            YAML front matter string
        """
        # Required fields
        front_matter_lines = [
            f"title: {post_data['title']}",
            f"date: {post_data.get('date', datetime.now().isoformat())}",
            f"author: {post_data.get('author', config.default_author)}",
            f"category: {post_data['category']}",
            f"tags: {', '.join(post_data['tags'])}",
            f"slug: {post_data.get('slug', self._generate_slug(post_data['title']))}",
        ]

        # Optional fields
        if 'youtube_id' in post_data:
            front_matter_lines.append(f"youtube_id: {post_data['youtube_id']}")

        if 'summary' in post_data:
            # Escape quotes in summary for YAML
            summary = post_data['summary'].replace('"', '\\"')
            front_matter_lines.append(f'summary: "{summary}"')

        if 'youtube_thumbnail' in post_data and post_data['youtube_thumbnail']:
            # Convert absolute path to relative path for Pelican
            thumbnail_path = Path(post_data['youtube_thumbnail'])
            try:
                # Get relative path from content directory
                relative_path = thumbnail_path.relative_to(self.content_dir.parent)
                front_matter_lines.append(f"image: {relative_path}")
            except ValueError:
                # Fallback to basename if path is not relative to content dir
                front_matter_lines.append(f"image: {thumbnail_path.name}")

        if 'language' in post_data:
            front_matter_lines.append(f"language: {post_data['language']}")

        return '\n'.join(front_matter_lines)

    def save_post(self, post_data: Dict[str, Any]) -> str:
        """
        Save blog post to Pelican content directory.

        Args:
            post_data: Dictionary containing post information

        Returns:
            Path to saved file

        Raises:
            PelicanIntegrationError: If saving fails
        """
        try:
            # Validate post data
            self.validate_post_data(post_data)

            # Generate filename if not provided
            filename = post_data.get('filename') or self.generate_filename(
                post_data['title']
            )

            # Create full file path
            file_path = self.content_dir / filename

            # Create front matter
            front_matter = self.create_front_matter(post_data)

            # Combine front matter with content
            full_content = f"---\n{front_matter}---\n\n"

            # Add summary if provided
            if 'summary' in post_data:
                full_content += f"{post_data['summary']}\n\n"

            # Add main content
            if 'content' in post_data:
                full_content += post_data['content']

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_content)

            logger.info(f"✅ Post saved successfully: {file_path}")
            return str(file_path)

        except Exception as e:
            error_msg = f"Failed to save post: {str(e)}"
            logger.error(error_msg)
            raise PelicanIntegrationError(error_msg)

    def check_existing_post(self, youtube_id: str) -> Optional[str]:
        """
        Check if a post already exists for the given YouTube video.

        Args:
            youtube_id: YouTube video ID

        Returns:
            Path to existing post file, or None if not found
        """
        try:
            # Look for markdown files containing the YouTube ID
            for md_file in self.content_dir.glob('*.md'):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if f"youtube_id: {youtube_id}" in content:
                        logger.info(f"📄 Found existing post for video {youtube_id}: {md_file}")
                        return str(md_file)

                except Exception as e:
                    logger.warning(f"Error reading {md_file}: {e}")
                    continue

            return None

        except Exception as e:
            logger.error(f"Error checking existing posts: {e}")
            return None

    def update_post(self, post_data: Dict[str, Any]) -> str:
        """
        Update an existing post or create new if it doesn't exist.

        Args:
            post_data: Dictionary containing post information

        Returns:
            Path to saved/updated file
        """
        youtube_id = post_data.get('youtube_id')

        if youtube_id:
            existing_post = self.check_existing_post(youtube_id)
            if existing_post:
                logger.info(f"🔄 Updating existing post for video {youtube_id}")
                # For now, we'll create a new file with timestamp to avoid conflicts
                # In a full implementation, you might want to replace the existing file
                post_data['filename'] = self.generate_filename(
                    post_data['title'],
                    datetime.now().strftime("%Y-%m-%d")
                )

        return self.save_post(post_data)

    def get_post_stats(self) -> Dict[str, int]:
        """
        Get statistics about posts in the content directory.

        Returns:
            Dictionary with post statistics
        """
        try:
            total_posts = 0
            posts_by_category = {}
            posts_by_language = {}

            for md_file in self.content_dir.glob('*.md'):
                total_posts += 1

                try:
                    # Extract metadata from front matter
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Simple front matter parsing
                    category = self._extract_front_matter_field(content, 'category')
                    language = self._extract_front_matter_field(content, 'language')

                    if category:
                        posts_by_category[category] = posts_by_category.get(category, 0) + 1

                    if language:
                        posts_by_language[language] = posts_by_language.get(language, 0) + 1

                except Exception as e:
                    logger.warning(f"Error parsing metadata from {md_file}: {e}")

            return {
                'total_posts': total_posts,
                'posts_by_category': posts_by_category,
                'posts_by_language': posts_by_language
            }

        except Exception as e:
            logger.error(f"Error getting post stats: {e}")
            return {'total_posts': 0, 'posts_by_category': {}, 'posts_by_language': {}}

    def _extract_front_matter_field(self, content: str, field: str) -> Optional[str]:
        """Extract a field from front matter."""
        import re

        # Look for front matter pattern
        pattern = rf'{field}:\s*(.+?)(?:\n|$)'
        match = re.search(pattern, content)

        if match:
            value = match.group(1).strip()
            # Remove quotes if present
            value = value.strip('"').strip("'")
            return value

        return None

    def validate_pelican_structure(self) -> Dict[str, Any]:
        """
        Validate that the Pelican project structure is correct.

        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []

        # Check required directories
        required_dirs = {
            'content': config.content_dir,
            'output': config.output_dir,
            'logs': config.logs_dir,
            'thumbnails': config.thumbnails_dir
        }

        for name, dir_path in required_dirs.items():
            if not dir_path.exists():
                issues.append(f"Missing required directory: {dir_path}")
            else:
                # Check if directory is writable
                try:
                    test_file = dir_path / '.test_write'
                    test_file.write_text('test')
                    test_file.unlink()
                except Exception:
                    issues.append(f"Directory not writable: {dir_path}")

        # Check for Pelican configuration files
        pelican_configs = ['pelicanconf.py', 'publishconf.py']
        for config_file in pelican_configs:
            config_path = Path(config_file)
            if not config_path.exists():
                warnings.append(f"Pelican config file not found: {config_file}")

        # Check for theme directory
        themes_dir = Path('themes')
        if not themes_dir.exists():
            warnings.append("No themes directory found")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

# Convenience functions
async def save_markdown_post(post_data: Dict[str, Any], content_dir: Optional[Path] = None) -> str:
    """
    Save a markdown post to the content directory.

    Args:
        post_data: Dictionary containing post information
        content_dir: Optional content directory (uses config default if not provided)

    Returns:
        Path to saved file
    """
    integrator = PelicanIntegrator()
    if content_dir:
        integrator.content_dir = content_dir

    return integrator.save_post(post_data)

def get_post_stats() -> Dict[str, int]:
    """Get statistics about posts in the content directory."""
    integrator = PelicanIntegrator()
    return integrator.get_post_stats()

def validate_pelican_structure() -> Dict[str, Any]:
    """Validate Pelican project structure."""
    integrator = PelicanIntegrator()
    return integrator.validate_pelican_structure()
