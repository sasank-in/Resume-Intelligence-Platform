#!/usr/bin/env python3
"""
Setup script for Resume Summarizer application
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n[SETUP] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[OK] {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("RESUME SUMMARIZER - SETUP SCRIPT")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("[ERROR] Failed to install dependencies")
        sys.exit(1)
    
    # Check .env file
    if not os.path.exists('.env'):
        print("\n[WARNING] .env file not found")
        print("Please create a .env file with your Groq API key:")
        print("GROQ_API_KEY=your_key_here")
        
        api_key = input("\nEnter your Groq API key (or press Enter to skip): ").strip()
        if api_key:
            with open('.env', 'w') as f:
                f.write(f"GROQ_API_KEY={api_key}\n")
            print("[OK] .env file created")
        else:
            print("[WARNING] Skipping .env creation - you'll need to create it manually")
    else:
        print("[OK] .env file exists")
    
    # Test imports
    print("\n[SETUP] Testing imports...")
    try:
        from app.config import GROQ_API_KEY
        from groq import Groq
        import fastapi
        import uvicorn
        print("[OK] All imports successful")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nTo start the application:")
    print("  python main.py")
    print("\nThen open your browser to:")
    print("  http://localhost:8000")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()