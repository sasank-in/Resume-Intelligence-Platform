"""Shared pytest fixtures."""
import os
import sys
from unittest.mock import MagicMock, patch

# Ensure project root is on path so `from app...` and `from main import app` work
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Provide a fake Groq key BEFORE any module imports config
os.environ.setdefault("GROQ_API_KEY", "test-key-not-real")
os.environ.setdefault("ENV", "test")
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault("SESSION_BACKEND", "memory")
# Disable rate limiting in tests by setting a very high cap
os.environ.setdefault("RATE_LIMIT_DEFAULT", "10000/minute")
os.environ.setdefault("RATE_LIMIT_UPLOAD", "10000/minute")
os.environ.setdefault("RATE_LIMIT_LLM", "10000/minute")

import pytest
from fastapi.testclient import TestClient


def _fake_chat_completion(content="OK"):
    """Build a fake groq response object shaped like the real one."""
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = content
    return resp


@pytest.fixture
def mock_groq():
    """Patch Groq client at the modules that import it."""
    with patch("app.services.client") as svc_client, \
         patch("src.utils.ats_checker.Groq") as ats_groq, \
         patch("src.recommenders.job_recommender.Groq", create=True) as rec_groq:
        svc_client.chat.completions.create.return_value = _fake_chat_completion(
            '{"name": "Test Candidate", "email": "test@example.com", '
            '"skills": ["python"], "experience": [], "education": []}'
        )
        ats_groq.return_value = MagicMock()
        rec_groq.return_value = MagicMock()
        yield {
            "services": svc_client,
            "ats": ats_groq,
            "recommender": rec_groq,
        }


@pytest.fixture
def client(mock_groq):
    """FastAPI TestClient with lifespan started and Groq mocked."""
    from main import app
    with TestClient(app) as c:
        yield c
