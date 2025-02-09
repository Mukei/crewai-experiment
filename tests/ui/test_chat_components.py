"""Tests for chat UI components."""
import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
from src.ui.components.chat import (
    initialize_chat_state,
    display_chat_messages,
    handle_user_input,
    format_message,
    display_message
)

@pytest.fixture
def mock_streamlit():
    """Mock streamlit session state and functions."""
    with patch("src.ui.components.chat.st") as mock_st:
        mock_st.session_state = MagicMock()
        mock_st.session_state.messages = []
        mock_st.chat_message = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.code = MagicMock()
        mock_st.spinner = MagicMock()
        mock_st.error = MagicMock()
        mock_st.progress = MagicMock()
        mock_st.write = MagicMock()
        
        # Mock ResearchCrew
        mock_crew = MagicMock()
        mock_crew_instance = MagicMock()
        mock_crew_instance.get_crew.return_value = mock_crew
        mock_crew.kickoff.return_value = "Test response"
        mock_st.session_state.crew = mock_crew_instance
        
        yield mock_st

@pytest.fixture
def mock_research_crew():
    """Mock ResearchCrew class."""
    with patch("src.ui.components.chat.ResearchCrew") as mock_crew_class:
        mock_instance = MagicMock()
        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = "Test response"
        mock_instance.get_crew.return_value = mock_crew
        mock_crew_class.return_value = mock_instance
        yield mock_crew_class

def test_initialize_chat_state(mock_streamlit, mock_research_crew):
    """Test chat state initialization."""
    initialize_chat_state()
    assert hasattr(mock_streamlit.session_state, "messages")
    assert isinstance(mock_streamlit.session_state.messages, list)
    assert len(mock_streamlit.session_state.messages) == 0
    assert hasattr(mock_streamlit.session_state, "crew")
    mock_research_crew.assert_called_once()

def test_display_chat_messages(mock_streamlit):
    """Test chat message display."""
    mock_streamlit.session_state.messages = [
        {"role": "user", "content": "Test question"},
        {"role": "assistant", "content": "Test answer"},
        {"role": "system", "content": "# Test header"}
    ]
    display_chat_messages()
    assert mock_streamlit.chat_message.call_count == 3

def test_display_message_types(mock_streamlit):
    """Test different message type displays."""
    test_messages = [
        ("user", "Regular text", "text"),
        ("assistant", "```python\nprint('test')\n```", "code"),
        ("system", "# Header", "markdown")
    ]
    
    for role, content, msg_type in test_messages:
        display_message(role, content)
        mock_streamlit.chat_message.assert_called_with(role)
        if msg_type == "code":
            mock_streamlit.code.assert_called()
        else:
            mock_streamlit.markdown.assert_called()

def test_handle_user_input_success(mock_streamlit):
    """Test successful user input handling."""
    # Mock successful process_with_revisions
    mock_streamlit.session_state.crew.process_with_revisions.return_value = {
        "status": "approved",
        "research": "Research output",
        "content": "Content output",
        "feedback": "APPROVED: Good quality"
    }
    
    handle_user_input("Test input")
    
    messages = mock_streamlit.session_state.messages
    assert len(messages) == 4  # User input + Research + Content + Editor feedback
    
    # Check message sequence
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Test input"
    
    assert messages[1]["role"] == "system"
    assert "Research Results" in messages[1]["content"]
    
    assert messages[2]["role"] == "assistant"
    assert messages[2]["content"] == "Content output"
    
    assert messages[3]["role"] == "system"
    assert "Editor's Review" in messages[3]["content"]
    
    # Check content display
    mock_streamlit.markdown.assert_called_with("Content output")

def test_handle_user_input_error(mock_streamlit):
    """Test error handling in user input."""
    # Set up error condition
    mock_streamlit.session_state.crew.process_with_revisions.side_effect = Exception("Test error")
    handle_user_input("Test input")
    
    messages = mock_streamlit.session_state.messages
    assert len(messages) == 2  # User input + Error message
    
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Test input"
    
    assert messages[1]["role"] == "system"
    assert "Error" in messages[1]["content"]
    
    mock_streamlit.error.assert_called_with("❌ Error: Test error")

def test_handle_max_revisions(mock_streamlit):
    """Test handling of max revisions reached."""
    # Mock max revisions reached
    mock_streamlit.session_state.crew.process_with_revisions.return_value = {
        "status": "max_revisions",
        "research": "Research output",
        "content": "Content output",
        "feedback": "NEEDS REVISION: Not quite there"
    }
    
    handle_user_input("Test input")
    
    messages = mock_streamlit.session_state.messages
    assert len(messages) == 4  # User input + Warning + Content + Editor feedback
    
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Test input"
    
    assert messages[1]["role"] == "system"
    assert "Maximum revision attempts reached" in messages[1]["content"]
    
    assert messages[2]["role"] == "assistant"
    assert messages[2]["content"] == "Content output"
    
    assert messages[3]["role"] == "system"
    assert "Editor's Review (Not Approved)" in messages[3]["content"]
    
    # Check warning display
    mock_streamlit.warning.assert_called_with("⚠️ The content below has not been fully approved by the editor.")

def test_handle_empty_input(mock_streamlit):
    """Test handling of empty input."""
    handle_user_input("")
    assert len(mock_streamlit.session_state.messages) == 0

def test_format_message():
    """Test message formatting."""
    test_cases = [
        ("# Header", "markdown"),
        ("```python\nprint('test')\n```", "code"),
        ("Normal text", "text"),
        ("```\nplain code\n```", "code"),
        ("## Another header", "markdown"),
        ("Just some text with `inline code`", "text")
    ]
    
    for content, expected_type in test_cases:
        message = format_message(content)
        assert message["type"] == expected_type
        assert message["content"] == content 