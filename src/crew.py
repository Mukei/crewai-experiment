"""CrewAI experiment crew configuration."""
from pathlib import Path
from typing import Callable, Dict, Any, List, Optional, Union, Tuple
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from crewai.project.crew_base import CrewBase
from crewai.project.annotations import agent, task, crew
from src.tools.web_search import WebSearchTool
from src.utils.file_manager import FileManager
from src.utils.progress_tracker import ProgressTracker
import yaml
from src.config import CONFIG_DIR
from src.utils.logging_config import crew_logger as logger, error_logger
import time
import signal
import uuid
import threading
import sys

@CrewBase
class ResearchCrew:
    """Crew for AI research and content creation."""

    def __init__(self, progress_callback: Optional[Callable] = None, session_id: Optional[str] = None):
        """Initialize the ResearchCrew."""
        logger.info("Initializing ResearchCrew")
        
        # Store session ID
        self._session_id = session_id or str(uuid.uuid4())
        logger.info(f"Using session: {self._session_id}")
        
        # Initialize file manager and progress tracker
        self._file_manager = FileManager(base_dir="temp")
        self._progress_tracker = ProgressTracker(session_id=self._session_id)
        self._progress_callback = progress_callback
        
        # Load configurations
        self._llm_config = self._load_llm_config()
        self._task_templates = self._load_task_templates()
        self._agent_configs = self._load_agent_configs()
        
        # Initialize LLM and tools
        self._llm = self._create_llm()
        self.web_search = WebSearchTool()
        
        # Register signal handlers if in main thread
        if threading.current_thread() is threading.main_thread():
            self._register_signal_handlers()
        
        # Store current topic
        self._current_topic = None
        
        logger.info("ResearchCrew initialization complete")

    def _register_signal_handlers(self):
        """Register signal handlers for cleanup."""
        def cleanup_handler(signum, frame):
            """Handle cleanup on signal."""
            logger.info(f"Received signal {signum}")
            self.cleanup()
            sys.exit(0)
            
        # Register handlers for SIGINT and SIGTERM
        signal.signal(signal.SIGINT, cleanup_handler)
        signal.signal(signal.SIGTERM, cleanup_handler)

    def _cleanup(self):
        """Cleanup resources."""
        errors = []
        
        # Clean up LLM
        if hasattr(self, '_llm'):
            try:
                self._cleanup_llm()
            except Exception as e:
                errors.append(f"LLM cleanup error: {str(e)}")
                logger.error(f"Error during LLM cleanup: {str(e)}")
        
        # Clean up file manager
        if hasattr(self, '_file_manager'):
            try:
                self._file_manager.cleanup()
            except Exception as e:
                errors.append(f"File manager cleanup error: {str(e)}")
                logger.error(f"Error during file manager cleanup: {str(e)}")
        
        # Clean up progress tracker
        if hasattr(self, '_progress_tracker'):
            try:
                self._progress_tracker.cleanup()
            except Exception as e:
                errors.append(f"Progress tracker cleanup error: {str(e)}")
                logger.error(f"Error during progress tracker cleanup: {str(e)}")
        
        # Log all errors if any occurred
        if errors:
            error_msg = "Multiple cleanup errors occurred:\n" + "\n".join(errors)
            logger.error(error_msg)

    def cleanup(self):
        """Public method to cleanup resources."""
        try:
            self._cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            # Don't re-raise to ensure cleanup completes

    def _recover_state(self, session_id: str) -> None:
        """Recover state from a previous session.
        
        Args:
            session_id: Session ID to recover
        """
        try:
            logger.info(f"Attempting to recover state for session {session_id}")
            
            # Recover file state
            state = self._file_manager.recover_session(session_id)
            if not state:
                logger.warning("No file state found for recovery")
                return
            
            # Recover progress
            progress = self._progress_tracker.recover_progress()
            if not progress:
                logger.warning("No progress state found for recovery")
                return
            
            logger.info("State recovered successfully")
            self._report_progress(
                "System",
                progress.get("current_step", 0),
                progress.get("total_steps", 3),
                "Recovered previous session state"
            )
        except Exception as e:
            logger.error(f"Error recovering state: {str(e)}")
            self._progress_tracker.log_error(f"Failed to recover state: {str(e)}")

    def save_checkpoint(self) -> None:
        """Save a checkpoint of the current state."""
        try:
            logger.info("Saving checkpoint")
            # Progress is automatically saved by ProgressTracker
            # Files are automatically saved by FileManager
            # Just log the checkpoint
            self._progress_tracker.update_progress(
                "System",
                self._progress_tracker.get_current_progress().get("current_step", 0),
                self._progress_tracker.get_current_progress().get("total_steps", 3),
                "Checkpoint saved"
            )
            logger.info("Checkpoint saved successfully")
        except Exception as e:
            logger.error(f"Error saving checkpoint: {str(e)}")
            self._progress_tracker.log_error(f"Failed to save checkpoint: {str(e)}")

    def _handle_interrupt(self, signum, frame):
        """Handle interrupt signals."""
        logger.info(f"Received signal {signum}")
        self.cleanup()
        
    def _report_progress(self, agent: str, step: int, total: int, status: str) -> None:
        """Report progress through callback and tracker."""
        try:
            # Update progress tracker
            self._progress_tracker.update_progress(agent, step, total, status)
            
            # Call progress callback if available
            if self._progress_callback:
                self._progress_callback(agent, step, total, status)
                
            logger.debug(f"Progress updated: {agent} - Step {step}/{total} - {status}")
        except Exception as e:
            logger.error(f"Error in progress reporting: {str(e)}")

    def _load_llm_config(self) -> Dict:
        """Load LLM configuration from YAML."""
        logger.info("Loading LLM configuration")
        config_path = CONFIG_DIR / 'llm.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)
        logger.debug(f"Loaded LLM config: {config['ollama_llm']}")
        return config['ollama_llm']

    def _create_llm(self) -> LLM:
        """Create an LLM instance with the loaded configuration."""
        logger.info("Creating LLM instance")
        try:
            # Add retry logic for LLM creation
            max_retries = 3
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                try:
                    llm = LLM(
                        model=self._llm_config.get('model', 'ollama/deepseek-r1'),
                        base_url=self._llm_config.get('base_url', 'http://localhost:11434'),
                        temperature=self._llm_config.get('temperature', 0.7),
                        api_key=self._llm_config.get('api_key', 'not-needed'),
                        max_tokens=self._llm_config.get('max_tokens', 2048)
                    )
                    logger.info(f"LLM instance created successfully with model {self._llm_config.get('model')}")
                    return llm
                except Exception as e:
                    last_error = e
                    retry_count += 1
                    logger.warning(f"LLM creation attempt {retry_count} failed: {str(e)}")
                    time.sleep(1)  # Wait before retrying
            
            raise last_error
        except Exception as e:
            logger.error(f"Failed to create LLM: {str(e)}")
            raise

    def _cleanup_llm(self) -> None:
        """Clean up LLM resources safely."""
        if hasattr(self, '_llm') and self._llm is not None:
            try:
                logger.info("Cleaning up LLM resources")
                # Store the LLM instance temporarily
                temp_llm = self._llm
                self._llm = None
                # Ensure we have a bit of time for pending operations
                time.sleep(1)  # Increased wait time
                # Clean up the old instance
                if hasattr(temp_llm, 'cleanup'):
                    temp_llm.cleanup()
                del temp_llm
                logger.info("LLM resources cleaned up successfully")
            except Exception as e:
                logger.error(f"Error during LLM cleanup: {str(e)}")

    def _recreate_llm(self) -> None:
        """Recreate the LLM instance if needed."""
        try:
            self._llm = self._create_llm()
            logger.info("Successfully recreated LLM instance")
        except Exception as e:
            logger.error(f"Failed to recreate LLM: {str(e)}")
            raise

    def _load_task_templates(self) -> Dict:
        """Load task templates from YAML."""
        logger.info("Loading task templates")
        try:
            config_path = CONFIG_DIR / 'tasks.yaml'
            logger.debug(f"Loading task templates from: {config_path}")
            
            with open(config_path) as f:
                raw_yaml = f.read()
                logger.debug(f"Raw YAML content:\n{raw_yaml}")
                config = yaml.safe_load(raw_yaml)
                
            logger.debug(f"Loaded config: {config}")
            templates = config.get('task_templates', {})
            logger.debug(f"Extracted templates: {templates}")
            
            if not templates:
                raise ValueError("No task templates found in configuration")
                
            # Validate template structure
            required_tasks = ['research_task', 'writing_task', 'editing_task']
            for task in required_tasks:
                if task not in templates:
                    raise ValueError(f"Missing required task template: {task}")
                if not isinstance(templates[task], dict):
                    raise ValueError(f"Invalid template format for {task}")
                if 'description' not in templates[task] or 'expected_output' not in templates[task]:
                    raise ValueError(f"Missing required fields in {task} template")
            
            logger.info(f"Successfully loaded {len(templates)} task templates")
            return templates
        except Exception as e:
            logger.error(f"Error loading task templates: {str(e)}")
            raise

    def _load_agent_configs(self) -> Dict:
        """Load agent configurations from YAML."""
        logger.info("Loading agent configurations")
        config_path = CONFIG_DIR / 'agents.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)
        logger.debug(f"Loaded {len(config['agents'])} agent configurations")
        return config['agents']

    def _perform_web_search(self, topic: str) -> str:
        """Perform web search for the given topic."""
        if not self.web_search:
            error_msg = "Web search is not available - please check your SERPAPI_KEY"
            logger.warning(error_msg)
            return error_msg
        
        try:
            logger.info(f"Performing web search for topic: {topic}")
            results = self.web_search.search(topic)
            logger.info(f"Found {len(results)} search results")
            if not results:
                return "No search results found for the topic."
            summary = self.web_search.summarize_results(results)
            logger.info("Search results summarized successfully")
            return summary
        except Exception as e:
            error_msg = f"Web search failed: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            return error_msg

    def _create_web_search_tool(self):
        """Create a CrewAI Tool for web search."""
        logger.info("Creating web search tool")
        
        try:
            web_search = WebSearchTool()
            if not web_search.api_key:
                logger.warning("Web search tool not available - SERPAPI_KEY missing")
                return None
            return web_search
        except Exception as e:
            logger.error(f"Failed to create web search tool: {str(e)}")
            return None

    @agent
    def researcher(self) -> Agent:
        """Create the researcher agent."""
        config = self._agent_configs["researcher"]
        tools = []
        
        # Create and add web search tool
        web_search = self._create_web_search_tool()
        if web_search:
            tools.append(web_search)
            logger.info("Added web search tool to researcher agent")
        
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=tools,
            llm=self._llm,
            verbose=config.get('verbose', True)
        )

    @agent
    def writer(self) -> Agent:
        """Create the writer agent."""
        config = self._agent_configs["writer"]
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            llm=self._llm,
            verbose=config.get('verbose', True)
        )

    @agent
    def editor(self) -> Agent:
        """Create the editor agent."""
        config = self._agent_configs["editor"]
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            llm=self._llm,
            verbose=config.get('verbose', True)
        )

    @task
    def research_task(self) -> Task:
        """Create a research task."""
        if not self._current_topic:
            raise ValueError("No topic set for research task")
        
        template = self._task_templates['research_task']
        return Task(
            description=template['description'].format(topic=self._current_topic),
            expected_output=template['expected_output'].format(topic=self._current_topic),
            agent=self.researcher()
        )

    @task
    def writing_task(self) -> Task:
        """Create a writing task."""
        if not self._current_topic:
            raise ValueError("No topic set for writing task")
            
        template = self._task_templates['writing_task']
        return Task(
            description=template['description'].format(topic=self._current_topic),
            expected_output=template['expected_output'].format(topic=self._current_topic),
            agent=self.writer()
        )

    @task
    def editing_task(self) -> Task:
        """Create an editing task."""
        if not self._current_topic:
            raise ValueError("No topic set for editing task")
            
        template = self._task_templates['editing_task']
        return Task(
            description=template['description'].format(topic=self._current_topic),
            expected_output=template['expected_output'].format(topic=self._current_topic),
            agent=self.editor()
        )

    @crew
    def get_crew(self, topic: str) -> Crew:
        """Get a crew for the given topic."""
        self._current_topic = topic
        logger.info(f"Creating crew for topic: {topic}")
        
        return Crew(
            agents=[
                self.researcher(),
                self.writer(),
                self.editor()
            ],
            tasks=[
                self.research_task(),
                self.writing_task(),
                self.editing_task()
            ],
            verbose=True
        )

    def process_with_revisions(self, topic: Optional[str] = None, max_revisions: int = 3) -> str:
        """Process a topic with revisions until approved or max revisions reached."""
        if not topic:
            logger.warning("No topic provided, using default")
            topic = self._task_templates.get("default_topic", "AI and Machine Learning")
        
        self._current_topic = topic
        logger.info(f"Starting process with revisions for topic: {topic}")
        
        try:
            crew = self.get_crew(topic)
            result = crew.kickoff()
            
            # Handle different result types
            if result is None:
                error_msg = "Error: No response received from crew"
                logger.error(error_msg)
                return error_msg
            
            # Convert result to string if it's not already
            final_result = str(result)
            
            # Check if the editor approved the content
            if "APPROVED:" in final_result:
                logger.info("Content approved by editor")
            elif "NEEDS REVISION:" in final_result:
                logger.info("Content needs revision - check editor's feedback")
            else:
                logger.warning("Unexpected editor response format")
            
            return final_result
                
        except Exception as e:
            error_msg = f"Error during crew execution: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg
        finally:
            # Delay cleanup to ensure all operations are complete
            time.sleep(1)
            self.cleanup()