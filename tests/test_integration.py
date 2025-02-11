"""Integration tests using real services."""
import pytest
import os
from dotenv import load_dotenv
from src.crew import ResearchCrew
from src.tools.web_search import WebSearchTool
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.utils.file_manager import FileManager
from src.utils.progress_tracker import ProgressTracker
from datetime import datetime

# Load environment variables
load_dotenv()

def is_ollama_available():
    """Check if Ollama is running."""
    import requests
    try:
        response = requests.get("http://localhost:11434/api/version")
        return response.status_code == 200
    except:
        return False

def has_serpapi_key():
    """Check if SerpAPI key is configured."""
    return bool(os.getenv("SERPAPI_KEY"))

# Skip markers for tests requiring external services
requires_ollama = pytest.mark.skipif(
    not is_ollama_available(),
    reason="Ollama service is not available"
)

requires_serpapi = pytest.mark.skipif(
    not has_serpapi_key(),
    reason="SerpAPI key is not configured"
)

@requires_ollama
def test_ollama_research():
    """Test research with real Ollama LLM."""
    crew = ResearchCrew()
    result = crew.process_with_revisions("Python programming basics")
    
    # Verify response format and content
    assert isinstance(result, str)
    assert len(result) > 100  # Response should be substantial
    assert any(keyword in result.lower() for keyword in [
        "python",
        "programming",
        "code",
        "language"
    ])

@requires_serpapi
def test_web_search():
    """Test web search with real SerpAPI."""
    tool = WebSearchTool()
    results = tool.search("Latest AI developments 2024")
    
    # Verify search results
    assert results
    assert len(results) >= 3  # Should find multiple results
    assert all(isinstance(r.title, str) and r.title for r in results)
    assert all(isinstance(r.snippet, str) and r.snippet for r in results)
    assert all(isinstance(r.link, str) and r.link.startswith("http") for r in results)

@requires_ollama
@requires_serpapi
def test_full_research_flow():
    """Test complete research flow with real services."""
    crew = ResearchCrew()
    topic = "Recent developments in quantum computing"
    result = crew.process_with_revisions(topic)
    
    # Verify research quality
    assert isinstance(result, str)
    assert len(result) > 500  # Should be a comprehensive response
    assert "[1]" in result  # Should include citations
    assert "quantum" in result.lower()
    assert "comput" in result.lower()

@requires_ollama
def test_revision_process():
    """Test the revision process with real LLM."""
    crew = ResearchCrew()
    topic = "Write a very short story"
    
    # First attempt should need revision
    result = crew.process_with_revisions(topic, max_revisions=2)
    
    # Verify either approval or max revisions reached
    assert any(status in result for status in [
        "APPROVED:",
        "Max revisions",
        "NEEDS REVISION:"
    ])

@requires_ollama
@requires_serpapi
def test_research_with_web_validation():
    """Test research with web fact validation."""
    crew = ResearchCrew()
    topic = "Current Mars exploration missions"
    result = crew.process_with_revisions(topic)
    
    # Verify research includes web sources
    assert isinstance(result, str)
    assert len(result) > 300
    assert "[" in result and "]" in result  # Has citations
    assert "Source:" in result or "Reference:" in result
    
    # Verify content relevance
    assert any(keyword in result.lower() for keyword in [
        "mars",
        "nasa",
        "mission",
        "rover",
        "exploration"
    ])

@pytest.mark.asyncio
@requires_ollama
async def test_concurrent_research():
    """Test handling multiple research requests."""
    crew = ResearchCrew()
    topics = [
        "Artificial Intelligence",
        "Machine Learning",
        "Deep Learning"
    ]
    
    import asyncio
    
    async def research_topic(topic):
        return crew.process_with_revisions(topic)
    
    # Run research concurrently
    tasks = [research_topic(topic) for topic in topics]
    results = await asyncio.gather(*tasks)
    
    # Verify all research completed successfully
    assert len(results) == len(topics)
    assert all(isinstance(r, str) and len(r) > 100 for r in results)
    
    # Verify each result matches its topic
    for topic, result in zip(topics, results):
        assert any(word.lower() in result.lower() for word in topic.split())

@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    with patch('src.crew.LLM') as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield instance

@pytest.fixture
def mock_web_search():
    """Mock web search tool."""
    with patch('src.crew.WebSearchTool') as mock:
        instance = MagicMock()
        instance.search.return_value = ["Result 1", "Result 2"]
        instance.summarize_results.return_value = "Summarized results"
        mock.return_value = instance
        yield instance

