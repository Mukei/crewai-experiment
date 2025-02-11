# Implementation Decisions Log

## CrewAI with Ollama Integration

### 2024-01-27: Initial Setup Attempts and Issues

1. **First Attempt**: Used `langchain_community.llms import Ollama`
   - Status: Failed
   - Error: LiteLLM provider issues
   - Reason: Incompatibility between CrewAI's LiteLLM integration and Langchain's Ollama implementation

2. **Second Attempt**: Used `langchain_ollama import OllamaLLM`
   - Status: Failed
   - Error: Import issues and LiteLLM provider problems
   - Reason: Package structure changes in newer versions

3. **Third Attempt**: Used `crewai.llms import OllamaLLM`
   - Status: Failed
   - Error: ModuleNotFoundError: No module named 'crewai.llms'
   - Reason: Incorrect import path assumption

4. **Fourth Attempt**: Used direct Agent llm_config
   - Status: Failed
   - Error: OpenAI Authentication Error
   - Reason: CrewAI defaulting to OpenAI despite Ollama configuration

### Project Structure Evolution

1. **Initial Structure**: Single file approach
   - Status: Abandoned
   - Reason: Poor maintainability and lack of separation of concerns

2. **Python Module Structure**:
   - Status: Abandoned
   - Reason: Not following CrewAI's recommended practices

3. **Final Structure**: YAML-based Configuration
   - Status: Implemented
   - Components:
     - `config/agents.yaml`: Agent definitions
     - `config/tasks.yaml`: Task definitions
     - `config/llm.yaml`: Centralized LLM configuration
     - `crew.py`: Configuration loader and crew setup
     - `main.py`: Entry point
   - Rationale:
     - Better separation of configuration from code
     - Follows CrewAI's recommended practices
     - Easier to maintain and modify
     - More declarative approach

### LLM Configuration Strategy

1. **Initial Approach**: Per-agent LLM configuration
   - Status: Abandoned
   - Issues:
     - Duplicate configuration
     - Inconsistent settings
     - Harder to maintain

2. **Current Approach**: Centralized LLM Configuration
   - Status: Implemented
   - Implementation:
     ```yaml
     # config/llm.yaml
     ollama_llm:
       model: ollama/deepseek-r1
       base_url: http://localhost:11434
       temperature: 0.7
     ```
   - Benefits:
     - Single source of truth
     - Consistent settings across agents
     - Easier to maintain and update
     - Better resource utilization
     - Follows DRY principle

### Task Configuration

- Maintained context-awareness between tasks
- Research task feeds into writing task
- Clear expected outputs defined
- Proper agent assignment

### Best Practices Implemented

1. **Configuration Management**:
   - YAML for configurations
   - Separation of concerns
   - Centralized LLM settings

2. **Code Organization**:
   - Modular structure
   - Clear responsibility separation
   - Easy to extend

3. **Documentation**:
   - Inline code comments
   - Decision logging
   - Configuration documentation

### Future Considerations

1. **Scalability**:
   - Current structure supports easy addition of new agents and tasks
   - LLM configuration can be extended for different models

2. **Maintenance**:
   - YAML files make configuration updates straightforward
   - Centralized LLM configuration reduces maintenance overhead

3. **Extensibility**:
   - Structure allows for easy addition of new features
   - Can add more configuration options as needed

### Ollama Configuration Fix
- Added "ollama/" prefix to model names to explicitly identify provider
- Included dummy api_key field to satisfy LiteLLM validation
- Maintained local API base configuration
- Avoided OpenAI dependencies as per project requirements

Rationale: The original configuration didn't fully adhere to LiteLLM's Ollama requirements, causing fallback to OpenAI.

### Final Ollama Configuration
- Removed explicit provider declaration
- Relied on "ollama/" model prefix for routing
- Maintained dummy api_key as workaround
- Verified with LiteLLM 1.0.2 and CrewAI 0.28.8

Error Resolution: Prevents OpenAI fallback by eliminating provider ambiguity in LiteLLM configuration

### Implementation Plan

1. Keep essential packages in pixi.toml:
   ```toml
   [pypi-dependencies]
   crewai = "*"
   python-dotenv = "*"
   ```

2. Configure Agent with proper Ollama settings:
   - Set provider as "ollama"
   - Include base_url for local server
   - Use correct model name format

This approach ensures proper integration with local Ollama instance.

