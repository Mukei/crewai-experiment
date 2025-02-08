"""Streamlit chat interface for CrewAI experiment."""
import streamlit as st
from crew import ResearchCrew

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "crew" not in st.session_state:
        st.session_state.crew = ResearchCrew().crew()

def display_chat_messages():
    """Display all messages in the chat."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def process_user_input(user_input: str):
    """Process user input and get AI response."""
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Show processing message
        with st.chat_message("assistant"):
            with st.spinner("Researching..."):
                try:
                    # Get response from CrewAI
                    response = st.session_state.crew.kickoff()
                    # Add AI response to chat
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.session_state.messages.append({"role": "system", "content": f"❌ {error_msg}"})

def main():
    """Main function to run the Streamlit app."""
    st.title("AI Research Assistant")
    st.markdown("""
    Ask me to research any topic, and I'll provide a comprehensive analysis.
    """)

    # Initialize session state
    initialize_session_state()

    # Display chat messages
    display_chat_messages()

    # Chat input
    if user_input := st.chat_input("What would you like me to research?"):
        process_user_input(user_input)

if __name__ == "__main__":
    main() 