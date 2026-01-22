import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", 10))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "youtube_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
VIDEO_TABLE = os.getenv("VIDEO_TABLE", "youtube_videos")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
TEST_MODE = os.getenv("TEST_MODE", "False").lower() in ("true", "1")
