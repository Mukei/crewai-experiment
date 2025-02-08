"""Chat UI components for the Streamlit interface."""
import re
import streamlit as st
from typing import Dict, List, Optional

def initialize_chat_state() -> None:
    """Initialize chat-related session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def format_message(content: str) -> Dict[str, str]:
    """Format message content based on its type."""
    # Check for code blocks
    if re.search(r"```[\s\S]+?```", content):
        return {"type": "code", "content": content}
    # Check for markdown headers
    elif content.startswith("#"):
        return {"type": "markdown", "content": content}
    # Default to regular text
    return {"type": "text", "content": content}

def display_message(role: str, content: str) -> None:
    """Display a single chat message with appropriate formatting."""
    with st.chat_message(role):
        formatted = format_message(content)
        if formatted["type"] == "code":
            st.code(formatted["content"])
        else:
            st.markdown(formatted["content"])

def display_chat_messages() -> None:
    """Display all messages in the chat history."""
    for message in st.session_state.messages:
        display_message(message["role"], message["content"])

def handle_user_input(user_input: str) -> None:
    """Process user input and generate AI response."""
    if not user_input:
        return

    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Show AI response with loading indicator
    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            try:
                # Get response from CrewAI
                response = st.session_state.crew.kickoff()
                # Add AI response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.session_state.messages.append({
                    "role": "system",
                    "content": error_msg
                }) 