# CYCLE 03 UAT: Web UI Visualization

## Test Scenarios

### Scenario ID: C03-01 - Complete Dashboard Rendering (E2E)
*   **Priority**: Critical
*   **Description**: Verify that the Streamlit application successfully integrates all underlying layers, accepts user input, and correctly renders the KPIs and charts without errors.
*   **Execution Strategy**: The Marimo notebook will guide the user to launch the Streamlit app locally. The user will input `streamlit/streamlit`. They will visually confirm the presence of three KPIs (Stars, Forks, Issues), a line chart showing commit trends, and a bar chart showing top committers.

### Scenario ID: C03-02 - UI Error Safety and Graceful Degradation
*   **Priority**: High
*   **Description**: Ensure that when underlying systems fail (e.g., API errors, rate limits), the UI degrades gracefully, displaying a user-friendly message without exposing raw errors, stack traces, or secrets.
*   **Execution Strategy**:
    1.  The user enters a non-existent repo (`invalid/repo123`). The UI must display a clean warning ("Repository not found").
    2.  The `.env` token is intentionally broken. The user attempts a search. The UI must display a clean error ("Authentication failed") and absolutely no trace of the invalid token or Python stack trace must appear on the screen.

## Behavior Definitions

**Given** the application is running and a valid target repository is submitted,
**When** the controller successfully processes the data,
**Then** the UI must render the `st.metric` components and Streamlit native charts representing the transformed Polars DataFrames.

**Given** an underlying API call results in a 403 Forbidden error due to an invalid token,
**When** the controller catches the domain exception,
**Then** the Streamlit UI must render an `st.error` box with a safe message, and the application execution must halt for that specific request without terminating the server.
# CYCLE 03 UAT: Web UI Visualization

## Test Scenarios

### Scenario ID: C03-01 - Complete Dashboard Rendering (E2E)
*   **Priority**: Critical
*   **Description**: Verify that the Streamlit application successfully integrates all underlying layers, accepts user input, and correctly renders the KPIs and charts without errors.
*   **Execution Strategy**: The Marimo notebook will guide the user to launch the Streamlit app locally. The user will input `streamlit/streamlit`. They will visually confirm the presence of three KPIs (Stars, Forks, Issues), a line chart showing commit trends, and a bar chart showing top committers.

### Scenario ID: C03-02 - UI Error Safety and Graceful Degradation
*   **Priority**: High
*   **Description**: Ensure that when underlying systems fail (e.g., API errors, rate limits), the UI degrades gracefully, displaying a user-friendly message without exposing raw errors, stack traces, or secrets.
*   **Execution Strategy**:
    1.  The user enters a non-existent repo (`invalid/repo123`). The UI must display a clean warning ("Repository not found").
    2.  The `.env` token is intentionally broken. The user attempts a search. The UI must display a clean error ("Authentication failed") and absolutely no trace of the invalid token or Python stack trace must appear on the screen.

## Behavior Definitions

**Given** the application is running and a valid target repository is submitted,
**When** the controller successfully processes the data,
**Then** the UI must render the `st.metric` components and Streamlit native charts representing the transformed Polars DataFrames.

**Given** an underlying API call results in a 403 Forbidden error due to an invalid token,
**When** the controller catches the domain exception,
**Then** the Streamlit UI must render an `st.error` box with a safe message, and the application execution must halt for that specific request without terminating the server.
# CYCLE 03 UAT: Web UI Visualization

## Test Scenarios

### Scenario ID: C03-01 - Complete Dashboard Rendering (E2E)
*   **Priority**: Critical
*   **Description**: Verify that the Streamlit application successfully integrates all underlying layers, accepts user input, and correctly renders the KPIs and charts without errors.
*   **Execution Strategy**: The Marimo notebook will guide the user to launch the Streamlit app locally. The user will input `streamlit/streamlit`. They will visually confirm the presence of three KPIs (Stars, Forks, Issues), a line chart showing commit trends, and a bar chart showing top committers.

### Scenario ID: C03-02 - UI Error Safety and Graceful Degradation
*   **Priority**: High
*   **Description**: Ensure that when underlying systems fail (e.g., API errors, rate limits), the UI degrades gracefully, displaying a user-friendly message without exposing raw errors, stack traces, or secrets.
*   **Execution Strategy**:
    1.  The user enters a non-existent repo (`invalid/repo123`). The UI must display a clean warning ("Repository not found").
    2.  The `.env` token is intentionally broken. The user attempts a search. The UI must display a clean error ("Authentication failed") and absolutely no trace of the invalid token or Python stack trace must appear on the screen.

## Behavior Definitions

**Given** the application is running and a valid target repository is submitted,
**When** the controller successfully processes the data,
**Then** the UI must render the `st.metric` components and Streamlit native charts representing the transformed Polars DataFrames.

**Given** an underlying API call results in a 403 Forbidden error due to an invalid token,
**When** the controller catches the domain exception,
**Then** the Streamlit UI must render an `st.error` box with a safe message, and the application execution must halt for that specific request without terminating the server.