### Class-Based Architecture with YAML Configuration

1. **Architectural Approach**:
   - Status: Implemented
   - Components:
     - Standard class-based structure
     - YAML configuration files
     - Method-based agent and task definitions
   - Rationale:
     - Better compatibility with current CrewAI version
     - Maintains clean separation of concerns
     - Supports future migration to decorator-based approach

2. **Implementation Details**:
   - Components:
     - ResearchCrew class with clear method responsibilities
     - YAML-based configuration loading
     - Dynamic task creation with templates
     - Proper agent and task relationships
   - Benefits:
     - Clear code organization
     - Easy to maintain and extend
     - Configuration-driven approach
     - Strong type hints and IDE support

3. **Configuration Strategy**:
   - Retained YAML files for:
     - Agent configurations
     - Task templates
     - LLM settings
   - Enhanced with:
     - Dynamic topic injection
     - Template-based task descriptions
     - Proper context management between tasks

4. **Design Decisions**:
   - Keep configuration separate from code
   - Use clear method names for components
   - Maintain template-based approach for flexibility
   - Support dynamic topic injection
   - Preserve test coverage and maintainability

This approach provides:
- Clean separation of configuration and code
- Easy migration path to decorator-based structure
- Improved maintainability and type safety
- Better test coverage and error handling

Note: While CrewAI is moving towards a decorator-based approach, our current implementation maintains compatibility while being ready for future updates.

### CrewAI Version and Architecture Investigation

1. **Version Analysis**:
   - Current Version: CrewAI 0.100.0
   - Documentation suggests decorator-based approach with `CrewBase`
   - Implementation found in `crewai.project` module
   - Decision: Successfully implemented decorator-based approach

2. **Import Structure**:
   - `CrewBase` from `crewai.project.crew_base`
   - Decorators from `crewai.project.annotations`
   - Core components from `crewai` main package
   - Maintains clean separation of concerns

3. **Decorator Implementation**:
   - `@CrewBase` for class-level configuration
   - `@agent` for agent method definitions
   - `@task` for task method definitions
   - `@crew` for crew configuration
   - Automatic configuration loading from YAML

4. **Benefits of Current Approach**:
   - Follows CrewAI's recommended patterns
   - Better integration with CrewAI's features
   - Automatic configuration management
   - Clear component relationships
   - Strong type safety and IDE support

This investigation revealed that CrewAI's decorator-based pattern is fully supported in version 0.100.0, but requires importing from the correct module paths. Our implementation now follows the recommended approach while maintaining our configuration-driven architecture.

### Web Search and Source Traceability Implementation

1. **Enhanced Web Search Strategy**:
   - Status: Implementing
   - Components:
     - Increased number of search results (from 5 to 10)
     - Source metadata tracking
     - Result ranking and filtering
   - Rationale:
     - Better research coverage
     - More diverse perspectives
     - Enhanced credibility through source tracking

2. **Source Traceability Architecture**:
   - Status: Implementing
   - Implementation:
     ```python
     class SearchResult:
         source: str
         title: str
         snippet: str
         link: str
         relevance_score: float
     ```
   - Benefits:
     - Clear source attribution
     - Enhanced result validation
     - Better context preservation
     - Improved research quality

3. **Response Format Enhancement**:
   - Status: Implementing
   - Features:
     - Markdown-based citation system
     - Inline source references
     - Bibliography section
   - Benefits:
     - Professional presentation
     - Verifiable sources
     - Academic-style citations

4. **Agent Communication Protocol**:
   - Status: Implementing
   - Changes:
     - Enhanced context passing between agents
     - Source metadata preservation
     - Structured response format
   - Rationale:
     - Maintain source traceability
     - Improve information flow
     - Better quality control

### Implementation Approach for Multiple Sources

1. **Search Results Processing**:
   - Status: Implementing
   - Method:
     - Parallel processing of multiple sources
     - Result deduplication
     - Relevance scoring
   - Benefits:
     - Comprehensive research
     - Reduced redundancy
     - Better source quality

2. **Response Generation Strategy**:
   - Status: Implementing
   - Components:
     - Multi-source synthesis
     - Citation management
     - Fact cross-validation
   - Goals:
     - Balanced perspective
     - Accurate attribution
     - Reliable information

