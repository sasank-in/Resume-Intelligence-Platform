import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure Gemini AI
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("GEMINI_API_KEY not found in .env file")
    exit(1)

genai.configure(api_key=api_key)

print("Available Gemini Models:\n")
print("=" * 80)

for model in genai.list_models():
    print(f"\nModel: {model.name}")
    print(f"Display Name: {model.display_name}")
    print(f"Description: {model.description}")
    print(f"Version: {model.version}")
    print(f"Supported Methods: {model.supported_generation_methods}")
    print("-" * 80)
