"""Tests for the main module."""
import pytest
from unittest.mock import patch, MagicMock
from src.main import main

@pytest.fixture
def mock_research_crew():
    """Mock ResearchCrew class."""
    with patch("src.main.ResearchCrew") as mock_crew_class:
        mock_instance = MagicMock()
        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = "Test research results"
        mock_instance.get_crew.return_value = mock_crew
        mock_crew_class.return_value = mock_instance
        yield mock_crew_class

def test_main_execution(mock_research_crew, capsys):
    """Test main function execution."""
    # Execute main function
    main()
    
    # Verify ResearchCrew was initialized
    mock_research_crew.assert_called_once()
    
    # Verify get_crew was called with correct topic
    mock_research_crew.return_value.get_crew.assert_called_once_with(
        topic="AI and Machine Learning"
    )
    
    # Verify crew kickoff was called
    mock_crew = mock_research_crew.return_value.get_crew.return_value
    mock_crew.kickoff.assert_called_once()
    
    # Check output
    captured = capsys.readouterr()
    assert "Final Result:" in captured.out
    assert "Test research results" in captured.out 