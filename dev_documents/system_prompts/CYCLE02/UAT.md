# CYCLE02: API Client & Raw Data Fetching (UAT)

## Test Scenarios

### Scenario 1: Successful API Ingestion and Model Instantiation
**ID**: UAT-C02-01
**Priority**: High
**Description**: Verify that the GitHub Client can connect to the mocked API, inject headers correctly, retrieve payload strings, and instantiate the strict Pydantic domain models created in Cycle 01.

### Scenario 2: Robust Error Handling (403, 404, 429)
**ID**: UAT-C02-02
**Priority**: High
**Description**: Ensure that when the API returns an error status code, the application does not crash with a JSON decode error. Instead, it must gracefully intercept the HTTP status code and raise domain-specific exceptions.

## Behavior Definitions

### UAT-C02-01: Successful API Ingestion and Model Instantiation
**GIVEN** a valid `owner/repo` string and a secure `GITHUB_TOKEN`
**WHEN** the `fetch_repository_info` method is called
**THEN** an HTTP GET request is sent to `https://api.github.com/repos/{owner}/{repo}`
**AND** the request contains the header `Authorization: token {token}`
**AND** the returned JSON payload is parsed into a `RepositoryInfo` model.

**GIVEN** a valid `owner/repo` string
**WHEN** the `fetch_recent_commits` method is called
**THEN** an HTTP GET request is sent with the appropriate query parameters (e.g., `per_page=100`)
**AND** the response array is mapped to a list of `CommitData` models, extracting author names and timestamps securely.

### UAT-C02-02: Robust Error Handling
**GIVEN** a network request to GitHub
**WHEN** the API responds with HTTP 403 (Forbidden) or HTTP 429 (Too Many Requests)
**THEN** the client immediately halts execution
**AND** raises a custom `RateLimitError`
**AND** prevents `.json()` execution.

**GIVEN** an invalid repository name
**WHEN** the API responds with HTTP 404 (Not Found)
**THEN** the client intercepts the status code and raises a custom `NotFoundError` without leaking stack traces to standard output.
