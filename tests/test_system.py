#!/usr/bin/env python3
"""
Test script to verify all components are working
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    try:
        import PyPDF2
        print("  ✓ PyPDF2")
        import google.generativeai as genai
        print("  ✓ google-generativeai")
        from selenium import webdriver
        print("  ✓ selenium")
        from fastapi import FastAPI
        print("  ✓ fastapi")
        import uvicorn
        print("  ✓ uvicorn")
        
        # Test custom modules
        from src.scrapers import LinkedInScraper
        print("  ✓ linkedin_scraper")
        from src.builders import ProfileBuilder
        print("  ✓ profile_builder")
        from src.recommenders import JobRecommender
        print("  ✓ job_recommender")
        
        print("✅ All imports successful!\n")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}\n")
        return False

def test_env():
    """Test if environment variables are set"""
    print("🧪 Testing environment variables...")
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"  ✓ GEMINI_API_KEY found (length: {len(api_key)})")
        print("✅ Environment configured!\n")
        return True
    else:
        print("  ❌ GEMINI_API_KEY not found in .env file")
        print("  Create a .env file with: GEMINI_API_KEY=your_key_here\n")
        return False

def test_chromedriver():
    """Test if ChromeDriver is available"""
    print("🧪 Testing ChromeDriver...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        
        print("  ✓ ChromeDriver is working")
        print("✅ Selenium configured!\n")
        return True
    except Exception as e:
        print(f"  ❌ ChromeDriver error: {e}")
        print("  Install ChromeDriver:")
        print("    - Windows: choco install chromedriver")
        print("    - Mac: brew install chromedriver")
        print("    - Linux: sudo apt-get install chromium-chromedriver\n")
        return False

def test_gemini_api():
    """Test if Gemini API is accessible"""
    print("🧪 Testing Gemini API connection...")
    try:
        import google.generativeai as genai
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("  ❌ No API key found\n")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        response = model.generate_content("Say 'API working' if you can read this")
        
        if response.text:
            print(f"  ✓ API Response: {response.text[:50]}")
            print("✅ Gemini API working!\n")
            return True
        else:
            print("  ❌ No response from API\n")
            return False
    except Exception as e:
        print(f"  ❌ API error: {e}\n")
        return False

def test_profile_builder():
    """Test ProfileBuilder module"""
    print("🧪 Testing ProfileBuilder...")
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
            print(f"  ✓ Merged {len(unified['skills'])} skills")
            print("✅ ProfileBuilder working!\n")
            return True
        else:
            print("  ❌ Merge failed\n")
            return False
    except Exception as e:
        print(f"  ❌ ProfileBuilder error: {e}\n")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Resume Analyzer System Test")
    print("=" * 60 + "\n")
    
    results = {
        "Imports": test_imports(),
        "Environment": test_env(),
        "ChromeDriver": test_chromedriver(),
        "Gemini API": test_gemini_api(),
        "ProfileBuilder": test_profile_builder()
    }
    
    print("=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print("\n" + "=" * 60)
    
    all_passed = all(results.values())
    if all_passed:
        print("🎉 All tests passed! System is ready to use.")
        print("\nRun the application with: python app.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nRefer to SETUP.md for detailed setup instructions.")
    
    print("=" * 60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
