"""Tests for the ResearchCrew class."""
import pytest
from unittest.mock import patch, MagicMock
from src.crew import ResearchCrew

@pytest.fixture
def mock_yaml():
    """Mock YAML file loading."""
    with patch("yaml.safe_load") as mock_load:
        mock_load.side_effect = [
            {
                'ollama_llm': {
                    'model': 'deepseek-coder',
                    'base_url': 'http://localhost:11434',
                    'temperature': 0.7
                }
            },
            {
                'task_templates': {
                    'default_topic': 'AI and Machine Learning',
                    'research_task': {
                        'description': 'Research task template',
                        'expected_output': 'Research results',
                        'agent': 'researcher'
                    },
                    'writing_task': {
                        'description': 'Writing task template',
                        'expected_output': 'Written content',
                        'agent': 'writer'
                    },
                    'editing_task': {
                        'description': 'Editing task template',
                        'expected_output': 'Edited content',
                        'agent': 'editor'
                    }
                }
            },
            {
                'agents': {
                    'researcher': {
                        'role': 'Research Analyst',
                        'goal': 'Research',
                        'backstory': 'Expert researcher',
                        'verbose': True,
                        'allow_delegation': True
                    },
                    'writer': {
                        'role': 'Content Writer',
                        'goal': 'Write',
                        'backstory': 'Expert writer',
                        'verbose': True,
                        'allow_delegation': True
                    },
                    'editor': {
                        'role': 'Editor in Chief',
                        'goal': 'Edit',
                        'backstory': 'Expert editor',
                        'verbose': True,
                        'allow_delegation': True
                    }
                }
            }
        ] * 10  # Multiply the list to handle multiple reads
        yield mock_load

@pytest.fixture
def mock_llm():
    """Mock LLM class."""
    with patch("src.crew.LLM") as mock_llm_class:
        mock_instance = MagicMock()
        mock_instance.model_name = 'deepseek-coder'
        mock_instance.base_url = 'http://localhost:11434'
        mock_instance.api_key = None
        mock_llm_class.return_value = mock_instance
        yield mock_llm_class

@pytest.fixture
def mock_crew():
    """Mock Crew for testing."""
    with patch('src.crew.Crew') as mock:
        yield mock

def test_llm_configuration(mock_yaml, mock_llm, mock_crew):
    """Test LLM configuration loading."""
    crew = ResearchCrew()
    expected_config = {
        'model': 'deepseek-coder',
        'base_url': 'http://localhost:11434',
        'temperature': 0.7
    }
    assert crew._llm_config == expected_config

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

def test_editor_agent_creation(mock_yaml, mock_llm):
    """Test editor agent creation."""
    crew = ResearchCrew()
    editor = crew.editor()
    assert editor.role == "Editor in Chief"
    assert editor.goal == "Edit"
    assert editor.backstory == "Expert editor"
    assert editor.verbose is True
    assert editor.allow_delegation is True

def test_editing_task_creation(mock_yaml, mock_llm, mock_crew):
    """Test editing task creation."""
    crew = ResearchCrew()
    editor = crew.editor()
    task = crew.editing_task("Test content")
    assert task.description == "Editing task template"
    assert task.expected_output == "Edited content"
    assert task.agent.role == "Editor in Chief"

def test_process_with_revisions_approved(mock_yaml, mock_llm, mock_crew):
    """Test revision process with immediate approval."""
    crew = ResearchCrew()
    mock_crew.return_value.kickoff.return_value = {
        'content': 'Approved content',
        'approved': True,
        'feedback': 'Good work'
    }
    result = crew.process_with_revisions("Test topic")
    assert result['content'] == 'Approved content'
    assert result['approved'] is True

def test_process_with_revisions_needs_revision(mock_yaml, mock_llm, mock_crew):
    """Test revision process with multiple revisions."""
    crew = ResearchCrew()
    mock_crew.return_value.kickoff.side_effect = [
        {'content': 'Draft 1', 'approved': False, 'feedback': 'Needs work'},
        {'content': 'Draft 2', 'approved': True, 'feedback': 'Much better'}
    ]
    result = crew.process_with_revisions("Test topic")
    assert result['content'] == 'Draft 2'
    assert result['approved'] is True

def test_process_with_revisions_max_reached(mock_yaml, mock_llm, mock_crew):
    """Test revision process reaching max revisions."""
    crew = ResearchCrew()
    mock_crew.return_value.kickoff.return_value = {
        'content': 'Final draft',
        'approved': False,
        'feedback': 'Still needs work'
    }
    result = crew.process_with_revisions("Test topic", max_revisions=1)
    assert result['content'] == 'Final draft'
    assert result['approved'] is False

def test_crew_creation_with_editor(mock_yaml, mock_llm, mock_crew):
    """Test crew creation includes editor agent and task."""
    crew = ResearchCrew()
    editor = crew.editor()
    task = crew.editing_task("Test content")
    assert editor.role == "Editor in Chief"
    assert task.description == "Editing task template"
    assert task.agent.role == "Editor in Chief" 