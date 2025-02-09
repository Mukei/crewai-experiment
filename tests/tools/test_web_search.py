"""Tests for the WebSearchTool class."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.tools.web_search import WebSearchTool, SearchResult

@pytest.fixture
def mock_serpapi():
    """Mock SerpAPI responses."""
    with patch("src.tools.web_search.GoogleSearch") as mock_search:
        mock_instance = MagicMock()
        mock_search.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return {
        "organic_results": [
            {
                "position": 1,
                "title": "Test Title 1",
                "snippet": "Test Snippet 1",
                "link": "https://test1.com/article1",
                "source": "Test Source 1",
                "date": "2024-01-01",
                "rich_snippet": True,
                "displayed_link": "test1.com"
            },
            {
                "position": 2,
                "title": "Test Title 2",
                "snippet": "Test Snippet 2",
                "link": "https://test2.com/article2",
                "source": "Test Source 2",
                "date": "2024-01-02",
                "displayed_link": "test2.com"
            }
        ]
    }

@pytest.fixture
def web_search_tool():
    """Create a WebSearchTool instance with mock API key."""
    with patch.dict("os.environ", {"SERPAPI_KEY": "test_key"}):
        return WebSearchTool()

def test_search_result_formatting():
    """Test SearchResult formatting methods."""
    result = SearchResult(
        title="Test Title",
        snippet="Test Snippet",
        link="https://test.com/article",
        source="Test Source",
        published_date="January 1, 2024",
        relevance_score=0.8,
        reference_number=1
    )
    
    # Test inline citation
    inline = result.to_inline_citation()
    assert "[1]" in inline
    
    # Test markdown formatting
    markdown = result.to_markdown()
    assert "Test Snippet" in markdown
    assert "[1]" in markdown
    
    # Test bibliography entry
    bib = result.to_bibliography_entry()
    assert "[1]" in bib
    assert "Test Title" in bib
    assert "Test Source" in bib
    assert "https://test.com/article" in bib
    assert "January 1, 2024" in bib

def test_search_with_results(web_search_tool, mock_serpapi, sample_search_results):
    """Test search functionality with mock results."""
    mock_serpapi.get_dict.return_value = sample_search_results
    
    results = web_search_tool.search("test query")
    
    assert len(results) == 2
    assert isinstance(results[0], SearchResult)
    assert results[0].title == "Test Title 1"
    assert results[0].link == "https://test1.com/article1"
    assert results[0].reference_number == 1
    assert results[0].relevance_score > results[1].relevance_score

def test_relevance_scoring(web_search_tool):
    """Test result relevance scoring."""
    result1 = {"position": 1, "date": "2024-01-01", "rich_snippet": True}
    result2 = {"position": 2, "date": "2024-01-01"}
    result3 = {"position": 3}
    
    score1 = web_search_tool._calculate_relevance_score(result1)
    score2 = web_search_tool._calculate_relevance_score(result2)
    score3 = web_search_tool._calculate_relevance_score(result3)
    
    assert score1 > score2 > score3

def test_date_extraction(web_search_tool):
    """Test date extraction and formatting."""
    # Test valid date
    result1 = {"date": "2024-01-01"}
    date1 = web_search_tool._extract_date(result1)
    assert date1 == "January 01, 2024"
    
    # Test invalid date
    result2 = {"date": "invalid"}
    date2 = web_search_tool._extract_date(result2)
    assert date2 == "invalid"
    
    # Test missing date
    result3 = {}
    date3 = web_search_tool._extract_date(result3)
    assert date3 is None

def test_summarize_results_with_references(web_search_tool):
    """Test result summarization with references."""
    results = [
        SearchResult(
            title="Test Title 1",
            snippet="Test Snippet 1",
            link="https://test1.com/article1",
            source="Source 1",
            published_date="January 1, 2024",
            relevance_score=0.9,
            reference_number=1
        ),
        SearchResult(
            title="Test Title 2",
            snippet="Test Snippet 2",
            link="https://test2.com/article2",
            source="Source 2",
            published_date=None,
            relevance_score=0.8,
            reference_number=2
        )
    ]
    
    summary = web_search_tool.summarize_results(results)
    
    # Check inline citations
    assert "[1]" in summary
    assert "[2]" in summary
    
    # Check bibliography format
    assert "### References" in summary
    assert "https://test1.com/article1" in summary
    assert "https://test2.com/article2" in summary
    assert "January 1, 2024" in summary
    
    # Check content structure
    assert "### Key Findings" in summary
    assert "Test Snippet 1" in summary
    assert "Test Snippet 2" in summary

def test_reference_number_ordering(web_search_tool, mock_serpapi, sample_search_results):
    """Test that reference numbers are properly ordered after sorting."""
    mock_serpapi.get_dict.return_value = sample_search_results
    
    results = web_search_tool.search("test query")
    
    # Check reference numbers are sequential
    assert results[0].reference_number == 1
    assert results[1].reference_number == 2
    
    # Check they appear correctly in citations
    assert "[1]" in results[0].to_inline_citation()
    assert "[2]" in results[1].to_inline_citation()

def test_error_handling(web_search_tool, mock_serpapi):
    """Test error handling in search."""
    mock_serpapi.get_dict.return_value = {"error": "API Error"}
    
    with pytest.raises(Exception) as exc_info:
        web_search_tool.search("test query")
    assert "Search error: API Error" in str(exc_info.value)

def test_empty_results(web_search_tool):
    """Test handling of empty results."""
    summary = web_search_tool.summarize_results([])
    assert summary == "No search results found." 