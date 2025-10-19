import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_DIR, "..", "content")
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
