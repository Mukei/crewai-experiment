"""Tests for ProgressTracker class."""
import pytest
import json
from pathlib import Path
from datetime import datetime
from src.utils.progress_tracker import ProgressTracker

@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path

@pytest.fixture
def progress_tracker(temp_dir):
    """Create a ProgressTracker instance for testing."""
    return ProgressTracker("test_session", base_dir=str(temp_dir))

def test_initialization(progress_tracker, temp_dir):
    """Test progress tracker initialization."""
    # Check directory creation
    assert (temp_dir).exists()
    assert (temp_dir).is_dir()
    
    # Check progress file creation
    progress_file = temp_dir / "test_session_progress.json"
    assert progress_file.exists()
    
    # Check initial content
    with open(progress_file) as f:
        progress = json.load(f)
        assert progress["session_id"] == "test_session"
        assert progress["current_step"] == 0
        assert progress["total_steps"] == 0
        assert progress["status"] == "Initializing"
        assert progress["agent"] == "System"
        assert isinstance(progress["start_time"], str)
        assert isinstance(datetime.fromisoformat(progress["start_time"]), datetime)

def test_update_progress(progress_tracker):
    """Test updating progress information."""
    progress_tracker.update_progress("Researcher", 1, 3, "Researching")
    
    progress = progress_tracker.get_current_progress()
    assert progress["current_step"] == 1
    assert progress["total_steps"] == 3
    assert progress["status"] == "Researching"
    assert progress["agent"] == "Researcher"
    assert len(progress["steps"]) == 1
    
    step = progress["steps"][0]
    assert step["agent"] == "Researcher"
    assert step["step"] == 1
    assert step["total"] == 3
    assert step["status"] == "Researching"

def test_log_error(progress_tracker):
    """Test error logging."""
    error_msg = "Test error"
    progress_tracker.log_error(error_msg)
    
    progress = progress_tracker.get_current_progress()
    assert len(progress["errors"]) == 1
    assert progress["errors"][0]["error"] == error_msg
    assert isinstance(progress["errors"][0]["timestamp"], str)

def test_get_step_history(progress_tracker):
    """Test retrieving step history."""
    # Add multiple steps
    progress_tracker.update_progress("Researcher", 1, 3, "Step 1")
    progress_tracker.update_progress("Writer", 2, 3, "Step 2")
    progress_tracker.update_progress("Editor", 3, 3, "Step 3")
    
    history = progress_tracker.get_step_history()
    assert len(history) == 3
    assert history[0]["agent"] == "Researcher"
    assert history[1]["agent"] == "Writer"
    assert history[2]["agent"] == "Editor"

def test_get_errors(progress_tracker):
    """Test retrieving errors."""
    # Add multiple errors
    progress_tracker.log_error("Error 1")
    progress_tracker.log_error("Error 2")
    
    errors = progress_tracker.get_errors()
    assert len(errors) == 2
    assert errors[0]["error"] == "Error 1"
    assert errors[1]["error"] == "Error 2"

def test_cleanup(progress_tracker, temp_dir):
    """Test cleaning up progress files."""
    # Create some progress
    progress_tracker.update_progress("Test", 1, 1, "Testing")
    
    # Clean up
    progress_tracker.cleanup()
    
    # Check file is removed
    progress_file = temp_dir / "test_session_progress.json"
    assert not progress_file.exists()

def test_recover_progress(temp_dir):
    """Test progress recovery."""
    # Create initial progress
    tracker1 = ProgressTracker("recover_test", base_dir=str(temp_dir))
    tracker1.update_progress("Test", 1, 2, "Testing")
    
    # Create new tracker with same session
    tracker2 = ProgressTracker("recover_test", base_dir=str(temp_dir))
    recovered = tracker2.recover_progress()
    
    assert recovered is not None
    assert recovered["session_id"] == "recover_test"
    assert recovered["current_step"] == 1
    assert recovered["total_steps"] == 2
    assert recovered["status"] == "Testing"
    assert recovered["agent"] == "Test"

def test_progress_file_corruption(progress_tracker, temp_dir):
    """Test handling of corrupted progress file."""
    # Write invalid JSON
    progress_file = temp_dir / "test_session_progress.json"
    progress_file.write_text("invalid json")
    
    # Should handle gracefully and reinitialize
    progress = progress_tracker.get_current_progress()
    assert progress["session_id"] == "test_session"
    assert progress["current_step"] == 0

def test_concurrent_updates(temp_dir):
    """Test concurrent updates from multiple trackers."""
    # Create two trackers for same session
    tracker1 = ProgressTracker("shared_session", base_dir=str(temp_dir))
    tracker2 = ProgressTracker("shared_session", base_dir=str(temp_dir))
    
    # Update from both
    tracker1.update_progress("Agent1", 1, 3, "Step 1")
    tracker2.update_progress("Agent2", 2, 3, "Step 2")
    
    # Check both updates are recorded
    history = tracker1.get_step_history()
    assert len(history) == 2
    assert history[0]["agent"] == "Agent1"
    assert history[1]["agent"] == "Agent2" 