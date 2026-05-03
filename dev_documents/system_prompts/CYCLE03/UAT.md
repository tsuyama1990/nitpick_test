# CYCLE 03 UAT: Web UI Visualization

## Test Scenarios

### Scenario ID: C03-01 - Complete Dashboard Rendering (E2E)
*   **Priority**: Critical
*   **Description**: Verify that the final Streamlit web application successfully and flawlessly integrates all underlying architectural layers, accepts raw user input safely, and correctly renders the aggregated KPIs and complex charts without any runtime errors.
*   **Execution Strategy**: The interactive Marimo notebook will seamlessly guide the user to explicitly launch the Streamlit app locally on their machine. The human user will manually input a known repository like `streamlit/streamlit`. They will critically visually confirm the undeniable presence of exactly three prominent KPIs (Total Stars, Total Forks, Open Issues), an interactive line chart definitively showing chronological commit trends over time, and a clear bar chart definitively ranking the top committers.

### Scenario ID: C03-02 - UI Error Safety and Graceful Degradation
*   **Priority**: High
*   **Description**: Ensure that when the deeply underlying backend systems fail (e.g., due to catastrophic API errors or strict rate limits), the Streamlit UI degrades highly gracefully. It must mathematically display a user-friendly, safe error message absolutely without exposing raw HTTP errors, Python stack traces, or any secure tokens.
*   **Execution Strategy**:
    1.  The human user deliberately enters a completely non-existent repo string (`invalid-owner/repo12345`). The UI must display a highly clean, safe warning banner ("Repository not found").
    2.  The `.env` secret token is intentionally broken or deleted by the developer. The user attempts a standard search. The UI must display a highly clean, safe error banner ("Authentication failed") and absolutely no trace of the invalid token string or the raw Python stack trace must appear on the rendered screen or the terminal logs.

## Behavior Definitions

**Given** the complete Streamlit application is currently running and a mathematically valid target repository string is submitted by the human user,
**When** the central orchestrating controller successfully processes all the underlying data through the API and Polars transformer,
**Then** the UI must safely and accurately render the `st.metric` UI components and the interactive Streamlit native charts representing the fully transformed Polars DataFrames without any exceptions.

**Given** an underlying backend API network call results in a severe HTTP 403 Forbidden error due to an intentionally invalid access token,
**When** the central controller securely catches the resulting custom domain exception,
**Then** the Streamlit UI must immediately render an `st.error` red alert box containing a completely safe message, and the specific application execution must halt completely for that specific user request without terminating the underlying Streamlit server process.
