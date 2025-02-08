"""Tests for the ResearchCrew class."""
import pytest
from unittest.mock import patch, MagicMock
from src.crew import ResearchCrew

@pytest.fixture
def mock_yaml():
    """Mock YAML file loading."""
    with patch("src.crew.yaml.safe_load") as mock_load:
        mock_load.return_value = {
            'ollama_llm': {
                'model': 'deepseek-r1',
                'base_url': 'http://localhost:11434',
                'temperature': 0.7
            }
        }
        yield mock_load

@pytest.fixture
def mock_llm():
    """Mock LLM class."""
    with patch("src.crew.LLM") as mock_llm_class:
        mock_instance = MagicMock()
        mock_llm_class.return_value = mock_instance
        yield mock_llm_class

def test_llm_configuration(mock_yaml, mock_llm):
    """Test LLM configuration loading."""
    crew = ResearchCrew()
    
    # Check that LLM was created with correct parameters
    mock_llm.assert_called_once_with(
        model='deepseek-r1',
        base_url='http://localhost:11434',
        temperature=0.7
    )

def test_web_search_disabled_without_api_key(mock_yaml, mock_llm):
    """Test web search is disabled when API key is missing."""
    with patch("src.crew.WebSearchTool.__init__", side_effect=ValueError("No API key")):
        crew = ResearchCrew()
        assert crew.web_search is None

def test_web_search_enabled_with_api_key(mock_yaml, mock_llm):
    """Test web search is enabled when API key is present."""
    with patch("src.crew.WebSearchTool.__init__", return_value=None):
        crew = ResearchCrew()
        assert crew.web_search is not None 