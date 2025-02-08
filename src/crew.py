"""CrewAI experiment crew configuration."""
from pathlib import Path
from typing import Callable
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from crewai.project.crew_base import CrewBase
from crewai.project.annotations import agent, task, crew
from src.tools.web_search import WebSearchTool
import yaml

@CrewBase
class ResearchCrew:
    """Crew for AI research and content creation."""

    def __init__(self, default_topic: str = "AI and Machine Learning"):
        """Initialize the crew with configurations."""
        self.config_dir = Path(__file__).parent / "config"
        self.llm = self._load_llm()
        self.task_templates = self._load_task_templates()
        self.agent_configs = self._load_agent_configs()
        self.default_topic = default_topic
        try:
            self.web_search = WebSearchTool()
        except ValueError as e:
            print(f"Warning: Web search disabled - {str(e)}")
            self.web_search = None

    def _load_llm(self):
        """Load LLM configuration from YAML."""
        with open(self.config_dir / "llm.yaml", "r") as f:
            config = yaml.safe_load(f)
            llm_config = config['ollama_llm']
            # Only use supported parameters
            return LLM(
                model=llm_config['model'],
                base_url=llm_config['base_url'],
                temperature=llm_config['temperature']
            )

    def _load_agent_configs(self):
        """Load agent configurations from YAML."""
        with open(self.config_dir / "agents.yaml", "r") as f:
            return yaml.safe_load(f)

    def _load_task_templates(self):
        """Load task templates from YAML."""
        with open(self.config_dir / "tasks.yaml", "r") as f:
            return yaml.safe_load(f)

    def _perform_web_search(self, topic: str) -> str:
        """Perform web search for the given topic."""
        if not self.web_search:
            return "Web search is not available."
        
        try:
            results = self.web_search.search(topic)
            return self.web_search.summarize_results(results)
        except Exception as e:
            return f"Web search failed: {str(e)}"

    def _create_web_search_tool(self):
        """Create a CrewAI Tool for web search."""
        @tool("Web Search Tool")
        def web_search(topic: str) -> str:
            """Search the web for information about a given topic."""
            return self._perform_web_search(topic)
        
        return web_search

    @agent
    def researcher(self) -> Agent:
        """Create the researcher agent."""
        config = self.agent_configs["researcher"]
        tools = [self._create_web_search_tool()] if self.web_search else []
        return Agent(
            **config,
            llm=self.llm,
            tools=tools
        )

    @agent
    def writer(self) -> Agent:
        """Create the writer agent."""
        config = self.agent_configs["writer"]
        return Agent(
            **config,
            llm=self.llm
        )

    @task
    def research_task(self, topic: str = None) -> Task:
        """Create the research task."""
        topic = topic or self.default_topic
        config = self.task_templates["research_task"]
        description = config["description"].format(topic=topic)
        
        # Add web search instructions if available
        if self.web_search:
            description += "\nUse the web_search tool to gather recent information and verify facts."
        
        return Task(
            description=description,
            expected_output=config["expected_output"].format(topic=topic),
            agent=self.researcher()
        )

    @task
    def writing_task(self, topic: str = None) -> Task:
        """Create the writing task."""
        topic = topic or self.default_topic
        config = self.task_templates["writing_task"]
        return Task(
            description=config["description"].format(topic=topic),
            expected_output=config["expected_output"].format(topic=topic),
            agent=self.writer(),
            context=[self.research_task(topic)]
        )

    @crew
    def get_crew(self, topic: str = None) -> Crew:
        """Create and return the configured crew."""
        topic = topic or self.default_topic
        return Crew(
            agents=[self.researcher(), self.writer()],
            tasks=[
                self.research_task(topic),
                self.writing_task(topic)
            ],
            verbose=True
        ) 