# Cycle 04: User Acceptance Testing Plan

## Test Scenarios

### Scenario ID: UAT-C04-01
**Priority:** High
**Description:** Verify the local caching system successfully serializes and deserializes Polars DataFrames without data loss or schema alteration.

### Scenario ID: UAT-C04-02
**Priority:** High
**Description:** Verify the caching system correctly invalidates stale data based on the Time-To-Live (TTL) configuration, ensuring the application eventually fetches fresh metrics.

## Behavior Definitions

### UAT-C04-01: Cache Hit Accuracy
**GIVEN** a pre-calculated Polars DataFrame representing aggregated commit data
**WHEN** the DataFrame is saved to the cache and immediately retrieved
**THEN** the retrieved DataFrame must be structurally identical to the original DataFrame
**AND** all column data types must be perfectly preserved after the Parquet serialization round-trip.

### UAT-C04-02: TTL Expiration Logic
**GIVEN** a cached Parquet file containing historical commit data
**AND** the file's metadata indicates it was created 2 hours ago
**WHEN** the system attempts to retrieve the data from a cache configured with a 1-hour TTL
**THEN** the cache must report a cache miss (return None)
**AND** signal to the upstream orchestrator that fresh data must be ingested from the external API.
