"""
Pelican Integration Module

Handles saving AI-generated posts to Pelican's content directory.
Ensures proper file naming, front matter validation, and integration with Pelican workflow.
"""

import asyncio
import aiofiles
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class PelicanIntegrationError(Exception):
    """Custom exception for Pelican integration errors."""
    pass

async def save_markdown_post(
    post_data: Dict[str, str],
    content_dir: Path,
    filename_template: str = "{date}-{slug}.md",
    ensure_unique: bool = True
) -> str:
    """
    Save an AI-generated post to Pelican's content/posts directory.

    Args:
        post_data: Dictionary containing post data (title, content, slug, etc.)
        content_dir: Path to the content/posts directory
        filename_template: Template for filename generation
        ensure_unique: Whether to ensure unique filenames

    Returns:
        The filename of the saved post

    Raises:
        PelicanIntegrationError: If saving fails
    """
    try:
        # Generate filename
        filename = _generate_filename(
            post_data, filename_template, ensure_unique, content_dir
        )

        # Full path to save the post
        file_path = content_dir / filename

        # Create content directory if it doesn't exist
        content_dir.mkdir(parents=True, exist_ok=True)

        # Write the post content
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(post_data['content'])

        logger.info(f"✅ Post saved successfully: {filename}")
        return filename

    except Exception as e:
        logger.error(f"❌ Failed to save post: {str(e)}")
        raise PelicanIntegrationError(f"Failed to save post: {str(e)}")

def _generate_filename(
    post_data: Dict[str, str],
    template: str,
    ensure_unique: bool,
    content_dir: Path
) -> str:
    """Generate a unique filename for the post."""
    # Extract components for filename
    slug = post_data.get('slug', 'untitled')
    date = datetime.now().strftime('%Y-%m-%d')

    # Format the template
    filename = template.format(
        slug=slug,
        date=date,
        title=post_data.get('title', 'Untitled'),
        youtube_id=post_data.get('youtube_id', 'unknown')
    )

    # Ensure .md extension
    if not filename.endswith('.md'):
        filename += '.md'

    # Ensure uniqueness if requested
    if ensure_unique:
        base_name = filename[:-3]  # Remove .md
        counter = 1
        while (content_dir / filename).exists():
            filename = f"{base_name}-{counter}.md"
            counter += 1

    return filename

async def validate_pelican_front_matter(post_content: str) -> Dict[str, any]:
    """
    Validate that the front matter is valid for Pelican.

    Args:
        post_content: Full markdown content with front matter

    Returns:
        Dict with validation results
    """
    validation_results = {
        "valid": True,
        "warnings": [],
        "errors": []
    }

    try:
        # Extract front matter (between --- markers)
        if not post_content.startswith('---'):
            validation_results["valid"] = False
            validation_results["errors"].append("Content must start with --- for front matter")
            return validation_results

        # Find the second ---
        front_matter_end = post_content.find('---', 4)
        if front_matter_end == -1:
            validation_results["valid"] = False
            validation_results["errors"].append("Front matter must end with ---")
            return validation_results

        front_matter = post_content[4:front_matter_end].strip()
        content_body = post_content[front_matter_end + 3:].strip()

        # Parse YAML front matter (simplified - assuming simple key: value format)
        front_matter_dict = {}
        for line in front_matter.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                front_matter_dict[key.strip()] = value.strip()

        # Validate required fields
        required_fields = ['title', 'date', 'author']
        for field in required_fields:
            if field not in front_matter_dict:
                validation_results["valid"] = False
                validation_results["errors"].append(f"Missing required field: {field}")
            elif not front_matter_dict[field]:
                validation_results["valid"] = False
                validation_results["errors"].append(f"Required field '{field}' is empty")

        # Validate title (should not have quotes)
        if 'title' in front_matter_dict:
            title = front_matter_dict['title']
            if title.startswith('"') and title.endswith('"'):
                validation_results["warnings"].append("Title should not be wrapped in quotes")

        # Validate date format (should be ISO-like)
        if 'date' in front_matter_dict:
            try:
                datetime.fromisoformat(front_matter_dict['date'])
            except ValueError:
                validation_results["warnings"].append("Date should be in ISO format (YYYY-MM-DDTHH:MM:SS)")

        # Check content presence
        if not content_body:
            validation_results["warnings"].append("Post body appears to be empty")

        validation_results["front_matter"] = front_matter_dict
        validation_results["content_length"] = len(content_body)

    except Exception as e:
        validation_results["valid"] = False
        validation_results["errors"].append(f"Front matter parsing error: {str(e)}")

    return validation_results

async def get_pelican_posts_info(content_dir: Path) -> Dict[str, any]:
    """
    Get information about existing Pelican posts.

    Args:
        content_dir: Path to content/posts directory

    Returns:
        Dict with post statistics and recent posts
    """
    try:
        if not content_dir.exists():
            return {"total_posts": 0, "recent_posts": [], "files": []}

        markdown_files = list(content_dir.glob('*.md'))
        posts_info = []

        for file_path in markdown_files:
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()

                # Extract basic info from front matter
                validation = await validate_pelican_front_matter(content)

                if validation["valid"]:
                    front_matter = validation.get("front_matter", {})
                    posts_info.append({
                        "filename": file_path.name,
                        "title": front_matter.get("title", "Unknown"),
                        "date": front_matter.get("date", "Unknown"),
                        "author": front_matter.get("author", "Unknown"),
                        "category": front_matter.get("category", "General"),
                        "tags": front_matter.get("tags", "").split(", ") if front_matter.get("tags") else [],
                        "content_length": validation.get("content_length", 0)
                    })
            except Exception as e:
                logger.warning(f"Could not read post {file_path.name}: {str(e)}")

        # Sort by date (recent first)
        try:
            posts_info.sort(
                key=lambda x: datetime.fromisoformat(x["date"]) if x["date"] != "Unknown" else datetime.min,
                reverse=True
            )
        except Exception:
            # If sorting fails, keep original order
            pass

        return {
            "total_posts": len(markdown_files),
            "processed_posts": len(posts_info),
            "recent_posts": posts_info[:10],  # Last 10 posts
            "all_files": [f.name for f in markdown_files]
        }

    except Exception as e:
        logger.error(f"Error getting Pelican posts info: {str(e)}")
        return {"error": str(e)}

async def cleanup_generated_posts(
    content_dir: Path,
    prefix: str = "ai-",
    older_than_days: int = 30
) -> Dict[str, any]:
    """
    Clean up old AI-generated posts to prevent content directory bloat.

    Args:
        content_dir: Path to content/posts directory
        prefix: Prefix used for AI-generated posts
        older_than_days: Remove files older than this many days

    Returns:
        Dict with cleanup statistics
    """
    import time

    stats = {
        "files_found": 0,
        "files_deleted": 0,
        "errors": []
    }

    try:
        if not content_dir.exists():
            return stats

        current_time = time.time()
        cutoff_time = current_time - (older_than_days * 24 * 60 * 60)

        for file_path in content_dir.glob(f"{prefix}*.md"):
            stats["files_found"] += 1

            try:
                # Check file modification time
                file_time = file_path.stat().st_mtime

                if file_time < cutoff_time:
                    # Delete the file
                    file_path.unlink()
                    stats["files_deleted"] += 1
                    logger.info(f"Deleted old AI post: {file_path.name}")

            except Exception as e:
                stats["errors"].append(f"Error deleting {file_path.name}: {str(e)}")

    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        stats["errors"].append(f"Cleanup error: {str(e)}")

    return stats
