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
    handle_user_input("Test input")
    
    assert len(mock_streamlit.session_state.messages) == 2
    assert mock_streamlit.session_state.messages[0]["role"] == "user"
    assert mock_streamlit.session_state.messages[0]["content"] == "Test input"
    assert mock_streamlit.session_state.messages[1]["role"] == "assistant"
    assert mock_streamlit.session_state.messages[1]["content"] == "Test response"
    
    # Check that crew was called with correct topic
    mock_streamlit.session_state.crew.get_crew.assert_called_once_with(topic="Test input")
    mock_streamlit.markdown.assert_called_with("Test response")

def test_handle_user_input_error(mock_streamlit):
    """Test error handling in user input."""
    # Set up error condition
    mock_streamlit.session_state.crew.get_crew.side_effect = Exception("Test error")
    handle_user_input("Test input")
    
    assert len(mock_streamlit.session_state.messages) == 2
    assert mock_streamlit.session_state.messages[0]["role"] == "user"
    assert mock_streamlit.session_state.messages[1]["role"] == "system"
    assert "Error" in mock_streamlit.session_state.messages[1]["content"]
    mock_streamlit.error.assert_called_with("❌ Error: Test error")

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