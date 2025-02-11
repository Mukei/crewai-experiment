# Implementation Plan

## Phase 1: Basic UI and Testing Framework
- [x] Set up Testing Infrastructure
  - [x] Add pytest to pixi.toml
  - [x] Create tests directory structure
  - [x] Set up GitHub Actions for CI
  - [x] Create test utilities and fixtures
- [x] Set up Streamlit Chat UI
  - [x] Add streamlit to pixi.toml
  - [x] Create basic chat interface using st.chat_message
  - [x] Implement message history with st.session_state
  - [x] Add user input with st.chat_input
  - [x] Style chat interface with st.markdown
  - [x] Add basic error handling
  - [x] Create UI tests
- [ ] Initial CrewAI Integration
  - [ ] Create basic topic research functionality
  - [ ] Add integration tests
  - [ ] Add UI feedback for processing (st.spinner)
  - [ ] Test error scenarios
  - [ ] Add chat history persistence

## Phase 2: Enhanced UI and Dynamic Topics
- [x] Expand Chat UI Components
  - [x] Add system message styling
  - [x] Implement markdown support for responses
  - [x] Add code block formatting
  - [x] Add loading animations
  - [x] Add error message displays
  - [x] Add clear chat button
  - [x] Add export chat history
- [ ] Enhance CrewAI Integration
  - [ ] Update agents.yaml with dynamic topic (with tests)
  - [ ] Update tasks.yaml with dynamic topic (with tests)
  - [ ] Add parameter validation (with tests)
  - [ ] Test full integration flow
  - [ ] Add conversation context management

## Phase 3: File-Based Communication and Progress Tracking
- [x] Implement File-Based Communication
  - [x] Create FileManager class
  - [x] Add session-based file management
  - [x] Implement file cleanup
  - [x] Add file recovery mechanisms
- [x] Add Progress Tracking
  - [x] Create ProgressTracker class
  - [x] Implement step tracking
  - [x] Add error logging
  - [x] Create progress recovery

## Phase 4: Research Dashboard and Session Management
- [x] Implement Research Dashboard
  - [x] Create research results display
  - [x] Add revision history view
  - [x] Implement error log display
  - [x] Add session information panel
- [x] Session Management
  - [x] Add session recovery UI
  - [x] Implement state recovery
  - [x] Add progress persistence
  - [x] Create session cleanup

## Phase 5: Logging and Error Handling
- [x] Enhanced Logging System
  - [x] Create dedicated loggers for components
  - [x] Add file and console logging
  - [x] Implement error tracking
  - [x] Add progress logging
- [x] Error Recovery
  - [x] Add LLM recreation on failure
  - [x] Implement state recovery
  - [x] Add cleanup on errors
  - [x] Create error display in UI

## Current Status and Next Steps

### Completed Features:
1. File-based communication between agents
2. Progress tracking and recovery
3. Enhanced logging system
4. Research dashboard
5. Session management and recovery
6. Error handling and recovery

### To Test:
1. Complete workflow with research, writing, and editing
2. Session recovery after crashes
3. Progress tracking accuracy
4. File management and cleanup
5. Error handling and recovery
6. Dashboard updates and display

### Known Issues to Monitor:
1. LLM connection stability
2. File cleanup after sessions
3. Progress tracking accuracy
4. UI responsiveness with large content
5. Session recovery edge cases

### Testing Strategy:
1. Start with basic research flow
2. Monitor logs for errors
3. Test session recovery
4. Verify file management
5. Check dashboard updates

## Future Enhancements (Phase 6):
- [ ] Multiple Sources and Traceability
  - [ ] Enhanced web search
  - [ ] Source validation
  - [ ] Citation management
  - [ ] Bibliography generation
- [ ] UI Improvements
  - [ ] Source display
  - [ ] Citation tooltips
  - [ ] Bibliography section
  - [ ] Advanced progress visualization

## Testing Notes
```yaml
Test Categories:
  Functional Tests:
    - Complete research workflow
    - Session recovery
    - File management
    - Progress tracking
  
  Integration Tests:
    - UI-Backend communication
    - File-Progress coordination
    - Session management
    - Dashboard updates
  
  Error Handling:
    - LLM failures
    - File system errors
    - Recovery mechanisms
    - UI error display
```

