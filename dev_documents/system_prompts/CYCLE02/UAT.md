# Cycle 02: User Acceptance Testing Plan

## Test Scenarios

### Scenario ID: UAT-C02-01
**Priority:** High
**Description:** Verify the GitHub API Client successfully retrieves and parses metrics data for a known, public repository using mocked network responses.

### Scenario ID: UAT-C02-02
**Priority:** High
**Description:** Verify the GitHub API Client successfully handles HTTP 404 responses by translating them into the application's specific `RepositoryNotFoundError`.

## Behavior Definitions

### UAT-C02-01: Successful Data Retrieval
**GIVEN** the GitHub API Client is configured with a valid token
**AND** the network layer is mocked to return a valid JSON payload for the `streamlit/streamlit` repository
**WHEN** a request is made to fetch repository metrics
**THEN** the client must return a Python dictionary containing the expected keys (`stargazers_count`, `forks_count`, `open_issues_count`) corresponding to the mock data.

### UAT-C02-02: Graceful Error Translation
**GIVEN** the network layer is mocked to return an HTTP 404 Not Found status code
**WHEN** a request is made to fetch metrics for a non-existent repository (e.g., `invalid-owner/invalid-repo`)
**THEN** the client must intercept the HTTP error
**AND** explicitly raise a `RepositoryNotFoundError` to prevent raw HTTP traces from propagating up the application stack.
