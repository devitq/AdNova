import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("AIOGRAM_BOT_TOKEN", None)

API_ENDPOINT = os.getenv("AIOGRAM_BACKEND_URL", "http://localhost:8080")

REDIS_URI = os.getenv("REDIS_URI", "redis://localhost:6379")

MINIO_URL = os.getenv('MINIO_ENDPOINT', 'http://localhost:9000')
