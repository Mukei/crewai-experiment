"""Tests for the ResearchCrew class."""
import pytest
from unittest.mock import patch, MagicMock
from src.crew import ResearchCrew
from crewai import Task

@pytest.fixture
def mock_yaml(mocker):
    """Mock YAML configuration loading."""
    mock = mocker.patch('yaml.safe_load')
    mock.return_value = {
        'ollama_llm': {
            'model': 'ollama/deepseek-r1',
            'base_url': 'http://localhost:11434',
            'temperature': 0.7,
            'api_key': 'not-needed',
            'context_window': 4096,
            'max_tokens': 2048,
            'provider': 'ollama'
        },
        'task_templates': {
            'default_topic': 'AI and Technology',
            'research_task': {
                'description': 'Research {topic}',
                'expected_output': 'Research findings about {topic}'
            },
            'writing_task': {
                'description': 'Write about {topic}',
                'expected_output': 'Article about {topic}'
            },
            'editing_task': {
                'description': 'Edit content about {topic}',
                'expected_output': 'Edited content about {topic}'
            }
        },
        'agents': {
            'researcher': {
                'name': 'Researcher',
                'role': 'Research Expert',
                'goal': 'Find accurate information',
                'backstory': 'Expert researcher with a focus on gathering accurate and up-to-date information from reliable sources.',
                'verbose': True,
                'allow_delegation': False
            },
            'writer': {
                'name': 'Writer',
                'role': 'Content Writer',
                'goal': 'Create engaging content',
                'backstory': 'Professional writer with expertise in creating clear, engaging, and informative content.',
                'verbose': True,
                'allow_delegation': False
            },
            'editor': {
                'name': 'Editor',
                'role': 'Senior content editor and quality controller',
                'goal': 'Ensure content accuracy, quality, and adherence to requirements',
                'backstory': 'Senior editor with extensive experience in content review and quality control. Focuses on maintaining high standards while preserving the original message.',
                'verbose': True,
                'allow_delegation': False
            }
        }
    }
    return mock

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
        'model': 'ollama/deepseek-r1',
        'base_url': 'http://localhost:11434',
        'temperature': 0.7,
        'api_key': 'not-needed',
        'context_window': 4096,
        'max_tokens': 2048,
        'provider': 'ollama'
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
    assert editor.role == "Senior content editor and quality controller"
    assert editor.goal == "Ensure content accuracy, quality, and adherence to requirements"
    assert editor.backstory == "Senior editor with extensive experience in content review and quality control. Focuses on maintaining high standards while preserving the original message."
    assert editor.allow_delegation is False

def test_editing_task_creation(mock_yaml, mock_llm, mock_crew):
    """Test editing task creation."""
    crew = ResearchCrew()
    editor = crew.editor()
    crew._current_topic = "Test topic"  # Set the topic
    
    # Mock file manager to return test content
    crew._file_manager.get_latest_file = MagicMock(side_effect=lambda agent_type, file_type: {
        'research': "Test research content",
        'writing': "Test draft content"
    }.get(agent_type, ""))
    
    task = crew.editing_task()
    
    # Verify task creation
    assert isinstance(task, Task)
    assert task.agent.role == "Senior content editor and quality controller"
    assert isinstance(task.context, list)
    assert len(task.context) > 0
    assert all(isinstance(item, str) for item in task.context)
    
    # Verify content is in context
    context_str = '\n'.join(task.context)
    assert "Test research content" in context_str
    assert "Test draft content" in context_str
    assert "Task type: editing" in context_str
    assert "Requires approval: true" in context_str

def test_process_with_revisions_approved(mock_yaml, mock_llm, mock_crew):
    """Test process_with_revisions when content is approved."""
    crew = ResearchCrew()
    
    # Mock file manager
    crew._file_manager.get_latest_file = MagicMock(return_value="APPROVED: Test content")
    
    # Mock the get_crew method to return a mock crew
    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.return_value = None  # Simulate successful completion
    crew.get_crew = MagicMock(return_value=mock_crew_instance)
    
    # Process with revisions
    processed = crew.process_with_revisions("Test topic")
    
    # Verify the result
    assert "Test content" in processed
    
    # Verify method calls
    crew.get_crew.assert_called_once_with(topic="Test topic")
    mock_crew_instance.kickoff.assert_called_once()

