"""
Configuration settings for Resume Summarizer application
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

GROQ_MODEL = 'openai/gpt-oss-120b'

# File Upload Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ['.pdf']

# Rate Limiting Configuration
MAX_REQUESTS_PER_MINUTE = 30
REQUEST_TIMEOUT = 60  # seconds

# Application Settings
APP_TITLE = "Resume Summarizer"
APP_DESCRIPTION = "AI-powered resume analysis and job recommendation system"
APP_VERSION = "1.0.0"

# Directory Configuration
STATIC_DIR = "static"
UPLOAD_DIR = "uploads"
