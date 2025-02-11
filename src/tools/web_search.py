"""Web search tool using SerpAPI."""
import os
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime
from serpapi import GoogleSearch
from dotenv import load_dotenv
from pydantic import BaseModel
from crewai.tools import BaseTool
from src.utils import web_search_logger as logger
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class WebSearchInput(BaseModel):
    """Input schema for web search tool."""
    query: str

@dataclass
class SearchResult:
    """Data class for search results with metadata."""
    title: str
    snippet: str
    link: str
    source: str
    published_date: Optional[str]
    relevance_score: float = 0.0
    reference_number: int = 0  # Added for numbered references

    def to_inline_citation(self) -> str:
        """Generate an inline citation with reference number."""
        return f"[{self.reference_number}]"

    def to_markdown(self) -> str:
        """Convert the search result to markdown format with inline citation."""
        return f"{self.snippet} {self.to_inline_citation()}"

    def to_bibliography_entry(self) -> str:
        """Generate a detailed bibliography entry."""
        date_str = f" (Published: {self.published_date})" if self.published_date else ""
        return f"[{self.reference_number}] {self.title} - {self.source}{date_str}\n    {self.link}"

class WebSearchTool(BaseTool):
    """Tool for performing web searches using SerpAPI."""
    
    name: str = "Web Search Tool"
    description: str = "Search the web for information about a given topic"
    api_key: Optional[str] = None
    min_sources: int = 3
    max_sources: int = 10
    
    def __init__(self, min_sources: int = 3, max_sources: int = 10):
        """Initialize the web search tool."""
        super().__init__()
        self.api_key = os.getenv("SERPAPI_KEY")
        self.min_sources = min_sources
        self.max_sources = max_sources
        logger.info(f"WebSearchTool initialized with min_sources={min_sources}, max_sources={max_sources}")
        
        if not self.api_key:
            logger.warning("No SERPAPI_KEY found in environment variables")
    
    def _run(self, topic: str) -> str:
        """Execute the web search for the given topic."""
        try:
            if not self.api_key:
                return "⚠️ Web search is not available - SERPAPI_KEY is missing"
                
            # Use our proper search and summarize methods
            results = self.search(topic)
            return self.summarize_results(results)
            
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}", exc_info=True)
            return f"⚠️ Web search failed: {str(e)}"

    def _calculate_relevance_score(self, result: dict) -> float:
        """Calculate a relevance score for a search result."""
        score = 1.0
        
        # Position-based score (decreases with position)
        position = result.get("position", 10)
        position_score = (11 - position) / 10
        score *= position_score
        
        # Date boost (20% boost for having a date)
        if result.get("date"):
            score *= 1.2
        
        # Rich snippet boost (10% boost)
        if result.get("rich_snippet"):
            score *= 1.1
        
        # Normalize score to be between 0 and 1
        final_score = min(max(score * 0.8, 0.0), 1.0)  # Scale down to allow for future boosts
        logger.debug(f"Calculated relevance score {final_score} for result: {result.get('title', '')}")
        return final_score

    def _extract_date(self, result: dict) -> Optional[str]:
        """Extract and format the publication date from a result."""
        date = result.get("date")
        if date:
            try:
                parsed_date = datetime.strptime(date, "%Y-%m-%d")
                formatted_date = parsed_date.strftime("%B %d, %Y")
                logger.debug(f"Extracted and formatted date: {formatted_date}")
                return formatted_date
            except ValueError:
                logger.warning(f"Failed to parse date: {date}")
                return date
        return None

    def search(self, query: str) -> List[SearchResult]:
        """Perform a web search using SerpAPI with enhanced result processing."""
        logger.info(f"Performing search for query: {query}")
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": self.max_sources * 2,  # Request more results for filtering
            "gl": "us",  # Search in US region
            "hl": "en",  # English language results
            "time": "y",  # Results from the past year
            "safe": "active",  # Safe search
            "start": 0  # Start from first page
        }
        
        try:
            logger.debug(f"Making API request with params: {params}")
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "error" in results:
                error_msg = f"Search error: {results['error']}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
            organic_results = results.get("organic_results", [])
            logger.info(f"Found {len(organic_results)} organic results")
            
            if not organic_results:
                logger.warning("No organic results found")
                return []
                
            processed_results = []
            for i, result in enumerate(organic_results, 1):
                relevance_score = self._calculate_relevance_score(result)
                processed_result = SearchResult(
                    title=result.get("title", ""),
                    snippet=result.get("snippet", ""),
                    link=result.get("link", ""),
                    source=result.get("source", result.get("displayed_link", "Unknown")),
                    published_date=self._extract_date(result),
                    relevance_score=relevance_score,
                    reference_number=i
                )
                logger.debug(f"Processed result {i}: {processed_result.title} (score: {relevance_score})")
                processed_results.append(processed_result)
            
            # Sort by relevance and take top results
            processed_results.sort(key=lambda x: x.relevance_score, reverse=True)
            # Update reference numbers after sorting
            for i, result in enumerate(processed_results[:self.max_sources], 1):
                result.reference_number = i
                
            final_results = processed_results[:self.max_sources]
            logger.info(f"Returning {len(final_results)} processed results")
            return final_results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}", exc_info=True)
            raise

    def summarize_results(self, results: List[SearchResult]) -> str:
        """Create a markdown summary of search results with inline citations."""
        logger.info(f"Summarizing {len(results)} search results")
        if not results:
            logger.warning("No results to summarize")
            return "No search results found."

        summary = "### Key Findings\n\n"
        
        # Add main content with inline citations
        for result in results:
            summary += f"- {result.to_markdown()}\n\n"
            logger.debug(f"Added finding from: {result.title}")
        
        # Add bibliography with full URLs and reference numbers
        summary += "\n### References\n\n"
        for result in results:
            summary += f"{result.to_bibliography_entry()}\n\n"
            logger.debug(f"Added reference: {result.title}")
        
        logger.info("Summary generation complete")
        return summary 