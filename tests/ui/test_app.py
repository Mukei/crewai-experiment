"""Tests for the Streamlit chat interface."""
import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.ui.app import initialize_session_state, process_user_input

@pytest.fixture
def mock_streamlit():
    """Mock streamlit session state and functions."""
    with patch("src.ui.app.st") as mock_st:
        # Mock session state
        mock_st.session_state = MagicMock()
        mock_st.session_state.messages = []
        mock_st.session_state.crew = MagicMock()
        yield mock_st

def test_initialize_session_state(mock_streamlit):
    """Test session state initialization."""
    initialize_session_state()
    assert hasattr(mock_streamlit.session_state, "messages")
    assert hasattr(mock_streamlit.session_state, "crew")

def test_process_user_input_success(mock_streamlit):
    """Test successful processing of user input."""
    # Mock successful response
    mock_streamlit.session_state.crew.kickoff.return_value = "Test response"
    
    # Process input
    process_user_input("Test input")
    
    # Check messages were added
    assert len(mock_streamlit.session_state.messages) == 2
    assert mock_streamlit.session_state.messages[0]["role"] == "user"
    assert mock_streamlit.session_state.messages[0]["content"] == "Test input"
    assert mock_streamlit.session_state.messages[1]["role"] == "assistant"
    assert mock_streamlit.session_state.messages[1]["content"] == "Test response"

def test_process_user_input_error(mock_streamlit):
    """Test error handling in user input processing."""
    # Mock error response
    mock_streamlit.session_state.crew.kickoff.side_effect = Exception("Test error")
    
    # Process input
    process_user_input("Test input")
    
    # Check error message was added
    assert len(mock_streamlit.session_state.messages) == 2
    assert mock_streamlit.session_state.messages[0]["role"] == "user"
    assert mock_streamlit.session_state.messages[1]["role"] == "system"
    assert "Error: Test error" in mock_streamlit.session_state.messages[1]["content"] 