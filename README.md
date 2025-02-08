# CrewAI Experiment

[![CI](https://github.com/username/crewai-experiment/actions/workflows/ci.yml/badge.svg)](https://github.com/username/crewai-experiment/actions/workflows/ci.yml)

A research assistant powered by CrewAI with Streamlit UI and NeMo Guardrails.

## Features
- Chat-based interface for research queries
- AI-powered research and summarization
- Content safety with NeMo Guardrails
- Configurable guardrails settings

## Development
1. Install dependencies:
```bash
pixi install
```

2. Run tests:
```bash
pixi run test
```

3. Generate coverage report:
```bash
pixi run coverage-report
```
The coverage report will be available in the `coverage/` directory.

4. Start the UI:
```bash
pixi run ui
```

## Testing
- Unit tests with pytest
- Integration tests for UI and CrewAI
- Local HTML coverage reports
- Continuous Integration with GitHub Actions

## Coverage Reports
After running tests with coverage, you can:
1. Find HTML reports in the `coverage/` directory
2. View line-by-line coverage information
3. See branch coverage details
4. Track uncovered code paths
