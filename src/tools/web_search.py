"""Web search tool using Serper.dev."""
import os
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.utils import web_search_logger as logger
from crewai_tools import SerperDevTool
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SearchResult(BaseModel):
    """Represents a single search result."""
    title: str
    snippet: str
    link: str
    source: Optional[str] = None
    published_date: Optional[str] = None
    relevance_score: float = 1.0
    reference_number: int = 1

    def to_inline_citation(self) -> str:
        """Format result as an inline citation."""
        return f"{self.snippet} [{self.reference_number}]"

    def to_markdown(self) -> str:
        """Format result in markdown."""
        return f"- {self.snippet} [[{self.reference_number}]]({self.link})"

    def to_bibliography_entry(self) -> str:
        """Format result as a bibliography entry."""
        date_str = f" ({self.published_date})" if self.published_date else ""
        return f"[{self.reference_number}] {self.title}. {self.source or 'Source'}{date_str}. Available at: {self.link}"

class WebSearchTool(SerperDevTool):
    """Tool for performing web searches using Serper.dev.
    
    This tool extends SerperDevTool to provide web search capabilities using the Serper.dev API.
    It includes additional formatting and error handling specific to our application's needs.
    """
    
    name: str = "Web Search"
    description: str = "Search the web for current information on a given topic"
    min_sources: int = Field(default=3, description="Minimum number of sources to return")
    max_sources: int = Field(default=10, description="Maximum number of sources to return")
    
    def __init__(self, min_sources: int = 3, max_sources: int = 10):
        """Initialize the web search tool.
        
        Args:
            min_sources (int): Minimum number of sources to return
            max_sources (int): Maximum number of sources to return
        """
        super().__init__()
        self.min_sources = min_sources
        self.max_sources = max_sources
        logger.info(f"WebSearchTool initialized with min_sources={min_sources}, max_sources={max_sources}")
        
        # Check if API key is available
        if not os.getenv("SERPER_API_KEY"):
            logger.warning("No SERPER_API_KEY found in environment variables")

    def _calculate_relevance_score(self, result: dict) -> float:
        """Calculate relevance score for a search result."""
        score = 1.0
        
        # Position-based scoring (higher positions get higher scores)
        position = result.get('position', 10)
        position_score = (11 - min(position, 10)) / 10
        score *= position_score
        
        # Bonus for rich snippets
        if result.get('rich_snippet'):
            score *= 1.2
            
        # Date-based scoring if available
        if 'date' in result:
            try:
                date = datetime.strptime(result['date'], '%Y-%m-%d')
                days_old = (datetime.now() - date).days
                # Newer results get higher scores
                if days_old <= 30:  # Very recent (last month)
                    date_factor = 1.2
                elif days_old <= 90:  # Recent (last quarter)
                    date_factor = 1.1
                elif days_old <= 365:  # Within a year
                    date_factor = 1.0
                else:  # Older than a year
                    date_factor = 0.9
                score *= date_factor
            except ValueError:
                pass
                
        return score

    def _extract_date(self, result: dict) -> Optional[str]:
        """Extract and format the publication date."""
        if 'date' in result:
            try:
                date = datetime.strptime(result['date'], '%Y-%m-%d')
                return date.strftime('%B %d, %Y')
            except ValueError:
                return result['date']
        return None

    def search(self, query: str) -> List[SearchResult]:
        """Execute the web search for the given topic."""
        try:
            if not os.getenv("SERPER_API_KEY"):
                raise ValueError("SERPER_API_KEY is missing")
            
            # Call parent's run method to perform the search
            raw_results = super().run(query)
            
            if not raw_results:
                return []
            
            # Parse and process results
            results = []
            for i, result in enumerate(raw_results.split('\n'), 1):
                if not result.strip():
                    continue
                    
                # Create SearchResult object
                search_result = SearchResult(
                    title=result,
                    snippet=result,
                    link=f"Source {i}",  # Placeholder as SerperDevTool doesn't provide links
                    reference_number=i
                )
                results.append(search_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error during web search: {str(e)}")
            raise Exception(f"Search error: {str(e)}")

    def summarize_results(self, results: List[SearchResult]) -> str:
        """Summarize search results with proper formatting."""
        if not results:
            return "No search results found."
            
        # Sort results by relevance score
        sorted_results = sorted(results, key=lambda x: x.relevance_score, reverse=True)
        
        # Update reference numbers after sorting
        for i, result in enumerate(sorted_results, 1):
            result.reference_number = i
        
        # Format summary
        summary_parts = []
        
        # Add key findings
        summary_parts.append("### Key Findings")
        for result in sorted_results:
            summary_parts.append(result.to_markdown())
        
        # Add bibliography
        summary_parts.append("\n### References")
        for result in sorted_results:
            summary_parts.append(result.to_bibliography_entry())
        
        return "\n\n".join(summary_parts) 