# Cycle 05: User Acceptance Testing Plan

## Test Scenarios

### Scenario ID: UAT-C05-01
**Priority:** High
**Description:** Verify the Orchestrator correctly routes data flow on a "Cold Start" (Cache Miss), fetching from the API, processing the data, and successfully populating the UI-ready payload.

### Scenario ID: UAT-C05-02
**Priority:** High
**Description:** Verify the Orchestrator successfully intercepts data requests on a "Warm Start" (Cache Hit), bypassing the external API completely and serving data directly from the local Parquet cache to protect rate limits.

## Behavior Definitions

### UAT-C05-01: Cold Start Data Pipeline
**GIVEN** an empty local cache and a valid repository request
**WHEN** the Orchestrator attempts to retrieve dashboard data
**THEN** the system must invoke the GitHub API client to fetch raw data
**AND** transform the raw data into Polars DataFrames
**AND** save the DataFrames to the local cache before returning the final payload.

### UAT-C05-02: Warm Start Rate Limit Protection
**GIVEN** the Orchestrator has recently processed data for a specific repository
**AND** valid Parquet files exist in the local cache within the TTL window
**WHEN** a subsequent request is made for the exact same repository
**THEN** the Orchestrator must immediately return the processed DataFrames from the cache
**AND** strictly execute zero HTTP requests against the GitHub API to ensure rate limit compliance.
