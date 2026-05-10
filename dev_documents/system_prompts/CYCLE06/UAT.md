# Cycle 06: User Acceptance Testing Plan

## Test Scenarios

### Scenario ID: UAT-C06-01
**Priority:** High
**Description:** Verify the Streamlit UI correctly renders KPI metrics and charts when provided with a valid repository input, ensuring the visual presentation aligns with the backend data.

### Scenario ID: UAT-C06-02
**Priority:** High
**Description:** Verify the Streamlit UI gracefully handles non-existent repository inputs (HTTP 404) by displaying a user-friendly error message rather than a system crash or raw exception trace.

## Behavior Definitions

### UAT-C06-01: Successful Dashboard Rendering
**GIVEN** the application is running and the user inputs a valid repository (e.g., `tiangolo/fastapi`)
**WHEN** the data retrieval is complete
**THEN** the UI must display three distinct KPI metrics for Stars, Forks, and Open Issues
**AND** render a line chart representing commit activity over time
**AND** render a bar chart displaying the top 5 committers without any visual errors.

### UAT-C06-02: Graceful Exception Handling
**GIVEN** the user inputs a non-existent repository string (e.g., `invalid/repo123`)
**WHEN** the backend orchestrator raises a `RepositoryNotFoundError`
**THEN** the UI must intercept this specific error
**AND** display a clear, formatted warning message (e.g., "Repository not found. Please check the spelling.")
**AND** no raw Python stack traces or internal system paths must be visible on the browser screen.
