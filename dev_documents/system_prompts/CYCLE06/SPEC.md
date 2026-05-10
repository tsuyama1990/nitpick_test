# Cycle 06: Streamlit Visualisation and UI Specification

## Summary
This final cycle brings the Proof-of-Concept to life by constructing the user interface using Streamlit. The objective is to build a thin, intuitive presentation layer that interacts exclusively with the `GitHubAnalyticsService` (Orchestrator) built in Cycle 05. The UI must handle user inputs, specifically capturing the target repository name, and trigger the backend data retrieval process. Upon receiving the processed data, it must render the Key Performance Indicators (KPIs) and the aggregated Polars DataFrames into interactive charts. Crucially, the UI must also implement graceful error handling, intercepting domain exceptions (like 404 Not Found or Rate Limit errors) and presenting them as user-friendly warnings rather than allowing the application to crash or leak Python stack traces to the user interface.

## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
This cycle requires the `GITHUB_TOKEN` to be active in the local `.env` file so the underlying orchestrator can function during manual UI testing. No new secrets are required.

### B. System Configurations (`docker-compose.yml`)
The Streamlit application will run directly on the host OS. A typical `streamlit run src/app.py` command will be used. Ensure the application binds to the default port `8501`.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
**MANDATORY INSTRUCTION:** Testing a Streamlit application programmatically can be fragile.
- While Streamlit's `AppTest` framework exists, it frequently struggles with mocking complex asynchronous or multithreaded backend services like `httpx`.
- You **MUST** instruct the Coder to prioritize testing the Streamlit UI logic using a User Acceptance Testing (UAT) approach executed via a Marimo notebook (`tests/uat/UAT_AND_TUTORIAL.py`). This notebook will programmatically invoke the service layer and verify the data structures *before* they are passed to the Streamlit rendering functions, serving as an executable specification of the UI's data requirements.
- If `AppTest` is used for basic component rendering verification, `unittest.mock.patch` may fail to intercept module-level imports due to Streamlit's dynamic background thread execution. You MUST rely on fixtures like `pytest-httpx`'s `HTTPXMock` to intercept the underlying network calls directly, ensuring that UI tests are strictly prevented from executing real network calls against the live API.

## System Architecture
The file structure adds the main Streamlit application entry point and the Marimo UAT notebook. The files explicitly marked in bold represent the targets for creation during this cycle.

```text
.
├── src/
│   ├── config.py
│   ├── domain/
│   ├── ingestion/
│   ├── processing/
│   └── **app.py**
└── tests/
    └── uat/
        └── **UAT_AND_TUTORIAL.py**
```

## Design Architecture
The design for the Visualisation Layer is centralized entirely within `src/app.py`. This script is executed top-to-bottom by the Streamlit server on every user interaction.

The script must begin by setting the page configuration using `st.set_page_config(page_title="GitHub Analytics PoC", layout="wide")`. Following this, it must initialize the core dependencies (the config, client, cache, and service). To prevent Streamlit from re-initializing these expensive objects on every render, the dependency initialization must be wrapped in a function decorated with `@st.cache_resource`.

The UI layout should consist of:
1.  **Header:** A simple title (e.g., `st.title("GitHub Repository Analytics")`).
2.  **Input Mechanism:** A text input field (`st.text_input`) prompting the user for the repository format `owner/repo`.
3.  **Action Trigger:** A button (`st.button("Analyze")`) or relying on the text input's `on_change` event to initiate processing.
4.  **Error Handling Boundary:** A `try...except` block surrounding the call to `service.get_dashboard_data()`. This block must catch `RepositoryNotFoundError` and output `st.error("Repository not found.")`, and catch `RateLimitExceededError` outputting `st.warning("API Rate Limit Exceeded. Try again later.")`. A generic `Exception` catch should output a safe, obfuscated error message to avoid stack trace leakage.
5.  **Data Rendering (Success Path):**
    - Retrieve the dictionary from the service.
    - Render the KPIs using `st.columns(3)` and `st.metric()` to display the Stars, Forks, and Open Issues from the `RepositoryMetrics` model.
    - Render the Date Aggregation using `st.line_chart(data=df_commits_by_date, x="date", y="commit_count")`.
    - Render the Committer Aggregation using `st.bar_chart(data=df_top_committers, x="name", y="commit_count")`.

The `tests/uat/UAT_AND_TUTORIAL.py` Marimo notebook must be designed as an interactive executable specification. It will contain Markdown cells explaining the architecture, followed by Python cells that instantiate the Service Layer, pass in mock data (or use the cache), and programmatically assert that the output dictionaries match exactly what `src/app.py` expects to render.

## Implementation Approach
1. **Implement Streamlit App:** Create `src/app.py`. Import `streamlit as st`, the domain exceptions, and the `GitHubAnalyticsService`.
2. **Resource Caching:** Define a function `get_service() -> GitHubAnalyticsService` decorated with `@st.cache_resource`. Inside, instantiate `Settings()`, `GitHubClient()`, `LocalCache()`, and `GitHubAnalyticsService()`, returning the service instance.
3. **Build UI Layout:** Implement the `st.title` and `st.text_input`. Add basic regex validation to ensure the input roughly matches `owner/repo` before proceeding.
4. **Implement Data Fetch and Render:** Inside an `if st.button("Analyze"):` block, use a `with st.spinner("Fetching data..."):` context.
5. **Implement Error Handling:** Wrap the `service.get_dashboard_data()` call in the `try...except` block as defined in the architecture, mapping exceptions to `st.error` or `st.warning`.
6. **Implement Charting:** Extract the metrics and DataFrames from the returned dictionary and use `st.metric`, `st.line_chart`, and `st.bar_chart` to display the information to the user.

## Test Strategy

### Unit / UAT Testing Approach
- **Streamlit Component Testing (Optional but Recommended):** Use `streamlit.testing.v1.AppTest.from_file("src/app.py")`. Use `httpx_mock` to mock the API responses underneath the service layer. Run the app (`at.run()`), simulate inputting text, and assert that `at.error` is empty and `at.line_chart` exists.
- **Marimo UAT Development (Mandatory):** Create `tests/uat/UAT_AND_TUTORIAL.py`. Implement cells that document the scenarios defined in `USER_TEST_SCENARIO.md`. Create a cell that acts as a "Mock Mode" pipeline, simulating the exact inputs `app.py` receives, executing the underlying service functions using mock data, and asserting the output shapes and values using standard Python `assert` statements. This ensures the application logic is verifiable without requiring a browser or the Streamlit server to be running.
