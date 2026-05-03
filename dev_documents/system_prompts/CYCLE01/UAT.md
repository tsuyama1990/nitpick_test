# CYCLE 01 UAT: API Client Validation

## Test Scenarios

### Scenario ID: C01-01 - Successful Data Extraction
*   **Priority**: High
*   **Description**: Verify that the implemented API client can successfully connect to the official GitHub API, authenticate securely using the provided token, and retrieve strictly typed repository metadata and a complete commit history for a known, highly stable public repository. This crucial scenario ensures the foundational ingestion layer operates absolutely flawlessly under ideal, expected conditions.
*   **Execution Strategy**: An interactive Marimo notebook (`tutorials/UAT_AND_TUTORIAL.py`) will be executed. It will instantiate the `github_client` with valid, secure credentials and deliberately invoke the fetch methods against a well-known repository like `streamlit/streamlit`. The resulting output will be visually inspected within the notebook cells to explicitly confirm the return types are indeed the expected, strictly validated Pydantic models.

### Scenario ID: C01-02 - Error Handling for Invalid Repositories
*   **Priority**: High
*   **Description**: Ensure the implemented API client gracefully handles requests for completely non-existent or deleted repositories (HTTP 404 Not Found). It must prove it raises a highly specific, catchable custom Python domain exception rather than crashing catastrophically or exposing raw, unintelligible HTTP library stack traces to the caller.
*   **Execution Strategy**: The interactive Marimo notebook will invoke the HTTP client against an intentionally invalid string, such as `invalid-owner/non-existent-repo-12345`, and programmatically assert that a descriptive `RepositoryNotFoundError` (or an equivalent custom exception) is correctly raised by the ingestion layer.

### Scenario ID: C01-03 - Authentication Failure Handling
*   **Priority**: Critical
*   **Description**: Validate the system's resilience against invalid or expired authentication tokens. The client must instantly recognize an HTTP 401/403 Unauthorized response and translate it into a secure, domain-specific error, absolutely guaranteeing the invalid token string is never leaked in the generated error message or system logs.
*   **Execution Strategy**: The Marimo notebook environment will be temporarily configured with a mathematically invalid token string (e.g., `ghp_invalidtoken123`). The client will attempt a data fetch. The test will rigorously assert that an `AuthenticationError` is raised and string-search the exception message to prove the secret is not present.

## Behavior Definitions

**Given** a valid `.env` file containing a correct `GITHUB_TOKEN`,
**When** the API client requests metadata for `streamlit/streamlit`,
**Then** the client must return a mathematically validated `RepositoryMetadata` object containing perfectly accurate star and fork counts matching the live GitHub repository state.

**Given** a missing or intentionally invalid `GITHUB_TOKEN` injected into the environment,
**When** the API client attempts to authenticate with the GitHub REST API,
**Then** the client must rapidly intercept the failure and raise an `AuthenticationError` securely, without logging or exposing the invalid token string in the error message.

**Given** a user input representing a repository that does not exist on GitHub,
**When** the API client executes the HTTP GET request and receives a 404 status code,
**Then** the client must catch the underlying HTTP error and translate it by raising a clearly defined `RepositoryNotFoundError` exception.