3. **Quality Control Measures**:
   - Status: Implementing
   - Features:
     - Source credibility scoring
     - Content freshness tracking
     - Citation verification
   - Purpose:
     - Ensure reliable sources
     - Maintain information accuracy
     - Support fact-checking

This enhancement focuses on improving research quality through better source management and traceability, while maintaining the system's ease of use and performance.

### Streamlit State Management Strategy

1. **Initial Implementation Issues**:
   - Status: Identified
   - Problems:
     - Double initialization of ResearchCrew
     - Resource cleanup inconsistency
     - Session state conflicts
   - Impact:
     - Memory leaks
     - Performance degradation
     - Unstable application state

2. **Revised Implementation**:
   - Status: In Progress
   - Components:
     - Singleton pattern for ResearchCrew
     - Proper session state initialization
     - Resource cleanup hooks
   - Benefits:
     - Single source of truth
     - Consistent application state
     - Better resource management
     - Improved performance

3. **Implementation Details**:
   ```python
   # Singleton pattern with session state
   if 'crew' not in st.session_state:
       st.session_state.crew = ResearchCrew()
   
   # Resource cleanup
   def cleanup():
       if hasattr(st.session_state, 'crew'):
           st.session_state.crew._cleanup_llm()
   
   # Register cleanup
   st.session_state.on_cleanup = cleanup
   ```

4. **Testing Strategy**:
   - Unit tests for initialization
   - Integration tests for state management
   - UI tests for component lifecycle
   - Resource cleanup verification

This approach ensures:
- Single ResearchCrew instance per session
- Proper resource management
- Consistent application state
- Better testability

### Agent Communication Strategy

1. **File-Based Communication**:
   - Status: To be implemented
   - Implementation:
     - Use JSON files for structured data
     - Use MD files for content and research
     - Temporary file management for session
   - Benefits:
     - Better state persistence
     - Crash recovery capability
     - Easier debugging
     - Clear data flow tracking

2. **File Structure**:
   ```
   temp/
   ├── research/
   │   ├── {session_id}_research.md    # Research findings
   │   └── {session_id}_sources.json   # Source metadata
   ├── writing/
   │   ├── {session_id}_draft.md      # Initial content
   │   └── {session_id}_citations.json # Citation mapping
   └── editing/
       ├── {session_id}_review.md     # Editor's review
       └── {session_id}_final.md      # Final approved content
   ```

3. **Implementation Plan**:
   - Phase 1: Topic Handling (Current)
     - Implement file-based communication
     - Add session management
     - Update agent interactions
   - Phase 2: E2E Testing
     - Add file-based test fixtures
     - Implement cleanup in tests
     - Add file content validation
   - Phase 3: Crash Handling
     - Add file-based state recovery
     - Implement cleanup on signals
     - Add session recovery
   - Phase 4: Progress Display
     - Track progress via file changes
     - Add file-based checkpoints
     - Implement progress recovery

4. **Benefits**:
   - Improved reliability through persistence
   - Better error recovery
   - Clear data flow between agents
   - Easier debugging and testing
   - State recovery after crashes

This approach will help address our current issues while improving system reliability and maintainability.

### Logging Strategy Implementation

1. **Centralized Logging Configuration**:
   - Status: Implemented
   - Components:
     - Dedicated loggers for each component
     - Consistent formatting across all logs
     - Both file and console output
   - Benefits:
     - Better debugging capabilities
     - Clear separation of concerns
     - Easier log analysis
     - Improved error tracking

2. **Logger Structure**:
   - Main Logger: General application logs
   - Crew Logger: CrewAI operations
   - File Manager Logger: File operations
   - Progress Tracker Logger: Progress updates
   - UI Logger: User interface events
   - Error Logger: Critical issues

3. **Implementation Details**:
   ```python
   # Log format
   LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
   
   # Log levels
   INFO: State changes, operations
   DEBUG: Detailed tracking
   WARNING: Recoverable issues
   ERROR: Critical problems
   CRITICAL: System failures
   ```

4. **Benefits**:
   - Clear audit trail of operations
   - Better debugging support
   - Improved error tracking
   - Performance monitoring
   - State recovery support

5. **Testing Strategy**:
   - Unit tests for logger configuration
   - Integration tests for log output
   - Format verification
   - Level-specific logging tests
   - File handling tests

This logging implementation supports our file-based communication strategy while providing comprehensive debugging and monitoring capabilities. 