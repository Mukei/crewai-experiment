"""Main entry point for the CrewAI experiment."""
from crew import ResearchCrew

def main():
    """Run the CrewAI experiment."""
    # Initialize and run the crew
    crew = ResearchCrew().crew()
    result = crew.kickoff()

    # Display the final output
    print("\nFinal Result:")
    print(result)

if __name__ == "__main__":
    main() 