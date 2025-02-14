"""Test script for WebSearchTool using Serper.dev."""
from dotenv import load_dotenv
import os
from src.tools.web_search import WebSearchTool
import json

# Load environment variables
load_dotenv()

def test_web_search():
    """Test the WebSearchTool implementation."""
    # Get API key
    api_key = os.getenv("SERPER_API_KEY")
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key length: {len(api_key)}")
        print(f"API Key preview: ...{api_key[-4:]}")

    # Initialize WebSearchTool
    print("\nInitializing WebSearchTool...")
    tool = WebSearchTool(min_sources=3, max_sources=5)

    # Test search
    if api_key:
        try:
            print("\nTesting search functionality...")
            query = "Latest AI developments 2024"
            print(f"Query: {query}")
            
            # Execute search using the tool's run method
            print("\nExecuting search...")
            results = tool.run(query)
            
            print("\nSearch Results:")
            print(results)
            
        except Exception as e:
            print(f"\nError during search: {str(e)}")
            print(f"Error type: {type(e).__name__}")
    else:
        print("No API key found in environment variables")

if __name__ == "__main__":
    test_web_search() 