def test_process_with_revisions_needs_revision(mock_yaml, mock_llm, mock_crew):
    """Test process_with_revisions when content needs revision."""
    crew = ResearchCrew()
    # Mock the get_crew method to return a mock crew
    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.return_value = {
        'content': 'Test content',
        'approved': False,
        'feedback': 'NEEDS REVISION: More work needed'
    }
    crew.get_crew = MagicMock(return_value=mock_crew_instance)
    
    processed = crew.process_with_revisions("Test topic")
    assert "needs revision" in processed.lower()

def test_process_with_revisions_max_reached(mock_yaml, mock_llm, mock_crew):
    """Test revision process reaching max revisions."""
    crew = ResearchCrew()
    # Mock the get_crew method to return a mock crew
    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.return_value = {
        'content': 'Final draft',
        'approved': False,
        'feedback': 'Still needs work'
    }
    crew.get_crew = MagicMock(return_value=mock_crew_instance)
    
    result = crew.process_with_revisions("Test topic", max_revisions=1)
    assert "max revisions" in result.lower()

def test_crew_creation_with_editor(mock_yaml, mock_llm, mock_crew):
    """Test crew creation includes editor agent and task."""
    crew = ResearchCrew()
    editor = crew.editor()
    task = crew.editing_task("Test content")
    assert editor.role == "Editor in Chief"
    assert task.description == "Edit content about Test content"
    assert task.expected_output == "Edited content about Test content"

def test_cleanup_llm(mock_yaml, mock_llm):
    """Test LLM cleanup."""
    crew = ResearchCrew()
    crew._cleanup_llm()
    assert crew._llm is None

def test_recreate_llm(mock_yaml, mock_llm):
    """Test LLM recreation."""
    crew = ResearchCrew()
    crew._cleanup_llm()
    crew._recreate_llm()
    assert crew._llm is not None
    mock_llm.assert_called()

def test_perform_web_search_success(mock_yaml, mock_llm):
    """Test successful web search."""
    with patch("src.crew.WebSearchTool") as mock_tool:
        mock_instance = MagicMock()
        mock_instance.search.return_value = ["Result 1", "Result 2"]
        mock_instance.summarize_results.return_value = "Summarized results"
        mock_tool.return_value = mock_instance
        
        crew = ResearchCrew()
        result = crew._perform_web_search("test topic")
        
        assert result == "Summarized results"
        mock_instance.search.assert_called_once_with("test topic")
        mock_instance.summarize_results.assert_called_once()

def test_perform_web_search_no_results(mock_yaml, mock_llm):
    """Test web search with no results."""
    with patch("src.crew.WebSearchTool") as mock_tool:
        mock_instance = MagicMock()
        mock_instance.search.return_value = []
        mock_tool.return_value = mock_instance
        
        crew = ResearchCrew()
        result = crew._perform_web_search("test topic")
        
        assert result == "No search results found for the topic."

def test_perform_web_search_error(mock_yaml, mock_llm):
    """Test web search error handling."""
    with patch("src.crew.WebSearchTool") as mock_tool:
        mock_instance = MagicMock()
        mock_instance.search.side_effect = Exception("Search failed")
        mock_tool.return_value = mock_instance
        
        crew = ResearchCrew()
        result = crew._perform_web_search("test topic")
        
        assert "Web search failed: Search failed" in result

def test_create_web_search_tool_success(mock_yaml, mock_llm):
    """Test web search tool creation."""
    with patch("src.crew.WebSearchTool") as mock_tool:
        mock_instance = MagicMock()
        mock_instance.search.return_value = ["Result"]
        mock_instance.summarize_results.return_value = "Summary"
        mock_tool.return_value = mock_instance
        
        crew = ResearchCrew()
        tool = crew._create_web_search_tool()
        
        assert tool is not None
        assert tool.name == "Web Search Tool"
        # Test the tool by calling its run method
        result = tool.run("test topic")
        assert result == "Summary"
        mock_instance.search.assert_called_once_with("test topic")
        mock_instance.summarize_results.assert_called_once()

