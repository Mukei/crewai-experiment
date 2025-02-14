"""Chat UI components for the Streamlit interface."""
import re
import streamlit as st
from typing import Dict, List, Optional, Tuple
from src.crew import ResearchCrew
from src.utils import main_logger as logger, error_logger
import uuid
from pathlib import Path
from src.ui.components.research_display import display_research_dashboard, display_session_info

def cleanup_resources() -> None:
    """Clean up resources when the app is closing."""
    logger.info("Cleaning up resources")
    if hasattr(st.session_state, 'crew') and st.session_state.crew is not None:
        try:
            logger.info("Cleaning up crew resources")
            st.session_state.crew.cleanup()
            st.session_state.crew = None
            logger.info("Crew resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

def get_available_sessions() -> List[str]:
    """Get list of available sessions for recovery."""
    try:
        # Check temp directory for session files
        temp_dir = Path("temp/progress")
        if not temp_dir.exists():
            return []
        
        # Get unique session IDs from progress files
        sessions = []
        for file in temp_dir.glob("*_progress.json"):
            session_id = file.stem.split("_")[0]
            if session_id not in sessions:
                sessions.append(session_id)
        
        return sessions
    except Exception as e:
        logger.error(f"Error getting available sessions: {str(e)}")
        return []

def initialize_chat_state() -> None:
    """Initialize chat state."""
    logger.info("Initializing chat state")

    # Clean up existing crew if present
    if hasattr(st.session_state, 'crew') and st.session_state.crew is not None:
        try:
            logger.info("Cleaning up existing crew")
            st.session_state.crew.cleanup()
            st.session_state.crew = None
        except Exception as e:
            logger.error(f"Error during crew cleanup: {str(e)}")

    # Reset session state
    st.session_state.messages = []
    st.session_state.progress = None
    st.session_state.current_step = 0
    st.session_state.total_steps = 0
    st.session_state.status = ""

    # Initialize new crew
    logger.info("Creating new ResearchCrew instance")
    st.session_state.crew = ResearchCrew(
        progress_callback=update_progress
    )

    # Add session recovery UI
    available_sessions = get_available_sessions()
    if available_sessions:
        with st.sidebar:
            st.header("Session Recovery")
            selected_session = st.selectbox(
                "Recover previous session",
                ["None"] + available_sessions,
                key="session_selector"
            )
            if selected_session != "None":
                if st.button("Recover Session"):
                    recover_session(selected_session)
    
    # Display research dashboard if crew exists
    if hasattr(st.session_state, 'crew') and st.session_state.crew is not None:
        display_research_dashboard(st.session_state.crew)
    
    # Register cleanup handler
    if not hasattr(st.session_state, 'cleanup_registered'):
        st.session_state.cleanup_registered = True
        st.session_state.on_cleanup = cleanup_resources
        logger.info("Registered cleanup handler")

def recover_session(session_id: str) -> None:
    """Recover a previous session."""
    try:
        logger.info(f"Recovering session: {session_id}")
        
        # Clean up existing crew if present
        if hasattr(st.session_state, 'crew') and st.session_state.crew is not None:
            st.session_state.crew.cleanup()
        
        # Create new crew with session ID
        st.session_state.crew = ResearchCrew(
            progress_callback=update_progress,
            session_id=session_id
        )
        
        # Update session state
        st.session_state.current_session = session_id
        
        # Get progress from tracker
        progress = st.session_state.crew._progress_tracker.get_current_progress()
        
        # Update progress display
        st.session_state.current_step = progress.get("current_step", 0)
        st.session_state.total_steps = progress.get("total_steps", 3)
        
        # Add recovery message
        st.session_state.messages.append({
            "role": "system",
            "content": f"📥 Recovered session: {session_id}"
        })
        
        # Update research dashboard
        display_research_dashboard(st.session_state.crew)
        
        logger.info(f"Successfully recovered session: {session_id}")
        st.rerun()
    except Exception as e:
        error_msg = f"Error recovering session: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)

def update_progress(agent: str, step: int, total: int, status: str) -> None:
    """Update progress in the UI."""
    st.session_state.progress = step / total if total > 0 else 0
    st.session_state.current_step = step
    st.session_state.total_steps = total
    st.session_state.status = status
    st.experimental_rerun()

def process_user_input(user_input: str) -> None:
    """Process user input and update chat."""
    if not user_input:
        return

    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Process with crew
        if st.session_state.crew:
            logger.info("New chat input received: " + user_input)
            result = st.session_state.crew.process_with_revisions(user_input)
            
            # Add assistant message
            st.session_state.messages.append({"role": "assistant", "content": result})
            
            # Update display
            display_research_dashboard(st.session_state.crew)
        else:
            error_msg = "Error: Research crew not initialized"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            logger.error(error_msg)
            
    except Exception as e:
        error_msg = f"Error processing input: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        error_logger.error(error_msg, exc_info=True)

def display_chat_interface() -> None:
    """Display the chat interface."""
    # Initialize state if needed
    if not hasattr(st.session_state, 'messages'):
        initialize_chat_state()

    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if user_input := st.chat_input("Enter your research topic..."):
        process_user_input(user_input)

def display_progress() -> None:
    """Display progress information."""
    if hasattr(st.session_state, 'progress') and st.session_state.progress is not None:
        st.sidebar.progress(st.session_state.progress)
        st.sidebar.text(f"Step {st.session_state.current_step}/{st.session_state.total_steps}")
        st.sidebar.text(st.session_state.status)

def format_message(content: str) -> Dict[str, str]:
    """Format message content based on its type."""
    logger.debug(f"Formatting message: {content[:100]}...")
    
    # Convert content to string if it's not already
    content_str = str(content)
    
    # Check for code blocks
    if re.search(r"```[\s\S]+?```", content_str):
        return {"type": "code", "content": content_str}
    # Check for markdown headers
    elif content_str.startswith("#"):
        return {"type": "markdown", "content": content_str}
    # Default to regular text
    return {"type": "text", "content": content_str}

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
    """Display chat messages with proper formatting."""
    # Create containers for messages and progress
    messages_container = st.container()
    
    # Display progress tracking containers
    st.session_state.progress_container = st.container()
    st.session_state.status_container = st.container()
    st.session_state.step_counter = st.container()
    
    # Display messages
    with messages_container:
        for msg in st.session_state.messages:
            display_message(msg["role"], msg["content"])

def handle_user_input(prompt: str) -> None:
    """Handle user input and generate response."""
    if not prompt:
        return
        
    logger.info(f"Processing user input: {prompt}")
    
    try:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Process with crew and show progress
        with st.spinner("🤖 Processing your request..."):
            try:
                # Get response
                response = st.session_state.crew.process_with_revisions(topic=prompt)
                
                # Handle response
                if response is None:
                    error_msg = "❌ Error: No response received"
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                    st.error(error_msg)
                    logger.error("Error in crew execution: No response received")
                elif "Error" in response or "error" in response.lower():
                    error_msg = f"❌ {response}"
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                    st.error(error_msg)
                    logger.error(f"Error in crew execution: {response}")
                else:
                    # Format response based on editor decision
                    if "APPROVED:" in response:
                        formatted_response = response.replace("APPROVED:", "✅")
                    elif "NEEDS REVISION:" in response:
                        formatted_response = response.replace("NEEDS REVISION:", "⚠️")
                    else:
                        formatted_response = response
                    
                    # Add formatted response to chat
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": formatted_response
                    })
                    
                    # Display research dashboard if available
                    if hasattr(st.session_state.crew, '_file_manager'):
                        display_research_dashboard(st.session_state.crew)
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                st.error(error_msg)
                logger.error(f"Error processing user input: {str(e)}", exc_info=True)
                
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_msg
        })
        st.error(error_msg)
        logger.error(f"Error processing user input: {str(e)}", exc_info=True)