@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory for test files."""
    return tmp_path

@pytest.fixture
def research_crew(mock_llm, mock_web_search, temp_dir):
    """Create ResearchCrew instance for testing."""
    with patch('src.utils.file_manager.FileManager') as mock_fm, \
         patch('src.utils.progress_tracker.ProgressTracker') as mock_pt:
        
        # Configure FileManager mock
        fm_instance = FileManager(base_dir=str(temp_dir))
        mock_fm.return_value = fm_instance
        
        # Configure ProgressTracker mock
        pt_instance = ProgressTracker("test_session", base_dir=str(temp_dir))
        mock_pt.return_value = pt_instance
        
        crew = ResearchCrew()
        yield crew

def test_complete_workflow(research_crew, temp_dir):
    """Test the complete research workflow."""
    # Mock progress callback
    progress_updates = []
    def progress_callback(agent, step, total, status):
        progress_updates.append((agent, step, total, status))
    
    research_crew._progress_callback = progress_callback
    
    # Process a topic
    result = research_crew.process_with_revisions("Test Topic")
    
    # Verify progress tracking
    assert len(progress_updates) > 0
    assert progress_updates[0][0] == "System"  # First update from system
    
    # Verify file creation
    research_dir = temp_dir / "research"
    writing_dir = temp_dir / "writing"
    editing_dir = temp_dir / "editing"
    
    assert research_dir.exists()
    assert writing_dir.exists()
    assert editing_dir.exists()
    
    # Verify files were created
    assert list(research_dir.glob("*.md"))
    assert list(writing_dir.glob("*.md"))
    assert list(editing_dir.glob("*.md"))

def test_error_handling(research_crew, mock_llm):
    """Test error handling in the workflow."""
    # Make LLM raise an error
    mock_llm.side_effect = Exception("LLM Error")
    
    # Process should handle error gracefully
    result = research_crew.process_with_revisions("Test Topic")
    assert "Error" in result
    
    # Verify error was logged
    progress = research_crew._progress_tracker.get_current_progress()
    assert len(progress["errors"]) > 0
    assert "LLM Error" in progress["errors"][0]["error"]

def test_revision_workflow(research_crew):
    """Test the revision workflow."""
    # Mock review responses
    review_responses = [
        "NEEDS REVISION: First draft needs work",
        "NEEDS REVISION: Second draft needs work",
        "APPROVED: Final version looks good"
    ]
    
    # Mock file manager to return reviews
    def mock_get_latest_file(agent_type, file_type):
        if agent_type == 'editing':
            return review_responses.pop(0) if review_responses else "APPROVED: Final"
        return "Test content"
    
    research_crew._file_manager.get_latest_file = mock_get_latest_file
    
    # Process with revisions
    result = research_crew.process_with_revisions("Test Topic")
    
    # Verify final result
    assert "Final version looks good" in result

def test_cleanup_on_interrupt(research_crew):
    """Test cleanup when interrupted."""
    # Mock cleanup methods
    research_crew._cleanup_llm = MagicMock()
    research_crew._file_manager.cleanup = MagicMock()
    research_crew._progress_tracker.cleanup = MagicMock()
    
    # Simulate interrupt
    research_crew._handle_interrupt(2, None)  # SIGINT
    
    # Verify cleanup was called
    research_crew._cleanup_llm.assert_called_once()
    research_crew._file_manager.cleanup.assert_called_once()
    research_crew._progress_tracker.cleanup.assert_called_once()

def test_progress_tracking(research_crew):
    """Test progress tracking throughout workflow."""
    progress_updates = []
    def progress_callback(agent, step, total, status):
        progress_updates.append((agent, step, total, status))
    
    research_crew._progress_callback = progress_callback
    
    # Process a topic
    research_crew.process_with_revisions("Test Topic")
    
    # Verify progress updates
    assert len(progress_updates) > 0
    
    # Check progress file
    progress = research_crew._progress_tracker.get_current_progress()
    assert progress["session_id"] == research_crew.session_id
    assert len(progress["steps"]) > 0

def test_file_based_communication(research_crew, temp_dir):
    """Test file-based communication between agents."""
    # Mock agent outputs with proper JSON structure
    research_content = {
        "content": "# Research\nTest research content",
        "metadata": {"topic": "test"},
        "timestamp": datetime.now().isoformat()
    }
    draft_content = {
        "content": "# Draft\nTest draft content",
        "metadata": {"topic": "test"},
        "timestamp": datetime.now().isoformat()
    }
    review_content = {
        "content": "APPROVED: Test review content",
        "metadata": {"status": "APPROVED", "topic": "test"},
        "timestamp": datetime.now().isoformat()
    }
    
    # Process topic
    def mock_get_latest_file(agent_type):
        if agent_type == 'research':
            return research_content
        elif agent_type == 'writing':
            return draft_content
        elif agent_type == 'editing':
            return review_content
        return None
    
    research_crew._file_manager.get_latest_research = lambda: research_content
    research_crew._file_manager.get_latest_article = lambda: draft_content
    research_crew._file_manager.get_latest_review = lambda: review_content
    
    result = research_crew.process_with_revisions("Test Topic")
    
    # Verify content flow
    assert "Test review content" in result
    
    # Verify file creation
    assert list(temp_dir.glob("**/research/*.json"))
    assert list(temp_dir.glob("**/writing/*.json"))
    assert list(temp_dir.glob("**/editing/*.json"))

def test_recovery_after_crash(research_crew, temp_dir):
    """Test recovery after a crash."""
    # Create some initial state
    research_content = {
        "content": "Test research",
        "metadata": {"topic": "test"},
        "timestamp": datetime.now().isoformat()
    }
    draft_content = {
        "content": "Test draft",
        "metadata": {"topic": "test"},
        "timestamp": datetime.now().isoformat()
    }
    
    research_crew._file_manager.save_research("Test research", {"topic": "test"})
    research_crew._file_manager.save_article("Test draft", {"topic": "test"})
    
    # Simulate crash and recovery
    session_id = research_crew.session_id
    new_crew = ResearchCrew(session_id=session_id)
    
    # Recover state
    state = new_crew._file_manager.recover_session(session_id)
    
    # Verify state recovery
    assert state is not None
    assert "research" in state
    assert state["research"]["content"] == "Test research"
    assert state["research"]["metadata"]["topic"] == "test"
    assert "writing" in state
    assert state["writing"]["content"] == "Test draft"
    assert state["writing"]["metadata"]["topic"] == "test" 