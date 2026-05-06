# CYCLE06: E2E Testing, Final Assembly & Refinement (UAT)

## Test Scenarios

### Scenario 1: E2E Happy Path Integration
**ID**: UAT-C06-01
**Priority**: High
**Description**: Verify that the fully assembled application can fetch, transform, cache, and return data cohesively without breaking boundaries.

### Scenario 2: Error Propagation and UI Cleanliness
**ID**: UAT-C06-02
**Priority**: High
**Description**: Prove that deep system errors (like network timeouts or rate limits) are securely caught by the controller and safely translated into user-friendly UI warnings, completely preventing stack-trace leaks.

## Behavior Definitions

### UAT-C06-01: E2E Happy Path Integration
**GIVEN** an empty local cache and a simulated GitHub API returning 100 commits
**WHEN** the controller's `get_dashboard_data` method is invoked for `owner/repo`
**THEN** the system fetches data from the simulated API
**AND** processes it into two Polars DataFrames
**AND** saves the result to the local cache disk
**AND** returns the fully formatted tuple to the caller.

### UAT-C06-02: Error Propagation and UI Cleanliness
**GIVEN** the system is fully assembled
**WHEN** the backend API client encounters an HTTP 403 Rate Limit Error
**THEN** the controller intercepts the API exception
**AND** the application UI layer catches the controller's safe exception
**AND** renders a clean Streamlit warning box ("Rate limit exceeded. Please check your token or wait.")
**AND** the application logs show no trace of the underlying HTTP request headers or the raw `GITHUB_TOKEN`.
