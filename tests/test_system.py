#!/usr/bin/env python3
"""
System test suite for Resume Summarizer application.
Validates all components are working correctly before deployment.
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv


def test_imports():
    """Test if all required modules can be imported"""
    print("[TEST] Checking imports...")
    try:
        import PyPDF2
        print("  [PASS] PyPDF2")
        from groq import Groq
        print("  [PASS] groq")
        from selenium import webdriver
        print("  [PASS] selenium")
        from fastapi import FastAPI
        print("  [PASS] fastapi")
        import uvicorn
        print("  [PASS] uvicorn")
        
        # Test custom modules
        from src.scrapers import LinkedInScraper
        print("  [PASS] linkedin_scraper")
        from src.builders import ProfileBuilder
        print("  [PASS] profile_builder")
        from src.recommenders import JobRecommender
        print("  [PASS] job_recommender")
        
        print("[OK] All imports successful!\n")
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}\n")
        return False


def test_env():
    """Test if environment variables are set"""
    print("[TEST] Checking environment variables...")
    
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        print(f"  [PASS] GROQ_API_KEY found (length: {len(api_key)})")
        print("[OK] Environment configured!\n")
        return True
    else:
        print("  [FAIL] GROQ_API_KEY not found in .env file")
        print("  [INFO] Create a .env file with: GROQ_API_KEY=your_key_here\n")
        return False


def test_chromedriver():
    """Test if ChromeDriver is available"""
    print("[TEST] Checking ChromeDriver...")
    try:
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        
        print("  [PASS] ChromeDriver is working")
        print("[OK] Selenium configured!\n")
        return True
    except Exception as e:
        print(f"  [FAIL] ChromeDriver error: {e}")
        print("  [INFO] Install ChromeDriver:")
        print("    - Windows: choco install chromedriver")
        print("    - Mac: brew install chromedriver")
        print("    - Linux: sudo apt-get install chromium-chromedriver\n")
        return False


def test_groq_api():
    """Test if Groq API is accessible"""
    print("[TEST] Testing Groq API connection...")
    try:
        from groq import Groq
        
        load_dotenv()
        
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print("  [FAIL] No API key found\n")
            return False
        
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": "Say 'API working' if you can read this"}],
            temperature=0.7
        )
        
        if response.choices[0].message.content:
            print(f"  [PASS] API Response: {response.choices[0].message.content[:50]}")
            print("[OK] Groq API working!\n")
            return True
        else:
            print("  [FAIL] No response from API\n")
            return False
    except Exception as e:
        print(f"  [FAIL] API error: {e}\n")
        return False


def test_profile_builder():
    """Test ProfileBuilder module"""
    print("[TEST] Testing ProfileBuilder...")
    try:
        from src.builders import ProfileBuilder
        
        # Test data
        resume_data = {
            "name": "John Doe",
            "skills": ["Python", "JavaScript"],
            "experience": [{"title": "Engineer", "company": "Tech Corp"}]
        }
        
        linkedin_data = {
            "name": "John Doe",
            "skills": ["Python", "React"],
            "experience": [{"title": "Engineer", "company": "Tech Corp"}]
        }
        
        # Test merge
        unified = ProfileBuilder.merge_profiles(resume_data, linkedin_data)
        
        if unified and "skills" in unified:
            print(f"  [PASS] Merged {len(unified['skills'])} skills")
            print("[OK] ProfileBuilder working!\n")
            return True
        else:
            print("  [FAIL] Merge failed\n")
            return False
    except Exception as e:
        print(f"  [FAIL] ProfileBuilder error: {e}\n")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("RESUME SUMMARIZER - SYSTEM TEST SUITE")
    print("=" * 70 + "\n")
    
    results = {
        "Imports": test_imports(),
        "Environment": test_env(),
        "ChromeDriver": test_chromedriver(),
        "Groq API": test_groq_api(),
        "ProfileBuilder": test_profile_builder()
    }
    
    print("=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name:20} {status}")
    
    print("\n" + "=" * 70)
    
    all_passed = all(results.values())
    if all_passed:
        print("[SUCCESS] All tests passed! System is ready to use.")
        print("\nRun the application with: python main.py")
    else:
        print("[WARNING] Some tests failed. Please fix the issues above.")
        print("\nRefer to README.md for detailed setup instructions.")
    
    print("=" * 70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
