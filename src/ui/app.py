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
    handle_user_input
)
from src.utils import main_logger as logger

def initialize_app() -> None:
    """Initialize the Streamlit app."""
    logger.info("Initializing Streamlit application")
    
    # Force a clean restart by clearing browser cache
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
    
    # Clear all session state
    if not st.session_state.get('_initialized'):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state._initialized = True
        logger.debug("Cleared session state")
    
    logger.debug("Page configuration set")

def main() -> None:
    """Main function to run the Streamlit app."""
    try:
        initialize_app()
        initialize_chat_state()
        logger.info("Application initialized successfully")

        # Header
        st.title("🔍 AI Research Assistant")
        st.markdown("""
        Ask me to research any topic, and I'll provide a comprehensive analysis.
        
        I can help you with:
        - Topic research and analysis
        - Finding recent developments
        - Summarizing complex information
        """)
        logger.debug("Header and description displayed")

        # Chat interface
        st.divider()
        
        # Display chat messages
        display_chat_messages()
        logger.debug("Chat messages displayed")

        # Chat input
        if prompt := st.chat_input("What would you like me to research?"):
            logger.info(f"New chat input received: {prompt}")
            handle_user_input(prompt)
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error("❌ An error occurred while running the application. Please check the logs for details.")

if __name__ == "__main__":
    main() 