"""Tests for chat UI components."""
import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
from src.ui.components.chat import (
    initialize_chat_state,
    display_chat_messages,
    handle_user_input,
    format_message
)

@pytest.fixture
def mock_streamlit():
    """Mock streamlit session state and functions."""
    with patch("src.ui.components.chat.st") as mock_st:
        mock_st.session_state = MagicMock()
        mock_st.session_state.messages = []
        mock_st.session_state.crew = MagicMock()
        yield mock_st

def test_initialize_chat_state(mock_streamlit):
    """Test chat state initialization."""
    initialize_chat_state()
    assert hasattr(mock_streamlit.session_state, "messages")
    assert isinstance(mock_streamlit.session_state.messages, list)
    assert len(mock_streamlit.session_state.messages) == 0

def test_display_chat_messages(mock_streamlit):
    """Test chat message display."""
    mock_streamlit.session_state.messages = [
        {"role": "user", "content": "Test question"},
        {"role": "assistant", "content": "Test answer"}
    ]
    display_chat_messages()
    assert mock_streamlit.chat_message.call_count == 2

def test_handle_user_input_success(mock_streamlit):
    """Test successful user input handling."""
    mock_streamlit.session_state.crew.kickoff.return_value = "Test response"
    handle_user_input("Test input")
    
    assert len(mock_streamlit.session_state.messages) == 2
    assert mock_streamlit.session_state.messages[0]["role"] == "user"
    assert mock_streamlit.session_state.messages[0]["content"] == "Test input"
    assert mock_streamlit.session_state.messages[1]["role"] == "assistant"
    assert mock_streamlit.session_state.messages[1]["content"] == "Test response"

def test_handle_user_input_error(mock_streamlit):
    """Test error handling in user input."""
    mock_streamlit.session_state.crew.kickoff.side_effect = Exception("Test error")
    handle_user_input("Test input")
    
    assert len(mock_streamlit.session_state.messages) == 2
    assert mock_streamlit.session_state.messages[0]["role"] == "user"
    assert mock_streamlit.session_state.messages[1]["role"] == "system"
    assert "Error" in mock_streamlit.session_state.messages[1]["content"]

def test_format_message():
    """Test message formatting."""
    test_cases = [
        ("# Header", "markdown"),
        ("```python\nprint('test')\n```", "code"),
        ("Normal text", "text")
    ]
    
    for content, expected_type in test_cases:
        message = format_message(content)
        assert message["type"] == expected_type
        assert message["content"] == content 