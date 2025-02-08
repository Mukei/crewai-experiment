"""Streamlit chat interface for CrewAI experiment."""
import streamlit as st
from crew import ResearchCrew
from ui.components.chat import (
    initialize_chat_state,
    display_chat_messages,
    handle_user_input
)

def initialize_app():
    """Initialize the Streamlit app."""
    st.set_page_config(
        page_title="AI Research Assistant",
        page_icon="🔍",
        layout="wide"
    )
    
    if "crew" not in st.session_state:
        st.session_state.crew = ResearchCrew().crew()

def main():
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