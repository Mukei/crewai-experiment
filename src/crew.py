"""CrewAI experiment crew configuration."""
from pathlib import Path
from crewai import Agent, Task, Crew, LLM
import yaml

class ResearchCrew:
    """Crew for AI research and content creation."""

    def __init__(self):
        """Initialize the crew with configurations."""
        self.config_dir = Path(__file__).parent / "config"
        self.llm = self._load_llm()
        self.agents = self._load_agents()
        self.tasks = self._load_tasks()

    def _load_llm(self):
        """Load LLM configuration from YAML."""
        with open(self.config_dir / "llm.yaml", "r") as f:
            config = yaml.safe_load(f)
            return LLM(**config['ollama_llm'])

    def _load_agents(self):
        """Load agent configurations from YAML."""
        with open(self.config_dir / "agents.yaml", "r") as f:
            configs = yaml.safe_load(f)
        
        agents = {}
        for name, config in configs.items():
            agents[name] = Agent(
                **config,
                llm=self.llm
            )
        return agents

    def _load_tasks(self):
        """Load task configurations from YAML."""
        with open(self.config_dir / "tasks.yaml", "r") as f:
            configs = yaml.safe_load(f)
        
        tasks = []
        for name, config in configs.items():
            task = Task(
                description=config['description'],
                expected_output=config['expected_output'],
                agent=self.agents[config['agent']]
            )
            tasks.append(task)
        return tasks

    def crew(self) -> Crew:
        """Create and return the configured crew."""
        return Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            verbose=True
        ) 