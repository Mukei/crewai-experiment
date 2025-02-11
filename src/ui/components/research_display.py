"""Research results and revision history display components."""
import streamlit as st
from typing import Dict, List, Optional
from pathlib import Path
from src.utils import main_logger as logger

def display_research_results(file_manager, session_id: str) -> None:
    """Display research results with citations and sources.
    
    Args:
        file_manager: FileManager instance
        session_id: Current session ID
    """
    try:
        # Get research content
        research_content = file_manager.get_latest_file('research', 'md')
        if research_content:
            with st.expander("📚 Research Results", expanded=False):
                st.markdown(research_content)
                
                # Get and display sources
                try:
                    sources = file_manager.get_latest_file('research', 'json')
                    if sources:
                        st.divider()
                        st.subheader("Sources")
                        st.json(sources)
                except Exception as e:
                    logger.error(f"Error displaying sources: {str(e)}")
    except Exception as e:
        logger.error(f"Error displaying research results: {str(e)}")

def display_revision_history(file_manager, progress_tracker, session_id: str) -> None:
    """Display revision history and feedback.
    
    Args:
        file_manager: FileManager instance
        progress_tracker: ProgressTracker instance
        session_id: Current session ID
    """
    try:
        # Get step history
        steps = progress_tracker.get_step_history()
        if steps:
            with st.expander("📝 Revision History", expanded=False):
                for step in steps:
                    # Create a unique key for each step
                    step_key = f"{session_id}_{step['timestamp']}"
                    
                    # Display step information
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown(f"**{step['agent']}**")
                        st.caption(f"Step {step['step']}/{step['total']}")
                    with col2:
                        st.info(step['status'])
                    
                    # If this is an editing step, show the review
                    if step['agent'] == "Editor":
                        try:
                            review = file_manager.get_latest_file('editing', 'md')
                            if review:
                                if "APPROVED:" in review:
                                    st.success("✅ " + review.split("APPROVED:", 1)[1].strip())
                                elif "NEEDS REVISION:" in review:
                                    st.warning("⚠️ " + review.split("NEEDS REVISION:", 1)[1].strip())
                        except Exception as e:
                            logger.error(f"Error displaying review: {str(e)}")
                    
                    st.divider()
    except Exception as e:
        logger.error(f"Error displaying revision history: {str(e)}")

def display_error_log(progress_tracker) -> None:
    """Display error log if any errors occurred.
    
    Args:
        progress_tracker: ProgressTracker instance
    """
    try:
        errors = progress_tracker.get_errors()
        if errors:
            with st.expander("⚠️ Error Log", expanded=False):
                for error in errors:
                    st.error(f"**{error['timestamp']}**\n{error['error']}")
    except Exception as e:
        logger.error(f"Error displaying error log: {str(e)}")

def display_session_info(session_id: str, progress_tracker) -> None:
    """Display session information and current progress.
    
    Args:
        session_id: Current session ID
        progress_tracker: ProgressTracker instance
    """
    try:
        progress = progress_tracker.get_current_progress()
        if progress:
            with st.expander("ℹ️ Session Info", expanded=False):
                st.code(f"Session ID: {session_id}")
                
                # Ensure total_steps is at least 1 and current_step doesn't exceed total
                total_steps = max(progress.get('total_steps', 1), 1)
                current_step = min(progress.get('current_step', 0), total_steps)
                
                # Calculate percentage safely
                percentage = int((current_step / total_steps) * 100)
                
                st.metric(
                    "Progress",
                    f"{current_step}/{total_steps}",
                    f"{percentage}%"
                )
                st.caption(f"Started: {progress.get('start_time', 'N/A')}")
                if 'last_update' in progress:
                    st.caption(f"Last Update: {progress['last_update']}")
    except Exception as e:
        logger.error(f"Error displaying session info: {str(e)}")

def display_research_dashboard(crew) -> None:
    """Display the complete research dashboard.
    
    Args:
        crew: ResearchCrew instance
    """
    try:
        if not hasattr(crew, 'session_id'):
            return
            
        # Create dashboard container
        with st.sidebar:
            st.title("Research Dashboard")
            
            # Display session information
            display_session_info(crew.session_id, crew._progress_tracker)
            
            # Display research results
            display_research_results(crew._file_manager, crew.session_id)
            
            # Display revision history
            display_revision_history(
                crew._file_manager,
                crew._progress_tracker,
                crew.session_id
            )
            
            # Display error log
            display_error_log(crew._progress_tracker)
            
    except Exception as e:
        logger.error(f"Error displaying research dashboard: {str(e)}")
        st.sidebar.error("Error loading dashboard") 