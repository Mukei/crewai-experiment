"""Tests for chat UI components."""
import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
from src.ui.components.chat import (
    initialize_chat_state,
    display_chat_messages,
    handle_user_input,
    format_message,
    display_message,
    update_progress
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
    mock_streamlit.session_state.crew.process_with_revisions.return_value = "Content output"

    handle_user_input("Test input")

    messages = mock_streamlit.session_state.messages
    assert len(messages) == 2  # User input + Content
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Test input"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Content output"

def test_handle_user_input_error(mock_streamlit):
    """Test error handling in user input."""
    # Set up error condition
    mock_streamlit.session_state.crew.process_with_revisions.side_effect = Exception("Test error")
    handle_user_input("Test input")

    messages = mock_streamlit.session_state.messages
    assert len(messages) == 2  # User input + Error message

    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Test input"

    assert messages[1]["role"] == "assistant"
    assert "❌ Error: Test error" in messages[1]["content"]

def test_handle_max_revisions(mock_streamlit):
    """Test handling of max revisions reached."""
    # Mock max revisions reached
    mock_streamlit.session_state.crew.process_with_revisions.return_value = "Max revisions reached"

    handle_user_input("Test input")

    messages = mock_streamlit.session_state.messages
    assert len(messages) == 2  # User input + Warning
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Test input"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Max revisions reached"

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

def test_update_progress(mock_streamlit):
    """Test progress bar updates."""
    # Set up initial state
    mock_streamlit.session_state.current_step = 0
    mock_streamlit.session_state.total_steps = 3
    mock_streamlit.session_state.progress = None
    mock_streamlit.session_state.status = None
    
    # Initial update
    update_progress("Researcher", 0, 3, "Starting task")
    assert mock_streamlit.session_state.current_step == 0
    assert mock_streamlit.session_state.total_steps == 3
    assert mock_streamlit.session_state.progress == "Researcher: Starting task"
    
    # Subsequent update
    update_progress("Writer", 1, 3, "In progress")
    assert mock_streamlit.session_state.current_step == 1
    assert mock_streamlit.session_state.total_steps == 3
    assert mock_streamlit.session_state.progress == "Writer: In progress"
    
    # Final update
    update_progress("Editor", 3, 3, "Complete")
    assert mock_streamlit.session_state.current_step == 3
    assert mock_streamlit.session_state.total_steps == 3
    assert mock_streamlit.session_state.progress == "Editor: Complete"

def test_handle_user_input_with_special_characters(mock_streamlit):
    """Test handling input with special characters."""
    mock_streamlit.session_state.crew.process_with_revisions.return_value = "Processed @#$%^&*"
    handle_user_input("Test @#$%^&*")
    
    messages = mock_streamlit.session_state.messages
    assert messages[0]["content"] == "Test @#$%^&*"
    assert messages[1]["content"] == "Processed @#$%^&*"

def test_handle_user_input_with_markdown(mock_streamlit):
    """Test handling input with markdown formatting."""
    mock_streamlit.session_state.crew.process_with_revisions.return_value = "# Test Header\n\n- Point 1\n- Point 2"
    handle_user_input("Test markdown")
    
    messages = mock_streamlit.session_state.messages
    assert len(messages) == 2
    assert messages[1]["content"].startswith("# Test Header")

def test_handle_user_input_with_code_blocks(mock_streamlit):
    """Test handling input with code blocks."""
    response = "```python\nprint('hello')\n```"
    mock_streamlit.session_state.crew.process_with_revisions.return_value = response
    handle_user_input("Test code")
    
    messages = mock_streamlit.session_state.messages
    assert len(messages) == 2
    assert messages[1]["content"] == response

def test_format_message_with_mixed_content(mock_streamlit):
    """Test message formatting with mixed content."""
    # Test code block detection
    content = "# Header\n\nNormal text\n\n```python\ncode=True\n```"
    formatted = format_message(content)
    assert formatted["type"] == "code"
    assert formatted["content"] == content
    
    # Test markdown detection
    content = "# Header\n\nNormal text\n\nNo code blocks here"
    formatted = format_message(content)
    assert formatted["type"] == "markdown"
    assert formatted["content"] == content
    
    # Test regular text
    content = "Just some regular text without special formatting"
    formatted = format_message(content)
    assert formatted["type"] == "text"
    assert formatted["content"] == content

def test_display_message_with_error(mock_streamlit):
    """Test displaying error messages."""
    error_content = "❌ Error: Test error"
    display_message("assistant", error_content)
    mock_streamlit.chat_message.assert_called_with("assistant")
    mock_streamlit.markdown.assert_called_with(error_content)

def test_initialize_chat_state_cleanup(mock_streamlit, mock_research_crew):
    """Test chat state cleanup during initialization."""
    # Set up existing state
    mock_streamlit.session_state.messages = ["old message"]
    mock_streamlit.session_state.progress = "old progress"
    mock_streamlit.session_state.current_step = 0.5
    
    # Mock existing crew with cleanup method
    mock_crew = MagicMock()
    mock_cleanup = MagicMock()
    mock_crew._cleanup_llm = mock_cleanup
    mock_streamlit.session_state.crew = mock_crew
    
    # Create new mock crew instance for initialization
    new_crew = MagicMock()
    mock_research_crew.return_value = new_crew
    
    # Mock 'in' operator for session_state
    def mock_contains(self, key):
        return key in ["messages", "crew"]
    type(mock_streamlit.session_state).__contains__ = mock_contains
    
    # Mock hasattr to return True for _cleanup_llm
    with patch('builtins.hasattr', return_value=True):
        initialize_chat_state()
    
    # Verify cleanup
    mock_cleanup.assert_called_once()
    assert mock_streamlit.session_state.messages == []
    assert mock_streamlit.session_state.progress is None
    assert mock_streamlit.session_state.current_step == 0
    assert mock_streamlit.session_state.crew == new_crew 