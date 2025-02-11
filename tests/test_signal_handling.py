"""Tests for signal handling in ResearchCrew."""
import pytest
import signal
import os
from unittest.mock import patch, MagicMock
from src.crew import ResearchCrew

@pytest.fixture
def mock_file_manager():
    """Mock FileManager."""
    with patch('src.crew.FileManager') as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield instance

@pytest.fixture
def mock_llm():
    """Mock LLM."""
    with patch('src.crew.LLM') as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield instance

def test_cleanup_on_sigint(mock_file_manager, mock_llm):
    """Test cleanup is called on SIGINT."""
    crew = ResearchCrew()
    
    # Mock cleanup methods
    crew._cleanup_llm = MagicMock()
    
    # Send SIGINT
    with pytest.raises(SystemExit):
        os.kill(os.getpid(), signal.SIGINT)
    
    # Verify cleanup was called
    crew._cleanup_llm.assert_called_once()
    mock_file_manager.cleanup.assert_called_once()

def test_cleanup_on_sigterm(mock_file_manager, mock_llm):
    """Test cleanup is called on SIGTERM."""
    crew = ResearchCrew()
    
    # Mock cleanup methods
    crew._cleanup_llm = MagicMock()
    
    # Send SIGTERM
    with pytest.raises(SystemExit):
        os.kill(os.getpid(), signal.SIGTERM)
    
    # Verify cleanup was called
    crew._cleanup_llm.assert_called_once()
    mock_file_manager.cleanup.assert_called_once()

def test_cleanup_handles_errors(mock_file_manager, mock_llm):
    """Test cleanup handles errors gracefully."""
    crew = ResearchCrew()
    
    # Mock cleanup methods to raise exceptions
    crew._cleanup_llm = MagicMock(side_effect=Exception("LLM cleanup failed"))
    mock_file_manager.cleanup = MagicMock(side_effect=Exception("File cleanup failed"))
    
    # Mock progress tracker cleanup
    crew._progress_tracker.cleanup = MagicMock(side_effect=Exception("Progress cleanup failed"))
    
    # Verify cleanup completes without raising
    crew.cleanup()
    
    # Verify all cleanup methods were called despite errors
    crew._cleanup_llm.assert_called_once()
    mock_file_manager.cleanup.assert_called_once()
    crew._progress_tracker.cleanup.assert_called_once()

def test_multiple_signal_handlers(mock_file_manager, mock_llm):
    """Test multiple signal handlers don't conflict."""
    crew1 = ResearchCrew()
    crew2 = ResearchCrew()
    
    # Mock cleanup methods
    crew1._cleanup_llm = MagicMock()
    crew2._cleanup_llm = MagicMock()
    
    # Send SIGINT
    with pytest.raises(SystemExit):
        os.kill(os.getpid(), signal.SIGINT)
    
    # Verify both instances cleaned up
    crew1._cleanup_llm.assert_called_once()
    crew2._cleanup_llm.assert_called_once()
    assert mock_file_manager.cleanup.call_count == 2 