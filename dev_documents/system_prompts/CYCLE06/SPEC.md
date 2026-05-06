# CYCLE06: E2E Testing, Final Assembly & Refinement

## Summary

Cycle 06 is the culmination of the project. It involves creating the Service Layer (Controller) to orchestrate the flow between the UI, Storage, Transformation, and Ingestion layers. We will wire up the main Streamlit application script to invoke this controller. Finally, we will write end-to-end (E2E) tests simulating the entire application lifecycle, including critical scenarios for error propagation (e.g., exposing rate-limit errors safely to the UI) and executing the Marimo interactive tutorials for final UAT validation.

## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
- Maintained from Cycle 01.

### B. System Configurations (`docker-compose.yml`)
- Maintained from Cycle 01.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
- **Mandate Mocking:** E2E testing must utilize the `pytest-httpx` library to securely mock all network requests. Ensure that the E2E test runs NEVER hit the live GitHub API without the explicit `@pytest.mark.live` marker.

## System Architecture

The following directories and files must be implemented or modified:

.
├── src/
│   ├── presentation/
│   │   └── **app.py**
│   └── services/
│       ├── **__init__.py**
│       └── **dashboard_controller.py**
└── tests/
    ├── e2e/
    │   ├── **__init__.py**
    │   └── **test_dashboard_e2e.py**
    └── uat/
        └── **UAT_AND_TUTORIAL.py** (Marimo Notebook)

## Design Architecture

**DashboardController (`src/services/dashboard_controller.py`)**
- Orchestrates the data flow.
- Methods:
  - `get_dashboard_data(owner: str, repo: str) -> tuple[RepositoryInfo, pl.DataFrame, pl.DataFrame]`: The master function.
- Flow:
  1. Generate cache keys based on `owner` and `repo`.
  2. Attempt to load `RepositoryInfo` and the DataFrames from `CacheManager`.
  3. On cache miss:
     a. Call `GitHubClient` to fetch raw info and commits.
     b. Call `PolarsProcessor` to aggregate the commits into `commits_by_date_df` and `top_committers_df`.
     c. Save all three to `CacheManager`.
  4. Return the tuple to the UI.
- Error Handling: It must catch the custom `RateLimitError` and `NotFoundError` from the Ingestion layer and propagate them cleanly to the UI layer so the UI can render `st.error()` without leaking system state.

## Implementation Approach

1. **Init File**: Ensure `src/services/__init__.py` and `tests/e2e/__init__.py` exist.
2. **Implement Controller**: Create `src/services/dashboard_controller.py`. Import the Client, Cache Manager, and Processor. Wire the logic together as defined in the flow.
3. **Wire UI**: Update `src/presentation/app.py` to import `get_dashboard_data`. When the user submits the form, call the controller. Wrap the call in a `try...except` block catching the specific custom errors and displaying `st.error("...")` or `st.warning("...")`. On success, pass the returned tuple to the components created in Cycle 05.
4. **Marimo Notebook**: Create `tests/uat/UAT_AND_TUTORIAL.py`. Implement the interactive tutorial logic referencing the scenarios defined in `USER_TEST_SCENARIO.md`.

## Test Strategy

**Unit Testing Approach (Min 300 words)**
We will test the `DashboardController` state machine. Using `unittest.mock.patch`, we will mock the `CacheManager`, `GitHubClient`, and `PolarsProcessor`. The primary test will assert the Cache-Hit path: we mock `CacheManager.load_from_cache` to return valid data. We then assert that the Controller returns this data immediately and strictly verify that `GitHubClient.fetch...` was NEVER called, proving the system efficiently respects the rate-limit protections. Conversely, we will test the Cache-Miss path by mocking `load_from_cache` to return `None`, asserting that the Controller subsequently calls the API client, processes the data, and successfully calls `save_to_cache` before returning the tuple.

**Integration Testing Approach (Min 300 words)**
The End-to-End (E2E) testing strategy involves executing the fully assembled system logic from the controller down to the network boundary, bypassing only the Streamlit rendering engine. Using `pytest-httpx`, we will mock a full, multi-request GitHub API interaction (one endpoint for the repo info, another for the commits list). We will invoke `get_dashboard_data("testowner", "testrepo")` and assert that the entire pipeline executes flawlessly, returning the final aggregated Polars DataFrames and Pydantic models. We will also execute a negative E2E test, mocking a 403 Forbidden response from the API, and asserting that the Controller cleanly catches this, raising our safe `RateLimitError` without crashing due to JSON or type errors. Finally, we will configure the Marimo notebook for interactive, live User Acceptance Testing.