## Next Actions:
1. Run complete system test
2. Monitor logs for issues
3. Verify all components work together
4. Test recovery scenarios
5. Document any issues found

## Testing Strategy
- **Continuous Testing**:
  - Write tests before implementing features (TDD)
  - Run tests on every commit
  - Maintain minimum 80% coverage
  - Use GitHub Actions for CI

- **Test Categories**:
  ```yaml
  Unit Tests:
    - UI components
    - CrewAI integration
    - Guardrails functionality
    - Configuration handling
  
  Integration Tests:
    - Full workflow testing
    - UI-CrewAI interaction
    - Guardrails integration
    - Toggle functionality
  
  UI Tests:
    - Component rendering
    - User interactions
    - State management
    - Error handling
  ```

## Development Workflow
1. Write test for new feature
2. Implement feature
3. Verify tests pass
4. Update UI for immediate feedback
5. Document changes
6. Commit with tests

## Dependencies
```yaml
Required packages:
- streamlit
- streamlit-chat  # For enhanced chat components
- nemoguardrails
- pytest
- pytest-cov
- pytest-asyncio
- pytest-mock
```

## UI Components Structure
```yaml
Chat Interface:
  - Message Display:
    - User messages (right-aligned, user style)
    - AI responses (left-aligned, AI style)
    - System messages (centered, system style)
  - Input Area:
    - Chat input field
    - Send button
    - Clear chat button
  - Controls:
    - Guardrails toggle
    - Export chat button
  - Status:
    - Loading indicator
    - Error messages
    - System status
```

## Timeline (Adjusted for Testing)
- Phase 1: 3-4 days (includes test setup)
- Phase 2: 3-4 days
- Phase 3: 4-5 days
- Phase 4: 2-3 days
- Phase 5: 2-3 days

## Priority Order
1. Testing Infrastructure & Basic UI
2. Dynamic Topic Integration
3. Guardrails Implementation
4. Toggle Feature
5. Final Testing & Documentation

## Notes
- Tests must pass before merging any changes
- UI should be functional from Phase 1
- Regular user feedback through UI
- Continuous integration with GitHub Actions
- Regular test coverage reports 

## Phase 6: Multiple Sources and Traceability
- [ ] Enhance Web Search Tool
  - [ ] Update WebSearchTool class with new features
  - [ ] Implement SearchResult data class
  - [ ] Add result ranking and filtering
  - [ ] Implement source metadata tracking
  - [ ] Add tests for new functionality
- [ ] Improve Research Agent
  - [ ] Update research task template
  - [ ] Implement multi-source synthesis
  - [ ] Add source validation
  - [ ] Create tests for enhanced research
- [ ] Enhance Writer Agent
  - [ ] Update writing task template
  - [ ] Implement citation system
  - [ ] Add bibliography generation
  - [ ] Create tests for citation handling
- [ ] Update UI Components
  - [ ] Add source display
  - [ ] Implement citation tooltips
  - [ ] Add bibliography section
  - [ ] Create tests for new UI features

## Implementation Timeline
- Phase 6 (Multiple Sources and Traceability): 4-5 days
  - Day 1: Web Search Tool enhancements
  - Day 2: Research Agent improvements
  - Day 3: Writer Agent updates
  - Day 4: UI Component updates
  - Day 5: Testing and refinement

## Testing Strategy Update
```yaml
New Test Categories:
  Web Search Tests:
    - Result ranking accuracy
    - Source metadata handling
    - Error handling for multiple sources
    
  Agent Integration Tests:
    - Multi-source processing
    - Citation management
    - Source validation
    
  UI Component Tests:
    - Source display formatting
    - Citation tooltip functionality
    - Bibliography rendering
```

## Quality Metrics
```yaml
Source Management:
  - Minimum sources per research: 3
  - Maximum sources per research: 10
  - Source freshness: < 1 year old
  - Source diversity: At least 2 different domains

Citation Quality:
  - All facts must have citations
  - Bibliography must be complete
  - Links must be valid
  - Sources must be reputable

Performance Targets:
  - Search completion: < 5 seconds
  - Result processing: < 2 seconds
  - Response generation: < 10 seconds
```