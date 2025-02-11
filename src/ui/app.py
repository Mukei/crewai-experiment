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
    display_chat_messages,
    handle_user_input,
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
    
    # Clean up existing crew if present
    if hasattr(st.session_state, 'crew') and st.session_state.crew is not None:
        cleanup_resources()
    
    # Initialize chat state
    initialize_chat_state()
    
    # Register cleanup for app shutdown
    if not hasattr(st.session_state, '_cleanup_registered'):
        st.session_state._cleanup_registered = True
        st.session_state.on_cleanup = cleanup_resources
        logger.info("Registered cleanup handler")

def main() -> None:
    """Main function to run the Streamlit app."""
    try:
        initialize_app()

        # Header
        st.title("🔍 AI Research Assistant")
        st.markdown("""
        Ask me to research any topic, and I'll provide a comprehensive analysis.
        
        I can help you with:
        - Topic research and analysis
        - Finding recent developments
        - Summarizing complex information
        """)

        # Chat interface
        st.divider()
        
        # Display chat messages
        display_chat_messages()

        # Chat input
        if prompt := st.chat_input("What would you like me to research?"):
            logger.info(f"New chat input received: {prompt}")
            handle_user_input(prompt)
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error("❌ An error occurred while running the application. Please check the logs for details.")
        # Ensure cleanup on error
        cleanup_resources()

if __name__ == "__main__":
    main()