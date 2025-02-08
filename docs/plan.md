# Implementation Plan

## Phase 1: Basic UI and Testing Framework
- [x] Set up Testing Infrastructure
  - [x] Add pytest to pixi.toml
  - [x] Create tests directory structure
  - [x] Set up GitHub Actions for CI
  - [x] Create test utilities and fixtures
- [ ] Set up Streamlit Chat UI
  - [x] Add streamlit to pixi.toml
  - [ ] Create basic chat interface using st.chat_message
  - [ ] Implement message history with st.session_state
  - [ ] Add user input with st.chat_input
  - [ ] Style chat interface with st.markdown
  - [ ] Add basic error handling
  - [ ] Create UI tests
- [ ] Initial CrewAI Integration
  - [ ] Create basic topic research functionality
  - [ ] Add integration tests
  - [ ] Add UI feedback for processing (st.spinner)
  - [ ] Test error scenarios
  - [ ] Add chat history persistence

## Phase 2: Enhanced UI and Dynamic Topics
- [ ] Expand Chat UI Components
  - [ ] Add system message styling
  - [ ] Implement markdown support for responses
  - [ ] Add code block formatting
  - [ ] Add loading animations
  - [ ] Add error message displays
  - [ ] Add clear chat button
  - [ ] Add export chat history
- [ ] Enhance CrewAI Integration
  - [ ] Update agents.yaml with dynamic topic (with tests)
  - [ ] Update tasks.yaml with dynamic topic (with tests)
  - [ ] Add parameter validation (with tests)
  - [ ] Test full integration flow
  - [ ] Add conversation context management

## Phase 3: NVIDIA NeMo Guardrails Integration
- [ ] Setup NeMo Guardrails
  - [ ] Add nemoguardrails to pixi.toml
  - [ ] Create guardrails configuration
  - [ ] Add guardrails tests
  - [ ] Test configuration loading
- [ ] Implement Core Guardrails
  - [ ] Create topic validation (with tests)
  - [ ] Add content filtering (with tests)
  - [ ] Add output sanitization (with tests)
  - [ ] Test guardrails integration

## Phase 4: UI Guardrails Toggle and Testing
- [ ] Implement Toggle Feature
  - [ ] Add toggle UI component (with tests)
  - [ ] Create state management (with tests)
  - [ ] Add visual indicators (with tests)
  - [ ] Test toggle functionality
- [ ] Enhance Guardrails Integration
  - [ ] Create guardrails wrapper (with tests)
  - [ ] Add conditional execution (with tests)
  - [ ] Test full toggle flow
  - [ ] Add integration tests

## Phase 5: Documentation and Final Testing
- [ ] Complete Documentation
  - [ ] Update decision.md
  - [ ] Create user guide
  - [ ] Document test coverage
  - [ ] Add setup instructions
- [ ] Final Testing
  - [ ] Run full test suite
  - [ ] Performance testing
  - [ ] User acceptance testing
  - [ ] Document test results

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

## Timeline (Updated)
- Phase 1: 2-3 days (Testing infrastructure completed, UI in progress)
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

## Current Status
- Testing Infrastructure: ✅ Completed
- GitHub CI Setup: ✅ Completed
- Streamlit UI: 🚧 In Progress
- CrewAI Integration: 📅 Planned
- Guardrails: 📅 Planned

## Notes
- Tests must pass before merging any changes
- UI should be functional from Phase 1
- Regular user feedback through UI
- Continuous integration with GitHub Actions
- Regular test coverage reports 