"""Web search tool using SerpAPI."""
import os
from typing import List, Optional
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

class WebSearchTool:
    """Tool for performing web searches using SerpAPI."""

    def __init__(self):
        """Initialize the web search tool."""
        self.api_key = os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_KEY environment variable is required")

    def search(self, query: str, num_results: int = 5) -> List[dict]:
        """
        Perform a web search using SerpAPI.
        
        Args:
            query: The search query
            num_results: Number of results to return (default: 5)
            
        Returns:
            List of search results, each containing title, snippet, and link
        """
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": num_results
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            raise Exception(f"Search error: {results['error']}")
            
        organic_results = results.get("organic_results", [])
        
        formatted_results = []
        for result in organic_results[:num_results]:
            formatted_results.append({
                "title": result.get("title", ""),
                "snippet": result.get("snippet", ""),
                "link": result.get("link", "")
            })
            
        return formatted_results

    def summarize_results(self, results: List[dict]) -> str:
        """
        Create a markdown summary of search results.
        
        Args:
            results: List of search results
            
        Returns:
            Markdown formatted summary
        """
        summary = "### Search Results\n\n"
        for i, result in enumerate(results, 1):
            summary += f"{i}. **{result['title']}**\n"
            summary += f"   {result['snippet']}\n"
            summary += f"   [Read more]({result['link']})\n\n"
        return summary 