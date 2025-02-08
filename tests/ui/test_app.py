"""Tests for the Streamlit app."""
import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
from src.ui.app import initialize_app, main

@pytest.fixture
def mock_path_setup():
    """Mock path setup."""
    with patch("src.ui.app.sys") as mock_sys, \
         patch("src.ui.app.Path") as mock_path:
        mock_path_instance = MagicMock()
        mock_path_instance.parent.parent.parent = "/mock/project/root"
        mock_path.return_value = mock_path_instance
        yield mock_sys

@pytest.fixture
def mock_streamlit():
    """Mock streamlit functions and state."""
    with patch("src.ui.app.st") as mock_st:
        mock_st.session_state = MagicMock()
        mock_st.session_state.messages = []
        yield mock_st

@pytest.fixture
def mock_chat_components():
    """Mock chat components."""
    with patch("src.ui.app.initialize_chat_state") as mock_init, \
         patch("src.ui.app.display_chat_messages") as mock_display, \
         patch("src.ui.app.handle_user_input") as mock_handle:
        yield {
            "initialize": mock_init,
            "display": mock_display,
            "handle": mock_handle
        }

def test_initialize_app(mock_path_setup, mock_streamlit):
    """Test app initialization."""
    initialize_app()
    
    # Check page config
    mock_streamlit.set_page_config.assert_called_once()
    page_config = mock_streamlit.set_page_config.call_args[1]
    assert page_config["page_title"] == "AI Research Assistant"
    assert page_config["page_icon"] == "🔍"
    assert page_config["layout"] == "wide"

def test_main_flow(mock_path_setup, mock_streamlit, mock_chat_components):
    """Test main app flow."""
    # Mock chat input
    mock_streamlit.chat_input.return_value = "Test question"
    
    # Run main
    main()
    
    # Check initialization
    mock_chat_components["initialize"].assert_called_once()
    
    # Check UI elements
    mock_streamlit.title.assert_called_once_with("🔍 AI Research Assistant")
    mock_streamlit.markdown.assert_called()
    mock_streamlit.divider.assert_called_once()
    
    # Check chat components
    mock_chat_components["display"].assert_called_once()
    mock_chat_components["handle"].assert_called_once_with("Test question")

def test_main_no_input(mock_path_setup, mock_streamlit, mock_chat_components):
    """Test main app flow without user input."""
    # Mock no chat input
    mock_streamlit.chat_input.return_value = None
    
    # Run main
    main()
    
    # Check initialization still happens
    mock_chat_components["initialize"].assert_called_once()
    mock_chat_components["display"].assert_called_once()
    
    # Check no input handling
    mock_chat_components["handle"].assert_not_called() 