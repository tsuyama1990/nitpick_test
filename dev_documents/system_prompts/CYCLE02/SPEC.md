# CYCLE02: API Client & Raw Data Fetching

## Summary

Cycle 02 focuses on the Ingestion Layer. The objective is to build a robust HTTP client capable of interacting with the live GitHub REST API. This module will utilize the secure configuration and domain models created in Cycle 01. The key technical challenge is enforcing strict error handling for API rate limits and authentication failures, ensuring the application fails gracefully rather than crashing. The client must never expose the raw API token in logs or stack traces.

## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
- Maintained from Cycle 01: `GITHUB_TOKEN`
- Ensure no new external API services are added.

### B. System Configurations (`docker-compose.yml`)
- Maintained from Cycle 01.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
- **Mandate Mocking:** You MUST strictly use the `pytest-httpx` library to securely mock all network requests. Ensure that unit tests and standard test runs NEVER hit the live GitHub API without the explicit `@pytest.mark.live` marker. This guarantees isolation and prevents the CI pipeline from failing due to missing API keys or rate limits during automated execution. Use `pytest_httpx.HTTPXMock` for type-hinting the fixture.

## System Architecture

The following directories and files must be implemented or modified:

.
├── src/
│   ├── config/
│   │   └── settings.py
│   ├── domain_models/
│   │   ├── repository.py
│   │   └── commit.py
│   └── ingestion/
│       ├── **__init__.py**
│       └── **github_client.py**
└── tests/
    └── **test_ingestion.py**

## Design Architecture

**GitHubClient (`src/ingestion/github_client.py`)**
- Encapsulates all GitHub API communication logic.
- Methods:
  - `fetch_repository_info(owner: str, repo: str) -> RepositoryInfo`: Hits `GET /repos/{owner}/{repo}`.
  - `fetch_recent_commits(owner: str, repo: str, limit: int = 100) -> list[CommitData]`: Hits `GET /repos/{owner}/{repo}/commits` with a per_page limit.
- Key Invariants & Constraints:
  - Header Injection: Must securely inject the authorization header using the format `Authorization: token {token}` (not Bearer).
  - Rate Limit & Error Handling: Before calling `.json()`, the client must explicitly check `response.status_code`. If 403 or 429 is encountered, it must raise a custom `RateLimitError`. If 401, a custom `AuthError`. For 404, a `NotFoundError`. This prevents `JSONDecodeError` on non-JSON error pages.
  - Security: Ensure the HTTP logger (`logging.getLogger('httpx')`) is set to `logging.WARNING` to prevent sensitive header leakage.
- Consumers: The Controller layer (to be built later).
- Producers: Consumes GitHub REST API. Returns validated Pydantic models (`RepositoryInfo`, `CommitData`).

## Implementation Approach

1. **Init File**: Ensure `src/ingestion/__init__.py` exists.
2. **Implement GitHubClient**: Create `src/ingestion/github_client.py`.
3. **HTTP Setup**: Use the `httpx` library. Configure standard headers, including `Accept: application/vnd.github.v3+json`. Retrieve the `GITHUB_TOKEN` securely using the `get_settings()` singleton.
4. **Error Handling**: Implement the error checking logic directly examining `response.status_code` before parsing JSON.
5. **Data Fetching**: Implement `fetch_repository_info`. Use `httpx.get`. Check the status. Pass the resulting JSON dictionary to the `RepositoryInfo` model to instantiate and return it.
6. **Commit Fetching**: Implement `fetch_recent_commits`. Fetch the list of commits, iterate over the payload, instantiate a `CommitData` model for each, and return the typed list.
7. **Linting and Typing**: Execute `uv run ruff check .` and `uv run mypy .`. Ensure `httpx` is added to requirements if not already present.

## Test Strategy

**Unit Testing Approach (Min 300 words)**
We will use the `pytest-httpx` library to mock out the GitHub REST API. For `fetch_repository_info`, we will configure `httpx_mock` to return a massive JSON response simulating GitHub's payload, asserting that the client successfully parses it and returns a valid `RepositoryInfo` Pydantic object. Similarly, for `fetch_recent_commits`, we will mock a JSON array of nested commit nodes, verifying the client returns a list of correctly flattened `CommitData` objects. Critical security tests will ensure that `httpx` logging configuration is strictly evaluated, verifying that sensitive headers are not inadvertently recorded in standard debug logs. Mypy strict constraints will be satisfied by importing `HTTPXMock` correctly for the fixture type hints.

**Integration Testing Approach (Min 300 words)**
Integration testing for the ingestion layer requires careful handling of exceptional states. We will simulate external SaaS failures by mocking HTTP 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), and 429 (Too Many Requests) responses using `pytest-httpx`. We will assert that the `GitHubClient` explicitly intercepts these status codes and raises our custom, secure exception types (e.g., `RateLimitError`, `NotFoundError`) *before* attempting to execute a `.json()` parser, effectively preventing ugly stack traces and `JSONDecodeError`s. Finally, we will define a live test (decorated with `@pytest.mark.live` and configured out of standard runs via `pyproject.toml`) that optionally hits the real GitHub API using a valid token, providing absolute proof that the Pydantic schemas and client headers perfectly align with GitHub's live schema evolution.
