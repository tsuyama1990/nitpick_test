# Cycle 02: GitHub API Client Integration Specification

## Summary
This cycle is dedicated to constructing the Ingestion Layer. The objective is to build a robust, asynchronous-capable HTTP client that interacts directly with the live GitHub REST API. This client will utilize the configuration and domain schemas established in Cycle 01. The core mandate for this cycle is resilient network communication. The client must be capable of correctly injecting authentication tokens to maximize rate limits, handling pagination (or explicitly limiting the scope to 100 commits as per requirements), and translating raw HTTP status codes into the semantic domain exceptions defined previously. This cycle bridges the gap between the application's internal logic and the external data source, providing a clean, strictly-typed interface for downstream data transformation modules.

## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
This cycle actively utilizes the `GITHUB_TOKEN` defined in the previous cycle. No new secrets are introduced. Ensure the Coder uses the `get_settings()` singleton to access this token when initializing the HTTP client.

### B. System Configurations (`docker-compose.yml`)
No specific docker configurations are required for this cycle.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
**MANDATORY INSTRUCTION:** This cycle introduces real network requests using `httpx`. It is absolutely critical that the test suite does not execute these requests against the live GitHub API during automated test runs.
- **Mandate Mocking:** You MUST explicitly instruct the Coder to use the `pytest-httpx` library to intercept and mock all outbound HTTP requests made by the `GitHubClient`.
- The tests must configure `httpx_mock` to return mock JSON payloads or specific HTTP status codes (like 403 or 404) to verify error handling logic.
- Live API tests are strictly forbidden unless explicitly marked and excluded from the default test suite execution. Failure to mock will result in CI pipeline failures due to rate limiting and missing API keys in the Sandbox environment.

## System Architecture
The file structure for this cycle introduces the ingestion package. The files explicitly marked in bold represent the targets for creation during this cycle.

```text
.
├── src/
│   ├── config.py
│   ├── domain/
│   │   ├── exceptions.py
│   │   └── schemas.py
│   └── ingestion/
│       ├── __init__.py
│       └── **github_client.py**
└── tests/
    ├── conftest.py
    └── **test_ingestion.py**
```

## Design Architecture
The design for the Ingestion Layer centers around the `GitHubClient` class within `src/ingestion/github_client.py`. This class acts as a dedicated wrapper around the `httpx.Client`.

The initialization of the `GitHubClient` requires the `GITHUB_TOKEN`. It configures the underlying `httpx.Client` with the base URL (`https://api.github.com`), default timeout parameters (e.g., 10 seconds), and critically, default headers. These headers must include `Accept: application/vnd.github.v3+json` to ensure the correct API version, and `Authorization: Bearer {token}` to authenticate the requests.

The class exposes two primary methods:
1. `get_repository_metrics(self, owner: str, repo: str) -> dict`: This method targets the `/repos/{owner}/{repo}` endpoint. Its responsibility is to fetch the core repository information. Before returning the raw JSON dictionary, it must inspect the `response.status_code`. If a 404 is encountered, it must raise the `RepositoryNotFoundError`. If a 403 or 429 is encountered, it must raise the `RateLimitExceededError`.
2. `get_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[dict]`: This method targets the `/repos/{owner}/{repo}/commits` endpoint. It must include query parameters to enforce the limit (`per_page=100`). Similar to the metrics method, it must rigorously check status codes and translate HTTP errors into domain exceptions before returning the raw JSON array.

**Important Constraint:** The `GitHubClient` should *not* instantiate the Pydantic models itself. Its sole responsibility is network transport and error translation. It returns raw `dict` or `list[dict]` objects. Validation and instantiation will occur in the service layer in subsequent cycles. This maintains a strict separation of concerns.

## Implementation Approach
1. **Dependency Verification:** Ensure `httpx` is added to the project dependencies (this should be handled via the primary `pyproject.toml` configuration, but the Coder must verify its availability).
2. **Implement GitHubClient:** Create `src/ingestion/github_client.py`. Import `httpx` and the domain exceptions.
3. **Class Definition:** Define `class GitHubClient`. Implement the `__init__` method accepting the token string. Initialize `self.client = httpx.Client(...)` with the appropriate `base_url` and headers. Ensure the client is properly closed, either by providing a `close` method or utilizing it as a context manager (though a persistent client instance is often preferred for connection pooling).
4. **Implement Metrics Method:** Write `get_repository_metrics`. Use `self.client.get(...)` to construct the request. Implement a unified private helper method (e.g., `_handle_response`) to process the `httpx.Response` object, checking for `is_error` and raising `RepositoryNotFoundError` on 404 or `RateLimitExceededError` on 403/429. Return `response.json()`.
5. **Implement Commits Method:** Write `get_recent_commits`. Construct the URL and pass `params={"per_page": limit}` to the `get` request. Utilize the same error-handling helper. Return the JSON list.

## Test Strategy

### Unit Testing Approach
Unit testing will rely heavily on `pytest-httpx` to isolate the `GitHubClient` from the network. The tests will reside in `tests/test_ingestion.py`.
- **Initialization Test:** Verify that the `GitHubClient` constructs the `httpx.Client` with the correct `Authorization` and `Accept` headers based on the provided token.
- **Successful Response (Metrics & Commits):** Use `httpx_mock.add_response` to simulate a successful 200 OK HTTP response containing a mock JSON dictionary (for metrics) or a JSON list (for commits). Call the client methods and assert that the returned data matches the mock payload exactly.
- **Error Handling (404 Not Found):** Use `httpx_mock.add_response(status_code=404)` to simulate a repository that does not exist. Assert that calling the client methods strictly raises the `RepositoryNotFoundError` defined in the domain layer.
- **Error Handling (403 Rate Limit):** Use `httpx_mock.add_response(status_code=403)` to simulate rate limiting. Assert that the client strictly raises the `RateLimitExceededError`.

### Integration Testing Approach
While true integration testing with live APIs is discouraged in the automated CI, a local execution test is valuable.
- **Live Test (Skipped by Default):** Create a test marked with `@pytest.mark.skip(reason="Live API test")` that utilizes a real `GITHUB_TOKEN` from the `.env` file (if present) to execute a single request against a known repository (e.g., `streamlit/streamlit`) to verify the actual network path and JSON structure alignment. This ensures the client works in reality without failing CI pipelines.
