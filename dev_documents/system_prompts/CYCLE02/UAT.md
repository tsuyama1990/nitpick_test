# CYCLE 02 UAT: Transformation and Caching Validation

## Test Scenarios

### Scenario ID: C02-01 - Accurate Data Transformation
*   **Priority**: High
*   **Description**: Verify that the implemented Polars transformation logic mathematically and accurately calculates the daily commit frequency trends and definitively identifies the top 5 highest-volume committers without any runtime errors, absolutely ensuring the data is perfectly formatted and ready for complex UI visualization.
*   **Execution Strategy**: The interactive Marimo notebook will explicitly load a known, totally static JSON dataset containing exactly 100 heavily engineered mock commits (completely bypassing the real external API). It will programmatically pass this dataset entirely through the `transformer` module, and physically present the resulting DataFrames on screen. The reviewing user will manually and mathematically verify that the top listed committer perfectly matches the expected, hardcoded name from the static dataset.

### Scenario ID: C02-02 - Cache Effectiveness and TTL Verification
*   **Priority**: Critical
*   **Description**: Ensure the implemented local Parquet caching mechanism successfully and completely prevents redundant outbound API calls and drastically, noticeably reduces data response times for subsequent, repeated requests occurring within the defined TTL window.
*   **Execution Strategy**: The Marimo notebook will execute a live, real-world data fetch for a massive repository, explicitly recording and displaying the exact execution time. It will then immediately execute the exact same fetch command a second time, programmatically asserting that the second execution is significantly, mathematically faster (by several orders of magnitude) and explicitly verifying via application logs or test mock assertions that absolutely no actual external network request was dispatched during the second attempt.

## Behavior Definitions

**Given** a mathematically valid, perfectly structured set of commit records,
**When** the Polars transformer engine aggregates the data specifically by calendar date,
**Then** the final output DataFrame must mathematically group all individual commits occurring on the exact same calendar day into a single, combined row containing the mathematically correct total count integer.

**Given** a specifically requested target repository already has a completely valid Parquet cache file physically located on the disk that was created exactly 5 minutes ago (and the system TTL is set to 60 mins),
**When** the system orchestrator requests data for this specific repository,
**Then** the cache manager must intercept the request and instantaneously return the data entirely from the local disk, completely and absolutely bypassing the GitHub API client module.
