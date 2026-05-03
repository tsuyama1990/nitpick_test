# CYCLE 01 UAT: API Client Validation

## Test Scenarios

### Scenario ID: C01-01 - Successful Data Extraction
*   **Priority**: High
*   **Description**: Verify that the API client can successfully connect to GitHub, authenticate securely, and retrieve strictly typed repository metadata and commit history for a known public repository. This scenario ensures the foundational ingestion layer operates flawlessly under ideal conditions.
*   **Execution Strategy**: A Marimo notebook (`tutorials/UAT_AND_TUTORIAL.py`) will instantiate the `github_client` with valid credentials and invoke the fetch methods against a repository like `streamlit/streamlit`. The output will be inspected to confirm the return types are the expected Pydantic models.

### Scenario ID: C01-02 - Error Handling for Invalid Repositories
*   **Priority**: High
*   **Description**: Ensure the client gracefully handles requests for non-existent repositories (404 Not Found) by raising a specific, catchable custom exception rather than crashing or exposing raw HTTP library errors.
*   **Execution Strategy**: The Marimo notebook will invoke the client against `invalid-owner/non-existent-repo-12345` and assert that a `RepositoryNotFoundError` (or similar custom exception) is raised.

## Behavior Definitions

**Given** a valid `.env` file containing a `GITHUB_TOKEN`,
**When** the API client requests metadata for `streamlit/streamlit`,
**Then** the client must return a validated `RepositoryMetadata` object containing accurate star and fork counts.

**Given** a missing or invalid `GITHUB_TOKEN`,
**When** the API client attempts to authenticate,
**Then** the client must raise an `AuthenticationError` securely without logging the invalid token.
# CYCLE 01 UAT: API Client Validation

## Test Scenarios

### Scenario ID: C01-01 - Successful Data Extraction
*   **Priority**: High
*   **Description**: Verify that the API client can successfully connect to GitHub, authenticate securely, and retrieve strictly typed repository metadata and commit history for a known public repository. This scenario ensures the foundational ingestion layer operates flawlessly under ideal conditions.
*   **Execution Strategy**: A Marimo notebook (`tutorials/UAT_AND_TUTORIAL.py`) will instantiate the `github_client` with valid credentials and invoke the fetch methods against a repository like `streamlit/streamlit`. The output will be inspected to confirm the return types are the expected Pydantic models.

### Scenario ID: C01-02 - Error Handling for Invalid Repositories
*   **Priority**: High
*   **Description**: Ensure the client gracefully handles requests for non-existent repositories (404 Not Found) by raising a specific, catchable custom exception rather than crashing or exposing raw HTTP library errors.
*   **Execution Strategy**: The Marimo notebook will invoke the client against `invalid-owner/non-existent-repo-12345` and assert that a `RepositoryNotFoundError` (or similar custom exception) is raised.

## Behavior Definitions

**Given** a valid `.env` file containing a `GITHUB_TOKEN`,
**When** the API client requests metadata for `streamlit/streamlit`,
**Then** the client must return a validated `RepositoryMetadata` object containing accurate star and fork counts.

**Given** a missing or invalid `GITHUB_TOKEN`,
**When** the API client attempts to authenticate,
**Then** the client must raise an `AuthenticationError` securely without logging the invalid token.
# CYCLE 01 UAT: API Client Validation

## Test Scenarios

### Scenario ID: C01-01 - Successful Data Extraction
*   **Priority**: High
*   **Description**: Verify that the API client can successfully connect to GitHub, authenticate securely, and retrieve strictly typed repository metadata and commit history for a known public repository. This scenario ensures the foundational ingestion layer operates flawlessly under ideal conditions.
*   **Execution Strategy**: A Marimo notebook (`tutorials/UAT_AND_TUTORIAL.py`) will instantiate the `github_client` with valid credentials and invoke the fetch methods against a repository like `streamlit/streamlit`. The output will be inspected to confirm the return types are the expected Pydantic models.

### Scenario ID: C01-02 - Error Handling for Invalid Repositories
*   **Priority**: High
*   **Description**: Ensure the client gracefully handles requests for non-existent repositories (404 Not Found) by raising a specific, catchable custom exception rather than crashing or exposing raw HTTP library errors.
*   **Execution Strategy**: The Marimo notebook will invoke the client against `invalid-owner/non-existent-repo-12345` and assert that a `RepositoryNotFoundError` (or similar custom exception) is raised.

## Behavior Definitions

**Given** a valid `.env` file containing a `GITHUB_TOKEN`,
**When** the API client requests metadata for `streamlit/streamlit`,
**Then** the client must return a validated `RepositoryMetadata` object containing accurate star and fork counts.

**Given** a missing or invalid `GITHUB_TOKEN`,
**When** the API client attempts to authenticate,
**Then** the client must raise an `AuthenticationError` securely without logging the invalid token.
