"""Chat UI components for the Streamlit interface."""
import re
import streamlit as st
from typing import Dict, List, Optional
from src.crew import ResearchCrew
from src.utils import main_logger as logger, error_logger

def initialize_chat_state() -> None:
    """Initialize chat-related session state variables."""
    logger.info("Initializing chat state")
    
    # Clear existing state
    if "messages" in st.session_state:
        st.session_state.messages = []
    else:
        st.session_state.messages = []
    logger.debug("Initialized empty messages list")
    
    # Reset crew instance
    if "crew" in st.session_state:
        if hasattr(st.session_state.crew, '_cleanup_llm'):
            st.session_state.crew._cleanup_llm()
    st.session_state.crew = ResearchCrew()
    logger.debug("Created new ResearchCrew instance")
    
    # Reset progress tracking
    st.session_state.progress = None
    st.session_state.progress_status = None
    st.session_state.current_step = 0
    st.session_state.last_processed_message = None  # Track last processed message
    logger.debug("Initialized progress tracking")
    
    logger.info("Chat state initialization complete")

def update_progress(message: str, increment: float = None) -> None:
    """Update the progress bar and status message."""
    logger.debug(f"Updating progress: {message} (increment: {increment})")
    # Initialize progress components if needed
    if st.session_state.progress is None:
        st.session_state.progress = st.progress(0.0)
    if st.session_state.progress_status is None:
        st.session_state.progress_status = st.empty()
    
    # Update progress if increment provided
    if increment is not None:
        current = st.session_state.current_step
        new_progress = min(current + increment, 1.0)
        st.session_state.current_step = new_progress
        st.session_state.progress.progress(new_progress)
        logger.debug(f"Progress updated to {new_progress:.1%}")
    
    st.session_state.progress_status.write(f"🤖 {message}")

def format_message(content: str) -> Dict[str, str]:
    """Format message content based on its type."""
    logger.debug(f"Formatting message: {content[:100]}...")
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
    logger.debug(f"Displaying message from {role}")
    with st.chat_message(role):
        formatted = format_message(content)
        if formatted["type"] == "code":
            st.code(formatted["content"])
        else:
            st.markdown(formatted["content"])

def display_chat_messages() -> None:
    """Display all messages in the chat history."""
    logger.debug(f"Displaying {len(st.session_state.messages)} chat messages")
    for message in st.session_state.messages:
        display_message(message["role"], message["content"])

def handle_user_input(user_input: str) -> None:
    """Process user input and generate AI response."""
    if not user_input:
        logger.debug("Empty user input received")
        return
        
    # Check if we've already processed this message
    if st.session_state.get('last_processed_message') == user_input:
        logger.debug("Skipping already processed message")
        return
        
    logger.info(f"Processing user input: {user_input}")
    st.session_state.last_processed_message = user_input

    # Initialize progress tracking
    st.session_state.progress = st.progress(0.0)
    st.session_state.progress_status = st.empty()
    st.session_state.current_step = 0

    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    logger.debug("Added user message to chat history")

    try:
        # Update progress for research phase
        update_progress("🔍 Researching topic...", 0.2)
        
        # Process the topic with revisions
        content, status = st.session_state.crew.process_with_revisions(user_input)
        
        # Update progress for completion
        update_progress("✅ Processing complete", 1.0)
        
        if content:
            # Add AI response
            st.session_state.messages.append({
                "role": "assistant",
                "content": content
            })
            
            # Add status message
            st.session_state.messages.append({
                "role": "system",
                "content": f"Status: {status}"
            })
            logger.debug("Added AI response and status to chat history")
        else:
            # Handle error case
            error_message = "❌ I encountered an error while processing your request. Please try again."
            st.session_state.messages.append({
                "role": "system",
                "content": error_message
            })
            logger.error("Failed to generate response")
            
    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}", exc_info=True)
        error_message = f"❌ Error: {str(e)}"
        st.session_state.messages.append({
            "role": "system",
            "content": error_message
        })
        
    finally:
        # Clear progress tracking
        if st.session_state.progress:
            st.session_state.progress.empty()
        if st.session_state.progress_status:
            st.session_state.progress_status.empty()
        st.session_state.progress = None
        st.session_state.progress_status = None
        st.session_state.current_step = 0 