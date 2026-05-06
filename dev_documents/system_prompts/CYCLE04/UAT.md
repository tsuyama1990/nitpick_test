# CYCLE04: Caching Mechanism (Parquet) (UAT)

## Test Scenarios

### Scenario 1: Parquet Serialization Integrity
**ID**: UAT-C04-01
**Priority**: High
**Description**: Verify that the system can reliably write Polars DataFrames to disk in a binary format without data loss or corruption, and read them back exactly as they were.

### Scenario 2: TTL Cache Invalidation
**ID**: UAT-C04-02
**Priority**: High
**Description**: Prove that the cache mechanism correctly invalidates stale data based on the Time-To-Live threshold, preventing users from seeing indefinitely outdated metrics.

## Behavior Definitions

### UAT-C04-01: Parquet Serialization Integrity
**GIVEN** a valid Polars DataFrame containing processed commit aggregations
**WHEN** the `save_to_cache` method is executed
**THEN** a `.parquet` file is generated in the designated directory
**AND** reading that file back via `load_from_cache` yields a DataFrame identical in shape, schema, and values to the original.

### UAT-C04-02: TTL Cache Invalidation
**GIVEN** a cached Parquet file that was created 10 minutes ago
**AND** a system TTL configuration of 60 minutes
**WHEN** `load_from_cache` is invoked
**THEN** the system returns the cached DataFrame (Cache Hit).

**GIVEN** a cached Parquet file that was created 61 minutes ago
**AND** a system TTL configuration of 60 minutes
**WHEN** `load_from_cache` is invoked
**THEN** the system returns `None` (Cache Miss), indicating the data is stale and must be refreshed.
