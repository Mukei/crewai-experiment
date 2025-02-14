"""Tests for the WebSearchTool class."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from src.tools.web_search import WebSearchTool, SearchResult

@pytest.fixture
def mock_serper():
    """Mock SerperDevTool responses."""
    with patch("src.tools.web_search.SerperDevTool.run") as mock_run:
        mock_run.return_value = "Test Title 1\nTest Title 2"
        yield mock_run

@pytest.fixture
def web_search_tool():
    """Create a WebSearchTool instance with mock API key."""
    with patch.dict("os.environ", {"SERPER_API_KEY": "test_key"}):
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
    assert "Test Snippet" in inline
    
    # Test markdown formatting
    markdown = result.to_markdown()
    assert "Test Snippet" in markdown
    assert "[1]" in markdown
    assert "https://test.com/article" in markdown
    
    # Test bibliography entry
    bib = result.to_bibliography_entry()
    assert "[1]" in bib
    assert "Test Title" in bib
    assert "Test Source" in bib
    assert "January 1, 2024" in bib

def test_search_with_results(web_search_tool, mock_serper):
    """Test search functionality with mock results."""
    results = web_search_tool.search("test query")
    
    assert len(results) == 2
    assert isinstance(results[0], SearchResult)
    assert results[0].title == "Test Title 1"
    assert results[1].title == "Test Title 2"
    assert results[0].reference_number == 1
    assert results[1].reference_number == 2

def test_relevance_scoring(web_search_tool):
    """Test result relevance scoring."""
    # Test position-based scoring
    result1 = {"position": 1}
    result2 = {"position": 2}
    score1 = web_search_tool._calculate_relevance_score(result1)
    score2 = web_search_tool._calculate_relevance_score(result2)
    assert score1 > score2  # Higher position should score higher
    
    # Test rich snippet bonus
    result_with_rich = {"position": 1, "rich_snippet": True}
    result_without_rich = {"position": 1, "rich_snippet": False}
    score_with_rich = web_search_tool._calculate_relevance_score(result_with_rich)
    score_without_rich = web_search_tool._calculate_relevance_score(result_without_rich)
    assert score_with_rich > score_without_rich  # Rich snippet should boost score
    
    # Test date-based scoring
    today = datetime.now()
    
    # Create dates for different tiers
    very_recent = (today - timedelta(days=7)).strftime("%Y-%m-%d")  # Within last month
    older = (today - timedelta(days=400)).strftime("%Y-%m-%d")  # Over a year old
    
    result_new = {"position": 1, "date": very_recent}
    result_old = {"position": 1, "date": older}
    score_new = web_search_tool._calculate_relevance_score(result_new)
    score_old = web_search_tool._calculate_relevance_score(result_old)
    assert score_new > score_old  # Newer date should score higher

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
    
    # Check content structure
    assert "### Key Findings" in summary
    assert "Test Snippet 1" in summary
    assert "Test Snippet 2" in summary
    
    # Check bibliography
    assert "### References" in summary
    assert "Test Title 1" in summary
    assert "Test Title 2" in summary
    assert "January 1, 2024" in summary
    assert "https://test1.com/article1" in summary
    assert "https://test2.com/article2" in summary

def test_reference_number_ordering(web_search_tool, mock_serper):
    """Test that reference numbers are properly ordered after sorting."""
    results = web_search_tool.search("test query")
    
    # Check reference numbers are sequential
    assert len(results) == 2
    assert results[0].reference_number == 1
    assert results[1].reference_number == 2

def test_error_handling(web_search_tool, mock_serper):
    """Test error handling in search."""
    mock_serper.side_effect = Exception("API Error")
    
    with pytest.raises(Exception) as exc_info:
        web_search_tool.search("test query")
    assert "Search error: API Error" in str(exc_info.value)

def test_empty_results(web_search_tool):
    """Test handling of empty results."""
    summary = web_search_tool.summarize_results([])
    assert summary == "No search results found." 