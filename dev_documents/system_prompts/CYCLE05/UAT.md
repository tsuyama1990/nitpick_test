# CYCLE05: Streamlit Web UI & Presentation Layer (UAT)

## Test Scenarios

### Scenario 1: UI Input Validation Guardrails
**ID**: UAT-C05-01
**Priority**: High
**Description**: Verify that the UI strictly filters out malformed repository names before passing them to the system backend, preventing useless API calls and 404 errors.

### Scenario 2: Data Visualization Rendering
**ID**: UAT-C05-02
**Priority**: High
**Description**: Prove that valid domain models and DataFrames are accurately mapped to Streamlit visual components without crashing.

## Behavior Definitions

### UAT-C05-01: UI Input Validation Guardrails
**GIVEN** the Streamlit application is running
**WHEN** a user enters `invalid_repo_name_without_slash` and submits
**THEN** the system must halt execution of the query
**AND** display a warning message indicating the required `owner/repo` format.

### UAT-C05-02: Data Visualization Rendering
**GIVEN** a pre-computed `RepositoryInfo` model containing 1000 stars and 500 forks
**WHEN** the UI rendering function is invoked
**THEN** the screen displays KPI metrics strictly matching those numbers.

**GIVEN** a valid Polars DataFrame with chronological commit counts
**WHEN** the chart rendering function is invoked
**THEN** a line chart is successfully constructed and passed to Streamlit's frontend engine.
