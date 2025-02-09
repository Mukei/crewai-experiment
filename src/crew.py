"""CrewAI experiment crew configuration."""
from pathlib import Path
from typing import Callable, Dict, Any, List, Optional, Union, Tuple
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from crewai.project.crew_base import CrewBase
from crewai.project.annotations import agent, task, crew
from src.tools.web_search import WebSearchTool
import yaml
from src.config import CONFIG_DIR
from src.utils import crew_logger as logger, error_logger
import time

@CrewBase
class ResearchCrew:
    """Crew for AI research and content creation."""

    def __init__(self):
        """Initialize the research crew with configuration."""
        logger.info("Initializing ResearchCrew")
        self._llm_config = self._load_llm_config()
        self._task_templates = self._load_task_templates()
        self._agent_configs = self._load_agent_configs()
        self._llm = self._create_llm()
        try:
            logger.info("Initializing web search tool...")
            self.web_search = WebSearchTool()
            logger.info("Web search tool initialized successfully")
        except Exception as e:
            error_logger.error(f"Failed to initialize web search tool: {str(e)}", exc_info=True)
            self.web_search = None

    def _load_llm_config(self) -> Dict:
        """Load LLM configuration from YAML."""
        logger.info("Loading LLM configuration")
        config_path = CONFIG_DIR / 'llm.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)
        logger.debug(f"Loaded LLM config: {config['ollama_llm']}")
        return config['ollama_llm']

    def _create_llm(self) -> LLM:
        """Create LLM instance with configuration."""
        try:
            logger.info("Creating LLM instance")
            llm = LLM(
                model=self._llm_config['model'],
                base_url=self._llm_config['api_base'],
                temperature=self._llm_config['temperature'],
                api_key=self._llm_config['api_key'],
                timeout=30  # Add timeout to prevent hanging
            )
            logger.info(f"LLM instance created successfully with model {self._llm_config['model']}")
            return llm
        except Exception as e:
            error_msg = f"Failed to create LLM: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            raise

    def _cleanup_llm(self) -> None:
        """Clean up LLM resources safely."""
        if hasattr(self, '_llm') and self._llm is not None:
            try:
                logger.info("Cleaning up LLM resources")
                # Give time for any pending operations to complete
                time.sleep(1)
                self._llm = None
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
        config_path = CONFIG_DIR / 'tasks.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)
        logger.debug(f"Loaded {len(config['task_templates'])} task templates")
        return config['task_templates']

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
        
        if not self.web_search:
            logger.warning("Web search tool not available - SERPAPI_KEY missing")
            return None
            
        @tool("Web Search Tool")
        def web_search(topic: str) -> str:
            """Search the web for information about a given topic."""
            try:
                results = self._perform_web_search(topic)
                if not results:
                    return "⚠️ No search results found. Please check your query or try again."
                return results
            except Exception as e:
                logger.error(f"Web search failed: {str(e)}", exc_info=True)
                return f"⚠️ Web search failed: {str(e)}"
        
        return web_search

    @agent
    def researcher(self) -> Agent:
        """Create the researcher agent."""
        logger.info("Creating researcher agent")
        config = self._agent_configs["researcher"].copy()
        tools = []
        
        # Create and add web search tool
        web_search_tool = self._create_web_search_tool()
        if web_search_tool:
            logger.info("Adding web search tool to researcher agent")
            tools.append(web_search_tool)
        else:
            logger.warning("Researcher will proceed without web search capability")
            
        config['tools'] = tools
        config['llm'] = self._llm
        logger.debug(f"Researcher agent config: {config}")
        return Agent(**config)

    @agent
    def writer(self) -> Agent:
        """Create the writer agent."""
        logger.info("Creating writer agent")
        config = self._agent_configs["writer"].copy()
        config['llm'] = self._llm
        logger.debug(f"Writer agent config: {config}")
        return Agent(**config)

    @agent
    def editor(self) -> Agent:
        """Create the editor agent."""
        logger.info("Creating editor agent")
        config = self._agent_configs["editor"].copy()
        config['llm'] = self._llm
        logger.debug(f"Editor agent config: {config}")
        return Agent(**config)

    @task
    def research_task(self, topic: str = None) -> Task:
        """Create the research task."""
        topic = topic or self._task_templates["default_topic"]
        logger.info(f"Creating research task for topic: {topic}")
        config = self._task_templates["research_task"]
        description = config["description"].format(topic=topic)
        
        # Add web search instructions if available
        if self.web_search:
            description += "\nUse the web_search tool to gather recent information and verify facts."
        
        task = Task(
            description=description,
            expected_output=config["expected_output"].format(topic=topic),
            agent=self.researcher()
        )
        logger.debug(f"Research task created: {task}")
        return task

    @task
    def writing_task(self, topic: str = None, research_output: str = None) -> Task:
        """Create the writing task."""
        topic = topic or self._task_templates["default_topic"]
        logger.info(f"Creating writing task for topic: {topic}")
        config = self._task_templates["writing_task"]
        task = Task(
            description=config["description"].format(topic=topic),
            expected_output=config["expected_output"].format(topic=topic),
            agent=self.writer(),
            context=[self.research_task(topic)] if not research_output else [research_output]
        )
        logger.debug(f"Writing task created: {task}")
        return task

    @task
    def editing_task(self, topic: str = None, research_output: str = None, writing_output: str = None) -> Task:
        """Create the editing task."""
        topic = topic or self._task_templates["default_topic"]
        logger.info(f"Creating editing task for topic: {topic}")
        config = self._task_templates["editing_task"]
        context = []
        if research_output:
            context.append(research_output)
        if writing_output:
            context.append(writing_output)
        if not context:
            context = [self.research_task(topic), self.writing_task(topic)]
        
        task = Task(
            description=config["description"].format(topic=topic),
            expected_output=config["expected_output"].format(topic=topic),
            agent=self.editor(),
            context=context
        )
        logger.debug(f"Editing task created: {task}")
        return task

    @crew
    def get_crew(self, topic: str) -> Crew:
        """Get a crew for the given topic."""
        logger.info(f"Creating crew for topic: {topic}")
        
        # Initialize LLM if not already done
        if not hasattr(self, '_llm') or self._llm is None:
            self._llm = self._create_llm()
        
        # Create tasks
        research_task = self.research_task(topic)
        writing_task = self.writing_task(topic)
        editing_task = self.editing_task(topic)
        
        # Create agents with the same LLM instance
        researcher = self.researcher()
        writer = self.writer()
        editor = self.editor()
        
        # Create and return crew
        crew = Crew(
            agents=[researcher, writer, editor],
            tasks=[research_task, writing_task, editing_task],
            verbose=True
        )
        
        return crew

    def process_with_revisions(self, topic: str, max_revisions: int = 3) -> Tuple[str, str]:
        """Process a topic with revisions until approved or max revisions reached."""
        logger.info(f"Starting process with revisions for topic: {topic} (max_revisions={max_revisions})")
        
        revision_count = 0
        last_content = ""
        last_feedback = ""
        
        try:
            while revision_count < max_revisions:
                logger.info(f"Starting revision {revision_count + 1}")
                
                # Get crew with shared LLM instance
                crew = self.get_crew(topic)
                
                # Add previous feedback to context if available
                if last_feedback:
                    logger.info("Adding previous feedback to context")
                    for task in crew.tasks:
                        task.context.append(f"Previous feedback: {last_feedback}")
                
                # Run the crew tasks
                results = crew.kickoff()
                
                # Process results
                if isinstance(results, str):
                    content = results
                    feedback = "No explicit feedback provided"
                else:
                    content = results[1] if len(results) > 1 else results[0]
                    feedback = results[2] if len(results) > 2 else "No explicit feedback provided"
                
                # Check for approval
                if feedback.startswith("APPROVED:"):
                    logger.info("Content approved by editor")
                    return content, "Content approved by editor"
                
                # Store for next iteration
                last_content = content
                last_feedback = feedback
                revision_count += 1
                
                logger.info(f"Content needs revision. Feedback: {feedback}")
                
                # Clean up LLM before next iteration
                self._cleanup_llm()
            
            # Max revisions reached
            logger.warning(f"Maximum revisions ({max_revisions}) reached without approval")
            return last_content, f"⚠️ Maximum revisions ({max_revisions}) reached. Last feedback: {last_feedback}"
                
        except Exception as e:
            logger.error(f"Error during crew execution: {str(e)}", exc_info=True)
            self._cleanup_llm()
            raise
        finally:
            self._cleanup_llm() 