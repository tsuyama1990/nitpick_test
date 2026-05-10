# Cycle 03: User Acceptance Testing Plan

## Test Scenarios

### Scenario ID: UAT-C03-01
**Priority:** High
**Description:** Verify the Polars transformation logic correctly aggregates commit data by date, maintaining strict schema types suitable for downstream rendering.

### Scenario ID: UAT-C03-02
**Priority:** High
**Description:** Verify the Polars transformation logic correctly calculates the top committers and resolves ties deterministically using a secondary sort key.

## Behavior Definitions

### UAT-C03-01: Date Aggregation Accuracy
**GIVEN** a mock JSON dataset containing commits spread across multiple dates
**WHEN** the data is processed by the date aggregation function
**THEN** the resulting DataFrame must contain a `date` column of a native Date type and a `commit_count` column
**AND** the total sum of `commit_count` must exactly equal the number of input records.

### UAT-C03-02: Deterministic Top Committers
**GIVEN** a mock dataset where users "Alice", "Bob", and "Charlie" each have an identical number of commits
**WHEN** the data is processed to find the top 2 committers
**THEN** the system must consistently return "Alice" and "Bob" based on alphabetical tie-breaking
**AND** the application must not exhibit flaky behavior or random result ordering across multiple executions.