def test_create_web_search_tool_disabled(mock_yaml, mock_llm):
    """Test web search tool creation when disabled."""
    crew = ResearchCrew()
    crew.web_search = None
    tool = crew._create_web_search_tool()
    assert tool is None

def test_researcher_with_web_search(mock_yaml, mock_llm):
    """Test researcher agent creation with web search tool."""
    with patch("src.crew.WebSearchTool") as mock_tool:
        mock_instance = MagicMock()
        mock_tool.return_value = mock_instance
        
        crew = ResearchCrew()
        researcher = crew.researcher()
        
        assert researcher is not None
        assert len(researcher.tools) > 0

def test_researcher_without_web_search(mock_yaml, mock_llm):
    """Test researcher agent creation without web search tool."""
    crew = ResearchCrew()
    crew.web_search = None
    researcher = crew.researcher()
    
    assert researcher is not None
    assert not researcher.tools

def test_process_with_revisions_error(mock_yaml, mock_llm, mock_crew):
    """Test error handling in process_with_revisions."""
    crew = ResearchCrew()
    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.side_effect = Exception("Crew error")
    crew.get_crew = MagicMock(return_value=mock_crew_instance)
    
    result = crew.process_with_revisions("Test topic")
    assert "Error during crew execution: Crew error" in result

def test_process_with_revisions_string_result(mock_yaml, mock_llm, mock_crew):
    """Test process_with_revisions with string result."""
    crew = ResearchCrew()
    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.return_value = "Content approved"
    crew.get_crew = MagicMock(return_value=mock_crew_instance)
    
    result = crew.process_with_revisions("Test topic")
    assert "Content approved" in result

def test_research_task_creation_with_topic(mock_yaml, mock_llm):
    """Test research task creation with provided topic."""
    crew = ResearchCrew()
    task = crew.research_task("Test Topic")
    assert "Test Topic" in task.description
    assert "Test Topic" in task.expected_output

def test_writing_task_creation_with_topic_and_ref(mock_yaml, mock_llm):
    """Test writing task creation with provided topic and research task ref."""
    crew = ResearchCrew()
    research_task = crew.research_task("Test Topic")
    writing_task = crew.writing_task("Test Topic", research_task)
    assert "Test Topic" in writing_task.description
    assert "Test Topic" in writing_task.expected_output
    assert research_task in writing_task.context

def test_editing_task_creation_with_topic_and_refs(mock_yaml, mock_llm):
    """Test editing task creation with provided topic and task refs."""
    crew = ResearchCrew()
    research_task = crew.research_task("Test Topic")
    writing_task = crew.writing_task("Test Topic", research_task)
    editing_task = crew.editing_task("Test Topic", research_task, writing_task)
    assert "Test Topic" in editing_task.description
    assert "Test Topic" in editing_task.expected_output
    assert research_task in editing_task.context
    assert writing_task in editing_task.context

def test_get_crew_with_topic(mock_yaml, mock_llm):
    """Test get_crew with provided topic."""
    crew = ResearchCrew()
    test_crew = crew.get_crew("Test Topic")
    assert len(test_crew.tasks) == 3
    assert "Test Topic" in test_crew.tasks[0].description
    assert "Test Topic" in test_crew.tasks[1].description
    assert "Test Topic" in test_crew.tasks[2].description

def test_process_with_revisions_default_topic(mock_yaml, mock_llm, mock_crew):
    """Test process_with_revisions with no topic provided."""
    crew = ResearchCrew()
    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.return_value = {
        'content': 'Test content',
        'approved': True,
        'feedback': 'Good work'
    }
    crew.get_crew = MagicMock(return_value=mock_crew_instance)
    
    result = crew.process_with_revisions()
    assert "AI and Machine Learning" in result  # Default topic

def test_process_with_revisions_custom_topic(mock_yaml, mock_llm, mock_crew):
    """Test process_with_revisions with custom topic."""
    crew = ResearchCrew()
    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.return_value = {
        'content': 'Test content',
        'approved': True,
        'feedback': 'Good work'
    }
    crew.get_crew = MagicMock(return_value=mock_crew_instance)
    
    result = crew.process_with_revisions("Custom Topic")
    assert "Custom Topic" in result

