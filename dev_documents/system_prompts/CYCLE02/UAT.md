# CYCLE 02 UAT: Transformation and Caching Validation

## Test Scenarios

### Scenario ID: C02-01 - Accurate Data Transformation
*   **Priority**: High
*   **Description**: Verify that the Polars transformation logic accurately calculates the daily commit trends and identifies the top 5 committers without errors, ensuring the data is ready for visualization.
*   **Execution Strategy**: The Marimo notebook will load a known, static JSON dataset of 100 commits (bypassing the real API), pass it through the `transformer`, and present the resulting DataFrames. The user will manually verify that the top committer matches the expected name from the static dataset.

### Scenario ID: C02-02 - Cache Effectiveness and TTL
*   **Priority**: Critical
*   **Description**: Ensure the local Parquet cache successfully prevents redundant API calls and drastically reduces response times for subsequent requests within the TTL window.
*   **Execution Strategy**: The Marimo notebook will execute a live fetch for a repository, timing the operation. It will immediately execute the exact same fetch again, asserting that the second execution is significantly faster (orders of magnitude) and verifying via logs or mock assertions that no actual network request was dispatched.

## Behavior Definitions

**Given** a valid set of commit records,
**When** the transformer aggregates by date,
**Then** the output DataFrame must group all commits occurring on the same calendar day into a single row with the correct total count.

**Given** a requested repository has a valid Parquet cache file created 5 minutes ago (TTL=60 mins),
**When** the system requests data for this repository,
**Then** the cache manager must return the data from disk, completely bypassing the GitHub API client.
# CYCLE 02 UAT: Transformation and Caching Validation

## Test Scenarios

### Scenario ID: C02-01 - Accurate Data Transformation
*   **Priority**: High
*   **Description**: Verify that the Polars transformation logic accurately calculates the daily commit trends and identifies the top 5 committers without errors, ensuring the data is ready for visualization.
*   **Execution Strategy**: The Marimo notebook will load a known, static JSON dataset of 100 commits (bypassing the real API), pass it through the `transformer`, and present the resulting DataFrames. The user will manually verify that the top committer matches the expected name from the static dataset.

### Scenario ID: C02-02 - Cache Effectiveness and TTL
*   **Priority**: Critical
*   **Description**: Ensure the local Parquet cache successfully prevents redundant API calls and drastically reduces response times for subsequent requests within the TTL window.
*   **Execution Strategy**: The Marimo notebook will execute a live fetch for a repository, timing the operation. It will immediately execute the exact same fetch again, asserting that the second execution is significantly faster (orders of magnitude) and verifying via logs or mock assertions that no actual network request was dispatched.

## Behavior Definitions

**Given** a valid set of commit records,
**When** the transformer aggregates by date,
**Then** the output DataFrame must group all commits occurring on the same calendar day into a single row with the correct total count.

**Given** a requested repository has a valid Parquet cache file created 5 minutes ago (TTL=60 mins),
**When** the system requests data for this repository,
**Then** the cache manager must return the data from disk, completely bypassing the GitHub API client.
# CYCLE 02 UAT: Transformation and Caching Validation

## Test Scenarios

### Scenario ID: C02-01 - Accurate Data Transformation
*   **Priority**: High
*   **Description**: Verify that the Polars transformation logic accurately calculates the daily commit trends and identifies the top 5 committers without errors, ensuring the data is ready for visualization.
*   **Execution Strategy**: The Marimo notebook will load a known, static JSON dataset of 100 commits (bypassing the real API), pass it through the `transformer`, and present the resulting DataFrames. The user will manually verify that the top committer matches the expected name from the static dataset.

### Scenario ID: C02-02 - Cache Effectiveness and TTL
*   **Priority**: Critical
*   **Description**: Ensure the local Parquet cache successfully prevents redundant API calls and drastically reduces response times for subsequent requests within the TTL window.
*   **Execution Strategy**: The Marimo notebook will execute a live fetch for a repository, timing the operation. It will immediately execute the exact same fetch again, asserting that the second execution is significantly faster (orders of magnitude) and verifying via logs or mock assertions that no actual network request was dispatched.

## Behavior Definitions

**Given** a valid set of commit records,
**When** the transformer aggregates by date,
**Then** the output DataFrame must group all commits occurring on the same calendar day into a single row with the correct total count.

**Given** a requested repository has a valid Parquet cache file created 5 minutes ago (TTL=60 mins),
**When** the system requests data for this repository,
**Then** the cache manager must return the data from disk, completely bypassing the GitHub API client.
