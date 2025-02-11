from dotenv import load_dotenv
import os

load_dotenv()

print("Environment variables:")
print(f"SERPAPI_KEY: {'*' * 8}{os.getenv('SERPAPI_KEY')[-4:] if os.getenv('SERPAPI_KEY') else 'Not found'}")
print(f"OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL', 'Not found')}")
print(f"OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'Not found')}")
print(f"LOG_LEVEL: {os.getenv('LOG_LEVEL', 'Not found')}") 