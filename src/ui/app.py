"""Streamlit chat interface for CrewAI experiment."""
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import streamlit as st
from src.ui.components.chat import (
    initialize_chat_state,
    display_chat_interface,
    display_progress,
    cleanup_resources
)
from src.utils import main_logger as logger

def initialize_app() -> None:
    """Initialize the Streamlit app."""
    logger.info("Initializing Streamlit application")
    
    # Set page config
    st.set_page_config(
        page_title="AI Research Assistant",
        page_icon="🔍",
        layout="wide",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )
    
    # Initialize chat state if not already initialized
    if not hasattr(st.session_state, 'messages'):
        initialize_chat_state()
    
    # Register cleanup for app shutdown
    if not hasattr(st.session_state, '_cleanup_registered'):
        st.session_state._cleanup_registered = True
        st.session_state.on_cleanup = cleanup_resources
        logger.info("Registered cleanup handler")

def main():
    """Main application entry point."""
    try:
        # Initialize app
        initialize_app()
        
        # Display header
        st.title("🔍 AI Research Assistant")
        st.markdown("""
        Welcome to the AI Research Assistant! Enter a topic you'd like to research,
        and our AI crew will help you find and analyze relevant information.
        """)
        
        # Create columns for layout
        chat_col, progress_col = st.columns([2, 1])
        
        # Display chat interface in main column
        with chat_col:
            display_chat_interface()
        
        # Display progress in sidebar
        with progress_col:
            display_progress()
            
    except Exception as e:
        logger.error(f"Error in main app: {str(e)}", exc_info=True)
        st.error(f"An error occurred: {str(e)}")
        
    finally:
        # Ensure cleanup is registered
        if not hasattr(st.session_state, '_cleanup_registered'):
            st.session_state._cleanup_registered = True
            st.session_state.on_cleanup = cleanup_resources

if __name__ == "__main__":
    main()