# Cycle 05: Orchestration and Service Layer Specification

## Summary
This cycle is the linchpin of the application architecture. The objective is to design and implement the Service Layer (Orchestrator) that binds together the disparate components built in Cycles 01 through 04. This layer serves as the single point of contact for the frontend interface. It is responsible for receiving a repository request, determining if valid data exists within the local cache (Cycle 04), routing cache misses to the GitHub API client (Cycle 02), validating the raw API response using Pydantic (Cycle 01), delegating the complex calculations to the Polars transformation module (Cycle 03), and finally updating the cache with the fresh results. By centralizing this workflow, the architecture enforces a strict separation of concerns, ensuring the UI remains ignorant of API rate limits, caching mechanisms, and data structure transformations.

## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
The orchestrator relies on the underlying `GitHubClient` and `config.py` which manage the `GITHUB_TOKEN`. No new secrets are required.

### B. System Configurations (`docker-compose.yml`)
No specific configurations are required.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
**MANDATORY INSTRUCTION:** This cycle integrates the network client and the file system cache. Integration tests here run the highest risk of polluting the sandbox or causing external API failures.
- You **MUST** instruct the Coder to use `pytest-httpx` to mock the GitHub API responses when testing the Orchestrator's cache-miss scenario.
- You **MUST** instruct the Coder to use Pytest's `tmp_path` fixture and patch the `LocalCache` initialization to use this temporary directory during tests to prevent file system pollution.
- To verify cache efficiency, tests must strictly assert the number of executed HTTP requests using `len(httpx_mock.get_requests())`. A successful cache hit test must result in exactly `0` network requests.

## System Architecture
The file structure introduces the orchestrator module into the processing package. The files explicitly marked in bold represent the targets for creation during this cycle.

```text
.
├── src/
│   ├── config.py
│   ├── domain/
│   │   ├── exceptions.py
│   │   └── schemas.py
│   ├── ingestion/
│   │   └── github_client.py
│   └── processing/
│       ├── cache.py
│       ├── transformations.py
│       └── **orchestrator.py**
└── tests/
    └── **test_orchestrator.py**
```

## Design Architecture
The design revolves around the `GitHubAnalyticsService` class defined in `src/processing/orchestrator.py`. This class acts as a Facade pattern over the complex internal subsystems.

The initialization of the service requires dependency injection of the `GitHubClient` and the `LocalCache` instances. This design ensures that the service is highly testable, as mock instances of the client or cache can be injected easily during testing.

The service exposes a primary method: `get_dashboard_data(self, owner: str, repo: str) -> dict`. This method returns a dictionary containing the fully prepared data needed by the Streamlit frontend. The structure of the return dictionary should be:
```python
{
    "metrics": RepositoryMetrics, # Pydantic model
    "commits_by_date": pl.DataFrame,
    "top_committers": pl.DataFrame
}
```

The internal workflow of `get_dashboard_data` strictly dictates the following logical sequence:
1.  **Cache Key Generation:** Generate deterministic cache keys based on the repository owner and name (e.g., `f"{owner}_{repo}_metrics"`, `f"{owner}_{repo}_commits"`).
2.  **Cache Interception:** Check the `LocalCache` for valid Polars DataFrames matching the commit data keys. For the metrics (which are small and fit in Pydantic models), either rely on the API client's inherent caching (if implemented) or implement a lightweight dict cache within the service, but the primary focus is caching the heavy Polars DataFrames.
3.  **API Ingestion (On Cache Miss):** If the cache returns `None`, use the injected `GitHubClient` to fetch the raw metrics and recent commits. The service must catch any domain exceptions (`RepositoryNotFoundError`, `RateLimitExceededError`) raised here and allow them to propagate up to the caller (the UI) without intercepting them, as the UI is responsible for displaying the error.
4.  **Data Transformation (On Cache Miss):** Pass the raw commit list to `aggregate_commits_by_date` and `get_top_committers` from the transformations module.
5.  **Cache Update (On Cache Miss):** Save the newly calculated `pl.DataFrame` objects back into the `LocalCache` using the generated keys.
6.  **Data Assembly:** Construct and return the final dictionary containing the metrics and DataFrames.

## Implementation Approach
1. **Implement Service Class:** Create `src/processing/orchestrator.py`. Import necessary components from `src.ingestion`, `src.processing.cache`, `src.processing.transformations`, and `src.domain.schemas`.
2. **Initialization:** Define `class GitHubAnalyticsService`. Implement `__init__(self, client: GitHubClient, cache: LocalCache)`.
3. **Implement Workflow Method:** Define `get_dashboard_data`. Implement the cache check, API call, transformation, and cache save logic sequentially as defined in the Design Architecture. Ensure `RepositoryMetrics` is instantiated with the raw metrics dictionary to validate it before returning.

## Test Strategy

### Unit / Integration Testing Approach
Testing the Orchestrator involves verifying the interaction between the mocked subsystems. The tests reside in `tests/test_orchestrator.py`.
- **Cache Miss Scenario (Cold Start):**
  - Inject a real `LocalCache` instance backed by `tmp_path` and a real `GitHubClient` instance.
  - Mock the network using `httpx_mock.add_response` for both the metrics and commits endpoints, returning valid static JSON data.
  - Call `get_dashboard_data("owner", "repo")`.
  - Assert that the return dictionary contains the correct `RepositoryMetrics` and `pl.DataFrame` objects.
  - **Crucial Assertion:** Assert `len(httpx_mock.get_requests()) == 2` (one for metrics, one for commits) to prove the network was accessed.
- **Cache Hit Scenario (Warm Start):**
  - Immediately following the Cache Miss test, call `get_dashboard_data("owner", "repo")` a second time with identical arguments.
  - **Crucial Assertion:** Assert that the returned data is identical to the first run.
  - **Crucial Assertion:** Assert `len(httpx_mock.get_requests()) == 2` (meaning no *new* network requests were made during the second call), proving the cache successfully intercepted the execution flow.
- **Error Propagation:**
  - Mock the network to return a 404 for the metrics endpoint.
  - Call `get_dashboard_data("invalid", "repo")`.
  - Assert that `pytest.raises(RepositoryNotFoundError)` is triggered, verifying the service does not swallow critical domain exceptions.
