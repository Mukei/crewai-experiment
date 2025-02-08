"""Chat UI components for the Streamlit interface."""
import re
import streamlit as st
from typing import Dict, List, Optional
from src.crew import ResearchCrew

def initialize_chat_state() -> None:
    """Initialize chat-related session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "crew" not in st.session_state:
        # Initialize with a default topic that will be overridden when user inputs a topic
        st.session_state.crew = ResearchCrew(default_topic="General Research")
    if "progress" not in st.session_state:
        st.session_state.progress = None

def update_progress(message: str, progress: float) -> None:
    """Update the progress bar and status message."""
    if st.session_state.progress is None:
        st.session_state.progress = st.progress(0.0)
    st.session_state.progress.progress(progress)
    st.write(f"🤖 {message}")

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

    # Reset progress
    st.session_state.progress = None

    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Show AI response with loading indicator
    with st.chat_message("assistant"):
        try:
            # Research phase
            update_progress("Research Agent: Analyzing the topic...", 0.2)
            crew = st.session_state.crew.get_crew(topic=user_input)
            
            update_progress("Research Agent: Gathering information...", 0.4)
            # This is where we'll add web search integration
            
            update_progress("Research Agent: Synthesizing findings...", 0.6)
            
            update_progress("Writing Agent: Creating summary...", 0.8)
            
            response = crew.kickoff()
            
            update_progress("Complete!", 1.0)
            
            # Add AI response
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
            # Display the response immediately
            st.markdown(response)
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            st.session_state.messages.append({
                "role": "system",
                "content": error_msg
            })
            st.error(error_msg)
        finally:
            # Clear progress after completion
            if st.session_state.progress is not None:
                st.session_state.progress.empty()
            st.session_state.progress = None 