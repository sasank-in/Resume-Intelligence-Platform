"""Lightweight smoke tests. CI-safe: real external calls are skipped if unavailable."""
import os

import pytest


def test_imports():
    """All core modules import."""
    from pypdf import PdfReader  # noqa: F401
    from groq import Groq  # noqa: F401
    from fastapi import FastAPI  # noqa: F401
    import uvicorn  # noqa: F401

    from src.scrapers import LinkedInScraper  # noqa: F401
    from src.builders import ProfileBuilder  # noqa: F401
    from src.recommenders import JobRecommender  # noqa: F401


def test_env_loaded():
    """GROQ_API_KEY is set (real or test placeholder)."""
    assert os.getenv("GROQ_API_KEY"), "GROQ_API_KEY must be set"


@pytest.mark.skipif(
    os.getenv("RUN_SELENIUM_TESTS") != "1",
    reason="Selenium/Chrome not available in CI; set RUN_SELENIUM_TESTS=1 to enable",
)
def test_chromedriver():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=opts)
    driver.quit()


@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY", "").startswith("test-"),
    reason="Real GROQ_API_KEY not set; skipping live API call",
)
def test_groq_api_live():
    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": "Say 'API working'"}],
        temperature=0.7,
        max_tokens=20,
    )
    assert response.choices[0].message.content


def test_profile_builder_merge():
    from src.builders import ProfileBuilder

    resume = {
        "name": "John Doe",
        "skills": ["Python", "JavaScript"],
        "experience": [{"title": "Engineer", "company": "Tech Corp"}],
    }
    linkedin = {
        "name": "John Doe",
        "skills": ["Python", "React"],
        "experience": [{"title": "Engineer", "company": "Tech Corp"}],
    }

    unified = ProfileBuilder.merge_profiles(resume, linkedin)
    assert unified
    assert "skills" in unified
    assert len(unified["skills"]) >= 2