def test_web_search_tool_integration(mock_yaml, mock_llm):
    """Test web search tool integration with researcher agent."""
    crew = ResearchCrew()
    
    # Mock web search tool
    with patch("src.crew.WebSearchTool") as mock_tool:
        mock_instance = MagicMock()
        mock_instance.search.return_value = ["Result 1", "Result 2"]
        mock_instance.summarize_results.return_value = "Summarized results"
        mock_tool.return_value = mock_instance
        
        # Create researcher with tool
        researcher = crew.researcher()
        assert len(researcher.tools) == 1
        
        # Test tool execution
        tool = researcher.tools[0]
        result = tool.run("test topic")
        assert result == "Summarized results"

def test_research_task_context(mock_yaml, mock_llm):
    """Test research task context structure."""
    crew = ResearchCrew()
    crew._current_topic = "Test Topic"
    
    task = crew.research_task()
    
    # Verify context is a list of strings
    assert isinstance(task.context, list)
    assert all(isinstance(item, str) for item in task.context)
    assert len(task.context) > 0
    
    # Verify no dictionary or function objects in context
    assert all(not isinstance(item, dict) for item in task.context)
    assert all(not callable(item) for item in task.context)

def test_task_creation_with_callback(mock_yaml, mock_llm):
    """Test task creation with callback handling."""
    crew = ResearchCrew()
    crew._current_topic = "Test Topic"
    
    # Create tasks
    research_task = crew.research_task()
    writing_task = crew.writing_task()
    editing_task = crew.editing_task()
    
    # Verify callbacks are properly set
    assert callable(research_task.callback)
    assert callable(writing_task.callback)
    assert callable(editing_task.callback)
    
    # Verify context doesn't contain callbacks
    for task in [research_task, writing_task, editing_task]:
        assert all(not callable(item) for item in task.context)

def test_web_search_crew_tool_run(mock_yaml, mock_llm):
    """Test WebSearchCrewTool _run method."""
    crew = ResearchCrew()
    
    # Mock web search
    with patch("src.crew.WebSearchTool") as mock_tool:
        mock_instance = MagicMock()
        mock_instance.search.return_value = ["Result 1", "Result 2"]
        mock_instance.summarize_results.return_value = "Summarized results"
        mock_tool.return_value = mock_instance
        
        # Create tool
        tool = crew._create_web_search_tool()
        assert tool is not None
        
        # Test _run method
        result = tool._run("test topic")
        assert result == "Summarized results"
        mock_instance.search.assert_called_once_with("test topic")

def test_crew_execution_flow(mock_yaml, mock_llm):
    """Test the complete crew execution flow."""
    crew = ResearchCrew()
    crew._current_topic = "Test Topic"
    
    # Mock file manager
    with patch.object(crew._file_manager, 'get_latest_file') as mock_get_file:
        mock_get_file.return_value = "Test content"
        
        # Create and execute crew
        test_crew = crew.get_crew("Test Topic")
        
        # Verify crew structure
        assert len(test_crew.tasks) == 3
        assert all(isinstance(task.context, list) for task in test_crew.tasks)
        assert all(isinstance(item, str) for task in test_crew.tasks for item in task.context)
        
        # Verify task order and dependencies
        assert isinstance(test_crew.tasks[0], Task)  # Research task
        assert isinstance(test_crew.tasks[1], Task)  # Writing task
        assert isinstance(test_crew.tasks[2], Task)  # Editing task

def test_task_template_loading(mock_yaml, mock_llm):
    """Test task template loading and validation."""
    crew = ResearchCrew()
    
    # Verify templates are loaded
    assert 'research_task' in crew._task_templates
    assert 'writing_task' in crew._task_templates
    assert 'editing_task' in crew._task_templates
    
    # Verify template structure
    for task_name in ['research_task', 'writing_task', 'editing_task']:
        template = crew._task_templates[task_name]
        assert 'description' in template
        assert 'expected_output' in template
        assert 'context' in template
        assert isinstance(template['context'], list)
        assert all(isinstance(item, str) for item in template['context'])

# Remove UI-related tests as they belong in test_chat_components.py 