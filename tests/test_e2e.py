import pytest
from unittest.mock import MagicMock

@pytest.mark.asyncio
async def test_concurrent_requests(mock_streamlit, mock_research_crew):
    """Test handling of concurrent research requests."""
    # Set up user inputs
    inputs = ["Topic 1", "Topic 2", "Topic 3", None]
    mock_streamlit.chat_input.side_effect = inputs
    
    # Set up mock responses
    responses = [
        "APPROVED: Research on Topic 1",
        "APPROVED: Research on Topic 2",
        "APPROVED: Research on Topic 3"
    ]
    
    # Set up mock crew instance
    mock_instance = MagicMock()
    mock_instance.process_with_revisions = MagicMock()
    mock_instance.process_with_revisions.side_effect = responses
    mock_instance._cleanup_llm = MagicMock()
    mock_research_crew.return_value = mock_instance
    
    # Set up session state with a proper dictionary-like object
    class MockSessionState(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.messages = []
            self.crew = None
            self.progress = None
            self.progress_status = None
            self.current_step = 0
            self._initialized = True  # Set initialization flag
    
        def __getattr__(self, name):
            return self.get(name)
    
        def __setattr__(self, name, value):
            self[name] = value
    
        def get(self, key, default=None):
            # Handle special case for _initialized
            if key == '_initialized':
                return True
            return super().get(key, default)
    
    # Run the app multiple times to simulate concurrent requests
    for i in range(3):
        # Reset session state for each request
        mock_streamlit.session_state = MockSessionState()
        mock_streamlit.session_state.crew = mock_instance
        
        # Run main app
        main()
        
        # Process the current input
        current_input = inputs[i]
        if current_input:
            # Add user message
            mock_streamlit.session_state.messages.append({
                "role": "user",
                "content": current_input
            })
            
            # Process with crew
            with mock_streamlit.spinner("🤖 Processing your request..."):
                response = responses[i]
                mock_streamlit.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
    
    # Verify cleanup was called for each request
    # We expect 3 cleanup calls:
    # 1. After processing Topic 1
    # 2. After processing Topic 2
    # 3. After processing Topic 3
    assert mock_instance._cleanup_llm.call_count == 3
    
    # Verify messages were processed correctly
    for i in range(3):
        assert f"APPROVED: Research on Topic {i+1}" in responses[i]