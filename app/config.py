"""Configuration settings for Resume Summarizer."""
import os
from dotenv import load_dotenv

load_dotenv()


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

MAX_FILE_SIZE = _get_int("MAX_FILE_SIZE", 10 * 1024 * 1024)
ALLOWED_FILE_TYPES = [".pdf"]

# Per-LLM-call timeout (seconds). Distinct from session lifetime.
REQUEST_TIMEOUT = _get_int("REQUEST_TIMEOUT", 60)
# Idle session lifetime (seconds). Default 1 hour.
SESSION_TIMEOUT = _get_int("SESSION_TIMEOUT", 3600)
# How often the background sweeper runs (seconds).
SESSION_CLEANUP_INTERVAL = _get_int("SESSION_CLEANUP_INTERVAL", 300)

# Rate limiting (slowapi format: "<count>/<period>")
RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "60/minute")
RATE_LIMIT_UPLOAD = os.getenv("RATE_LIMIT_UPLOAD", "10/minute")
RATE_LIMIT_LLM = os.getenv("RATE_LIMIT_LLM", "30/minute")

# Session backend: "memory" (default) or "redis"
SESSION_BACKEND = os.getenv("SESSION_BACKEND", "memory").lower()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_JSON = os.getenv("LOG_JSON", "false").lower() == "true"

# CORS
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

APP_TITLE = "Resume Summarizer"
APP_DESCRIPTION = "AI-powered resume analysis and job recommendation system"
APP_VERSION = "1.1.0"

STATIC_DIR = "static"
UPLOAD_DIR = "uploads"

# Environment: "development" | "production"
ENV = os.getenv("ENV", "development").lower()
IS_PROD = ENV == "production"
