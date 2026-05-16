from src._logprint import make_log_print
print = make_log_print(__name__)
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Configure Groq
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    print("GROQ_API_KEY not found in .env file")
    exit(1)

client = Groq(api_key=api_key)

print("Available Groq Models:\n")
print("=" * 80)

try:
    models = client.models.list()
    for model in models.data:
        print(f"\nModel ID: {model.id}")
        print(f"Object: {model.object}")
        print("-" * 80)
except Exception as e:
    print(f"Error listing models: {e}")
    print("\nAvailable Groq models:")
    print("- mixtral-8x7b-32768 (Mixtral 8x7B) - Recommended")
    print("- llama2-70b-4096 (Llama 2 70B)")
    print("- llama-3.1-70b-versatile (Llama 3.1 70B)")
    print("- gemma-7b-it (Gemma 7B)")


