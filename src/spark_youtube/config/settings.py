"""
Configuration Management for SparkYouTube AI Blog System

Centralized configuration management with environment variable support,
validation, and default values according to project specifications.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

@dataclass
class ProjectConfig:
    """Project configuration with validation and defaults."""

    # API Configuration
    gemini_api_key: str = field(default_factory=lambda: os.getenv('GEMINI_API_KEY', ''))
    gemini_model: str = field(default='models/gemini-2.5-flash')

    # Directory Configuration
    project_root: Path = field(default_factory=lambda: Path.cwd())
    content_dir: Path = field(default_factory=lambda: Path('content/posts'))
    thumbnails_dir: Path = field(default_factory=lambda: Path('content/thumbnails'))
    logs_dir: Path = field(default_factory=lambda: Path('logs'))
    output_dir: Path = field(default_factory=lambda: Path('output'))

    # Processing Configuration
    batch_delay: float = field(default=3.0)  # Seconds between batch processing
    max_retries: int = field(default=3)
    request_timeout: int = field(default=30)

    # Content Configuration
    default_category: str = field(default='General')
    default_author: str = field(default='AI Generated')
    supported_languages: list = field(default_factory=lambda: ['en', 'zh-cn', 'zh-tw'])

    # Logging Configuration
    log_level: str = field(default='INFO')
    log_format: str = field(default='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_paths()
        self._validate_api_config()
        self._setup_logging()

    def _validate_paths(self):
        """Ensure all required directories exist."""
        for dir_path in [self.content_dir, self.thumbnails_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _validate_api_config(self):
        """Validate API configuration."""
        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Please set it with: export GEMINI_API_KEY='your_key_here'"
            )

    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format=self.log_format,
            handlers=[
                logging.FileHandler(self.logs_dir / 'spark_youtube.log'),
                logging.StreamHandler()
            ]
        )

    @property
    def log_file(self) -> Path:
        """Get current log file path."""
        return self.logs_dir / 'spark_youtube.log'

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization."""
        return {
            'gemini_model': self.gemini_model,
            'content_dir': str(self.content_dir),
            'thumbnails_dir': str(self.thumbnails_dir),
            'logs_dir': str(self.logs_dir),
            'output_dir': str(self.output_dir),
            'batch_delay': self.batch_delay,
            'max_retries': self.max_retries,
            'default_category': self.default_category,
            'default_author': self.default_author,
            'supported_languages': self.supported_languages,
        }


# Global configuration instance
_config_instance: Optional[ProjectConfig] = None

def get_config() -> ProjectConfig:
    """Get or create global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = ProjectConfig()
    return _config_instance

def reload_config():
    """Reload configuration (useful for testing)."""
    global _config_instance
    _config_instance = ProjectConfig()

# Convenience functions for common paths
def get_content_dir() -> Path:
    """Get content directory path."""
    return get_config().content_dir

def get_thumbnails_dir() -> Path:
    """Get thumbnails directory path."""
    return get_config().thumbnails_dir

def get_logs_dir() -> Path:
    """Get logs directory path."""
    return get_config().logs_dir

def get_output_dir() -> Path:
    """Get output directory path."""
    return get_config().output_dir
