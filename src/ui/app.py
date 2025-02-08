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

def initialize_app() -> None:
    """Initialize the Streamlit app."""
    st.set_page_config(
        page_title="AI Research Assistant",
        page_icon="🔍",
        layout="wide"
    )

def main() -> None:
    """Main function to run the Streamlit app."""
    initialize_app()
    initialize_chat_state()

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
        handle_user_input(prompt)

if __name__ == "__main__":
    main() 