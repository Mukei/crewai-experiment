"""Tests for FileManager class."""
import json
import pytest
from pathlib import Path
from src.utils.file_manager import FileManager

@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path

@pytest.fixture
def file_manager(temp_dir):
    """Create a FileManager instance for testing."""
    return FileManager(session_id="test_session", base_dir=str(temp_dir))

def test_directory_setup(file_manager, temp_dir):
    """Test that directories are created correctly."""
    expected_dirs = ['research', 'writing', 'editing']
    for dir_name in expected_dirs:
        assert (temp_dir / dir_name).exists()
        assert (temp_dir / dir_name).is_dir()

def test_save_research(file_manager):
    """Test saving research content."""
    content = "# Research Findings\nTest content"
    file_path = file_manager.save_research(content)
    
    # Check file was created
    assert file_path.exists()
    assert file_path.is_file()
    
    # Check content
    with open(file_path) as f:
        data = json.load(f)
        assert data["content"] == content
        assert "metadata" in data
        assert "timestamp" in data

def test_save_article(file_manager):
    """Test saving article content."""
    content = "# Article\nTest content"
    file_path = file_manager.save_article(content)
    
    # Check file was created
    assert file_path.exists()
    assert file_path.is_file()
    
    # Check content
    with open(file_path) as f:
        data = json.load(f)
        assert data["content"] == content
        assert "metadata" in data
        assert "timestamp" in data

def test_save_review(file_manager):
    """Test saving editor's review."""
    content = "Review content"
    
    # Test approved review
    file_path = file_manager.save_review(content, approved=True)
    assert file_path.exists()
    with open(file_path) as f:
        data = json.load(f)
        assert data["content"] == content
        assert data["metadata"]["status"] == "APPROVED"
        assert "timestamp" in data
    
    # Test needs revision
    file_path = file_manager.save_review(content, approved=False)
    assert file_path.exists()
    with open(file_path) as f:
        data = json.load(f)
        assert data["content"] == content
        assert data["metadata"]["status"] == "NEEDS_REVISION"
        assert "timestamp" in data

def test_get_latest_research(file_manager):
    """Test getting latest research content."""
    content1 = "First research"
    content2 = "Second research"
    
    file_manager.save_research(content1)
    file_manager.save_research(content2)
    
    latest = file_manager.get_latest_research()
    assert latest["content"] == content2
    assert "metadata" in latest
    assert "timestamp" in latest

def test_get_latest_article(file_manager):
    """Test getting latest article content."""
    content1 = "First article"
    content2 = "Second article"
    
    file_manager.save_article(content1)
    file_manager.save_article(content2)
    
    latest = file_manager.get_latest_article()
    assert latest["content"] == content2
    assert "metadata" in latest
    assert "timestamp" in latest

def test_get_latest_review(file_manager):
    """Test getting latest review with status."""
    content = "Review content"
    
    # Save approved review
    file_manager.save_review(content, approved=True)
    review = file_manager.get_latest_review()
    
    assert review is not None
    assert review["metadata"]["status"] == "APPROVED"
    assert review["content"] == content
    
    # Save needs revision review
    file_manager.save_review(content, approved=False)
    review = file_manager.get_latest_review()
    
    assert review is not None
    assert review["metadata"]["status"] == "NEEDS_REVISION"
    assert review["content"] == content

def test_cleanup(file_manager, temp_dir):
    """Test cleaning up all files."""
    # Create some files
    file_manager.save_research("Research content")
    file_manager.save_article("Article content")
    file_manager.save_review("Review content", True)
    
    # Verify files exist
    assert list(temp_dir.glob("**/*.json"))
    
    # Clean up
    file_manager.cleanup()
    
    # Verify all files are removed
    assert not temp_dir.exists()

def test_get_all_files(file_manager):
    """Test getting all files organized by type."""
    # Create some files
    file_manager.save_research("Research content")
    file_manager.save_article("Article content")
    file_manager.save_review("Review content", True)
    
    files = file_manager.get_all_files()
    
    assert "research" in files
    assert "writing" in files
    assert "editing" in files
    assert len(files["research"]) == 1
    assert len(files["writing"]) == 1
    assert len(files["editing"]) == 2  # One review and one final version
    
    # Verify all files are JSON
    for file_list in files.values():
        for file_path in file_list:
            assert file_path.suffix == ".json"

def test_save_draft(file_manager):
    """Test saving draft content."""
    content = "# Draft\nTest content"
    file_path = file_manager.save_draft(content)
    
    # Check file was created
    assert file_path.exists()
    assert file_path.is_file()
    
    # Check content
    with open(file_path) as f:
        data = json.load(f)
        assert data["content"] == content
        assert "metadata" in data
        assert "timestamp" in data

def test_get_latest_draft(file_manager):
    """Test getting latest draft content."""
    content1 = "First draft"
    content2 = "Second draft"
    
    file_manager.save_draft(content1)
    file_manager.save_draft(content2)
    
    latest = file_manager.get_latest_draft()
    assert latest["content"] == content2
    assert "metadata" in latest
    assert "timestamp" in latest 