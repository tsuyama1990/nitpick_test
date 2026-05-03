# User Test Scenarios & Tutorial Plan: GitHub Analytics Dashboard PoC

This document serves as the master plan for User Acceptance Testing (UAT) and the primary tutorial for verifying the capabilities of the GitHub Repository Analysis Dashboard Proof of Concept (PoC). It outlines the strategy for executing tests, validating requirements, and ensuring a seamless user experience.

## Tutorial Strategy

The overarching strategy is to provide a single, interactive, and executable environment where users and reviewers can validate all requirements detailed in `ALL_SPEC.md` without needing to manually run disparate Python scripts or deeply understand the test suite.

We will achieve this by utilizing **Marimo**, a reactive Python notebook framework. This approach offers several advantages:
1.  **Reproducibility**: The notebook strictly defines the execution environment and sequence.
2.  **Interactivity**: Users can tweak parameters (like the target repository name) and immediately see the data flow through the ingestion and transformation layers.
3.  **Documentation combined with Code**: The tutorial text is interspersed with the actual executable code, making the system architecture tangible.

### Execution Modes
The tutorial must support two execution modes to ensure resilience and ease of testing, particularly in CI environments:

*   **Real Mode (Live API)**: Requires a valid GitHub Personal Access Token in the `.env` file. This mode executes the full End-to-End (E2E) flow, hitting the live GitHub REST API, validating network handling, rate limiting protection, and real-world data parsing.
*   **Mock Mode (CI / No-API-Key)**: If no token is provided, the tutorial must not crash. Instead, it should gracefully fall back to using static, pre-defined mock JSON data representing the GitHub API response. This allows the core logic (Polars transformation, Pydantic validation) to be verified in sandboxed environments without external dependencies.

## Tutorial Plan

To ensure simplicity and maintainability, **a SINGLE Marimo file** will be created to house all scenarios.

**File Location:** `tutorials/UAT_AND_TUTORIAL.py`

This single file will be structured sequentially to guide the user through the system's capabilities, mapping directly to the development cycles:

### Section 1: Cycle 01 - Ingestion & Validation
*   **Action**: Attempt to load configuration. Determine if operating in 'Real Mode' or 'Mock Mode'.
*   **Action**: Instantiate the API client (or mock client).
*   **Validation**: Fetch repository metadata and the latest 100 commits for a target repository (e.g., `streamlit/streamlit`).
*   **Display**: Show the raw Pydantic domain models to prove data structure adherence and type safety.
*   **Error Test**: Deliberately query a non-existent repository (`invalid/repo123`) to demonstrate graceful custom exception handling (404 Not Found) without exposing stack traces.

### Section 2: Cycle 02 - Transformation & Caching Engine
*   **Action**: Pass the `CommitRecord` objects obtained in Section 1 into the Polars Transformation engine.
*   **Validation**: Display the resulting DataFrames:
    *   Table showing Daily Commit Counts.
    *   Table showing Top 5 Committers.
*   **Caching Test**: Execute a timing test. Fetch the data again using the main application controller. The notebook must demonstrate that the second fetch is significantly faster (cache hit) and bypassing the external network.

### Section 3: Cycle 03 - UI Pre-flight Check
*   *Note: While the notebook cannot run the Streamlit UI directly, it validates the data payload prepared for it.*
*   **Action**: Invoke the central Application Controller.
*   **Validation**: Display the final `DashboardData` DTO, proving that the presentation layer will receive cleanly formatted KPIs and DataFrames ready for direct rendering via `st.line_chart` and `st.bar_chart`.

## Tutorial Validation

The ultimate validation of this system requires running the Streamlit application alongside the Marimo tutorial.

1.  **Marimo Validation**: Execute `uv run marimo edit tutorials/UAT_AND_TUTORIAL.py`. Step through all cells. Ensure no unhandled exceptions occur and the output clearly demonstrates the system's capabilities in either Real or Mock mode.
2.  **Streamlit E2E Validation**: Execute `uv run streamlit run src/presentation/app.py`.
    *   Input a valid repository and visually confirm the KPIs and charts render correctly based on live data.
    *   Input an invalid repository and visually confirm a user-friendly error message is displayed (e.g., "Repository not found") without crashing the application.
    *   *Security Audit*: Confirm that during both success and failure scenarios, no sensitive tokens from the `.env` file are ever printed to the terminal console or exposed in the UI.
