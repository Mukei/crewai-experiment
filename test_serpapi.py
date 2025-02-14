from serpapi import GoogleSearch
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("SERPAPI_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API Key length: {len(api_key)}")
    print(f"API Key preview: ...{api_key[-4:]}")

# Test search with more parameters
if api_key:
    try:
        params = {
            "engine": "google",
            "q": "Latest AI developments 2024",
            "api_key": api_key,
            "num": 5,
            "gl": "us",  # Search in US region
            "hl": "en",  # English language results
            "google_domain": "google.com",
            "safe": "active"  # Safe search
        }
        print("\nMaking API request with parameters:")
        print(json.dumps(params, indent=2))
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            print(f"\nAPI Error Response:")
            print(json.dumps(results, indent=2))
        else:
            print("\nSearch successful!")
            organic_results = results.get('organic_results', [])
            print(f"Found {len(organic_results)} organic results")
            
            if organic_results:
                print("\nFirst result preview:")
                first_result = organic_results[0]
                print(f"Title: {first_result.get('title', 'N/A')}")
                print(f"Snippet: {first_result.get('snippet', 'N/A')}")
            else:
                print("\nNo organic results found in response")
                print("Full response keys:", list(results.keys()))
                
    except Exception as e:
        print(f"\nError during search: {str(e)}")
        print(f"Error type: {type(e).__name__}")
else:
    print("No API key found in environment variables") 