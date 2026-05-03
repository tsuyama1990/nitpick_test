# CYCLE 02 SPECIFICATION: Data Transformation and Local Storage

## Summary
The primary objective of Cycle 02 is to build the "Transformation and Storage Layer" of the architecture. This layer serves as the engine for processing raw data and managing application performance. Using the highly performant Polars library, we will implement logic to transform the structured Pydantic models (obtained in Cycle 01) into aggregated DataFrames required for visualization: daily commit counts and top committer rankings. Furthermore, to aggressively protect against GitHub API rate limits and drastically improve application responsiveness, we will implement a robust local caching mechanism. This cache will serialize the processed Polars DataFrames into Parquet files, utilizing a Time-to-Live (TTL) strategy to ensure data freshness while minimizing redundant network calls. By the end of this cycle, the system will efficiently process historical data and serve repeated requests instantaneously from disk.
# CYCLE 02 SPECIFICATION: Data Transformation and Local Storage

## Summary
The primary objective of Cycle 02 is to build the "Transformation and Storage Layer" of the architecture. This layer serves as the engine for processing raw data and managing application performance. Using the highly performant Polars library, we will implement logic to transform the structured Pydantic models (obtained in Cycle 01) into aggregated DataFrames required for visualization: daily commit counts and top committer rankings. Furthermore, to aggressively protect against GitHub API rate limits and drastically improve application responsiveness, we will implement a robust local caching mechanism. This cache will serialize the processed Polars DataFrames into Parquet files, utilizing a Time-to-Live (TTL) strategy to ensure data freshness while minimizing redundant network calls. By the end of this cycle, the system will efficiently process historical data and serve repeated requests instantaneously from disk.
# CYCLE 02 SPECIFICATION: Data Transformation and Local Storage

## Summary
The primary objective of Cycle 02 is to build the "Transformation and Storage Layer" of the architecture. This layer serves as the engine for processing raw data and managing application performance. Using the highly performant Polars library, we will implement logic to transform the structured Pydantic models (obtained in Cycle 01) into aggregated DataFrames required for visualization: daily commit counts and top committer rankings. Furthermore, to aggressively protect against GitHub API rate limits and drastically improve application responsiveness, we will implement a robust local caching mechanism. This cache will serialize the processed Polars DataFrames into Parquet files, utilizing a Time-to-Live (TTL) strategy to ensure data freshness while minimizing redundant network calls. By the end of this cycle, the system will efficiently process historical data and serve repeated requests instantaneously from disk.
# CYCLE 02 SPECIFICATION: Data Transformation and Local Storage

## Summary
The primary objective of Cycle 02 is to build the "Transformation and Storage Layer" of the architecture. This layer serves as the engine for processing raw data and managing application performance. Using the highly performant Polars library, we will implement logic to transform the structured Pydantic models (obtained in Cycle 01) into aggregated DataFrames required for visualization: daily commit counts and top committer rankings. Furthermore, to aggressively protect against GitHub API rate limits and drastically improve application responsiveness, we will implement a robust local caching mechanism. This cache will serialize the processed Polars DataFrames into Parquet files, utilizing a Time-to-Live (TTL) strategy to ensure data freshness while minimizing redundant network calls. By the end of this cycle, the system will efficiently process historical data and serve repeated requests instantaneously from disk.
# CYCLE 02 SPECIFICATION: Data Transformation and Local Storage

## Summary
The primary objective of Cycle 02 is to build the "Transformation and Storage Layer" of the architecture. This layer serves as the engine for processing raw data and managing application performance. Using the highly performant Polars library, we will implement logic to transform the structured Pydantic models (obtained in Cycle 01) into aggregated DataFrames required for visualization: daily commit counts and top committer rankings. Furthermore, to aggressively protect against GitHub API rate limits and drastically improve application responsiveness, we will implement a robust local caching mechanism. This cache will serialize the processed Polars DataFrames into Parquet files, utilizing a Time-to-Live (TTL) strategy to ensure data freshness while minimizing redundant network calls. By the end of this cycle, the system will efficiently process historical data and serve repeated requests instantaneously from disk.


## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
*   (No new external service secrets are required for this cycle. The existing GitHub token from Cycle 01 remains applicable.)

### B. System Configurations (`docker-compose.yml`)
*   **Local Storage Directory**: Define an environment variable (e.g., `CACHE_DIR=./.cache`) to specify where the Parquet files should be stored.
    *   **Instruction for Coder**: Ensure this directory is created automatically if it doesn't exist and is excluded from version control via `.gitignore`.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
*   **Mandate Mocking**: All tests verifying the transformation and caching logic MUST operate entirely independently of the network. The API client must be fully mocked. Furthermore, tests interacting with the file system (for cache validation) MUST utilize Pytest's `tmp_path` fixture to guarantee isolation and prevent tests from polluting the local environment or failing due to permission issues in the sandbox.

## System Architecture
This cycle introduces the processing and caching components, positioned between the ingestion layer and the future UI layer.

```text
.
├── src/
│   ├── config.py             # Updated with CACHE_DIR
│   ├── domain/
│   │   └── models.py         # Reused from Cycle 01
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── transformer.py    # Polars DataFrame aggregations
│   │   └── cache_manager.py  # Local Parquet storage logic
└── tests/
    └── unit/
        ├── test_transformer.py
        └── test_cache_manager.py
```

*   `src/processing/transformer.py`: Consumes a list of `CommitRecord` Pydantic models, converts them into a Polars DataFrame, and executes the required aggregations (group by date, count by author).
*   `src/processing/cache_manager.py`: Handles the I/O operations. It checks for the existence of valid Parquet files based on a TTL, reads them using Polars, and writes newly transformed DataFrames to disk.
## System Architecture
This cycle introduces the processing and caching components, positioned between the ingestion layer and the future UI layer.

```text
.
├── src/
│   ├── config.py             # Updated with CACHE_DIR
│   ├── domain/
│   │   └── models.py         # Reused from Cycle 01
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── transformer.py    # Polars DataFrame aggregations
│   │   └── cache_manager.py  # Local Parquet storage logic
└── tests/
    └── unit/
        ├── test_transformer.py
        └── test_cache_manager.py
```

*   `src/processing/transformer.py`: Consumes a list of `CommitRecord` Pydantic models, converts them into a Polars DataFrame, and executes the required aggregations (group by date, count by author).
*   `src/processing/cache_manager.py`: Handles the I/O operations. It checks for the existence of valid Parquet files based on a TTL, reads them using Polars, and writes newly transformed DataFrames to disk.
## System Architecture
This cycle introduces the processing and caching components, positioned between the ingestion layer and the future UI layer.

```text
.
├── src/
│   ├── config.py             # Updated with CACHE_DIR
│   ├── domain/
│   │   └── models.py         # Reused from Cycle 01
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── transformer.py    # Polars DataFrame aggregations
│   │   └── cache_manager.py  # Local Parquet storage logic
└── tests/
    └── unit/
        ├── test_transformer.py
        └── test_cache_manager.py
```

*   `src/processing/transformer.py`: Consumes a list of `CommitRecord` Pydantic models, converts them into a Polars DataFrame, and executes the required aggregations (group by date, count by author).
*   `src/processing/cache_manager.py`: Handles the I/O operations. It checks for the existence of valid Parquet files based on a TTL, reads them using Polars, and writes newly transformed DataFrames to disk.
## System Architecture
This cycle introduces the processing and caching components, positioned between the ingestion layer and the future UI layer.

```text
.
├── src/
│   ├── config.py             # Updated with CACHE_DIR
│   ├── domain/
│   │   └── models.py         # Reused from Cycle 01
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── transformer.py    # Polars DataFrame aggregations
│   │   └── cache_manager.py  # Local Parquet storage logic
└── tests/
    └── unit/
        ├── test_transformer.py
        └── test_cache_manager.py
```

*   `src/processing/transformer.py`: Consumes a list of `CommitRecord` Pydantic models, converts them into a Polars DataFrame, and executes the required aggregations (group by date, count by author).
*   `src/processing/cache_manager.py`: Handles the I/O operations. It checks for the existence of valid Parquet files based on a TTL, reads them using Polars, and writes newly transformed DataFrames to disk.
## System Architecture
This cycle introduces the processing and caching components, positioned between the ingestion layer and the future UI layer.

```text
.
├── src/
│   ├── config.py             # Updated with CACHE_DIR
│   ├── domain/
│   │   └── models.py         # Reused from Cycle 01
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── transformer.py    # Polars DataFrame aggregations
│   │   └── cache_manager.py  # Local Parquet storage logic
└── tests/
    └── unit/
        ├── test_transformer.py
        └── test_cache_manager.py
```

*   `src/processing/transformer.py`: Consumes a list of `CommitRecord` Pydantic models, converts them into a Polars DataFrame, and executes the required aggregations (group by date, count by author).
*   `src/processing/cache_manager.py`: Handles the I/O operations. It checks for the existence of valid Parquet files based on a TTL, reads them using Polars, and writes newly transformed DataFrames to disk.

## Design Architecture
This cycle focuses on the transition from Pydantic domain models to highly optimized Polars DataFrames.

*   **Polars DataFrames**: Serve as the primary data structure for aggregation. We transition from object-oriented Pydantic models to columnar data processing to achieve superior performance, especially when handling thousands of commits.
*   **`CacheEntry` Metadata**: While the actual data is stored in Parquet format, the cache manager must track metadata (e.g., timestamp of creation, target repository) to enforce the TTL. This can be achieved through file naming conventions (e.g., `facebook_react_commits_1678886400.parquet`) or a separate lightweight index.
*   **Invariants**: The Transformer must guarantee that the output DataFrames strictly adhere to the schema expected by the UI (e.g., a DataFrame with columns `['date', 'commit_count']` and another with `['author', 'commit_count']`).
*   **Backward Compatibility**: The caching format (Parquet) is chosen for its robustness and schema evolution capabilities, ensuring that if we add new columns in the future, older cache files might still be readable (or easily invalidated).
## Design Architecture
This cycle focuses on the transition from Pydantic domain models to highly optimized Polars DataFrames.

*   **Polars DataFrames**: Serve as the primary data structure for aggregation. We transition from object-oriented Pydantic models to columnar data processing to achieve superior performance, especially when handling thousands of commits.
*   **`CacheEntry` Metadata**: While the actual data is stored in Parquet format, the cache manager must track metadata (e.g., timestamp of creation, target repository) to enforce the TTL. This can be achieved through file naming conventions (e.g., `facebook_react_commits_1678886400.parquet`) or a separate lightweight index.
*   **Invariants**: The Transformer must guarantee that the output DataFrames strictly adhere to the schema expected by the UI (e.g., a DataFrame with columns `['date', 'commit_count']` and another with `['author', 'commit_count']`).
*   **Backward Compatibility**: The caching format (Parquet) is chosen for its robustness and schema evolution capabilities, ensuring that if we add new columns in the future, older cache files might still be readable (or easily invalidated).
## Design Architecture
This cycle focuses on the transition from Pydantic domain models to highly optimized Polars DataFrames.

*   **Polars DataFrames**: Serve as the primary data structure for aggregation. We transition from object-oriented Pydantic models to columnar data processing to achieve superior performance, especially when handling thousands of commits.
*   **`CacheEntry` Metadata**: While the actual data is stored in Parquet format, the cache manager must track metadata (e.g., timestamp of creation, target repository) to enforce the TTL. This can be achieved through file naming conventions (e.g., `facebook_react_commits_1678886400.parquet`) or a separate lightweight index.
*   **Invariants**: The Transformer must guarantee that the output DataFrames strictly adhere to the schema expected by the UI (e.g., a DataFrame with columns `['date', 'commit_count']` and another with `['author', 'commit_count']`).
*   **Backward Compatibility**: The caching format (Parquet) is chosen for its robustness and schema evolution capabilities, ensuring that if we add new columns in the future, older cache files might still be readable (or easily invalidated).

## Implementation Approach
1.  **Dependency Addition**: Add `polars` and `pyarrow` (required for Parquet support in Polars) to the project dependencies.
2.  **Transformer Logic**: Implement `transformer.py`. Write a function that takes a list of `CommitRecord`s, creates a Polars DataFrame, extracts the date from the datetime object, and performs a `group_by('date').count()` aggregation. Write another function to `group_by('author').count().sort('count', descending=True).head(5)`.
3.  **Cache Manager Implementation**: Implement `cache_manager.py`. Define a TTL (e.g., 3600 seconds). Implement `save_to_cache(repo_name, df)` which writes the DataFrame to `{CACHE_DIR}/{repo_name}_commits.parquet`. Implement `load_from_cache(repo_name)` which checks the file's modification time against the TTL; if valid, read and return the DataFrame, otherwise return `None`.
4.  **Integration**: Ensure the main application logic cleanly orchestrates checking the cache, falling back to the API client if necessary, and then saving the new data back to the cache.
## Implementation Approach
1.  **Dependency Addition**: Add `polars` and `pyarrow` (required for Parquet support in Polars) to the project dependencies.
2.  **Transformer Logic**: Implement `transformer.py`. Write a function that takes a list of `CommitRecord`s, creates a Polars DataFrame, extracts the date from the datetime object, and performs a `group_by('date').count()` aggregation. Write another function to `group_by('author').count().sort('count', descending=True).head(5)`.
3.  **Cache Manager Implementation**: Implement `cache_manager.py`. Define a TTL (e.g., 3600 seconds). Implement `save_to_cache(repo_name, df)` which writes the DataFrame to `{CACHE_DIR}/{repo_name}_commits.parquet`. Implement `load_from_cache(repo_name)` which checks the file's modification time against the TTL; if valid, read and return the DataFrame, otherwise return `None`.
4.  **Integration**: Ensure the main application logic cleanly orchestrates checking the cache, falling back to the API client if necessary, and then saving the new data back to the cache.
## Implementation Approach
1.  **Dependency Addition**: Add `polars` and `pyarrow` (required for Parquet support in Polars) to the project dependencies.
2.  **Transformer Logic**: Implement `transformer.py`. Write a function that takes a list of `CommitRecord`s, creates a Polars DataFrame, extracts the date from the datetime object, and performs a `group_by('date').count()` aggregation. Write another function to `group_by('author').count().sort('count', descending=True).head(5)`.
3.  **Cache Manager Implementation**: Implement `cache_manager.py`. Define a TTL (e.g., 3600 seconds). Implement `save_to_cache(repo_name, df)` which writes the DataFrame to `{CACHE_DIR}/{repo_name}_commits.parquet`. Implement `load_from_cache(repo_name)` which checks the file's modification time against the TTL; if valid, read and return the DataFrame, otherwise return `None`.
4.  **Integration**: Ensure the main application logic cleanly orchestrates checking the cache, falling back to the API client if necessary, and then saving the new data back to the cache.

## Test Strategy

### Unit Testing Approach
Unit tests must verify the Polars logic and the file system operations in complete isolation.
*   **Transformer Tests**: Supply a static list of hardcoded `CommitRecord` mock objects representing various scenarios (multiple commits on the same day, ties in commit counts). Assert that the resulting Polars DataFrames contain the exact expected values and column names.
*   **Cache Manager Tests**: Use Pytest's `tmp_path` fixture extensively. Test writing a dummy DataFrame to the temporary path and reading it back. Test the TTL logic by manually manipulating the file's modification time (using `os.utime`) to simulate an expired cache and verify that the manager correctly identifies it as invalid and returns `None`.

### Integration Testing Approach
Integration tests will verify the orchestration logic.
*   **Cache Hit/Miss Simulation**: Write a test that mocks the API client. Call the main extraction flow twice. Assert that the mocked API client is called exactly once during the first invocation (Cache Miss), and zero times during the second invocation (Cache Hit), proving that the caching mechanism successfully intercepts redundant requests.
## Test Strategy

### Unit Testing Approach
Unit tests must verify the Polars logic and the file system operations in complete isolation.
*   **Transformer Tests**: Supply a static list of hardcoded `CommitRecord` mock objects representing various scenarios (multiple commits on the same day, ties in commit counts). Assert that the resulting Polars DataFrames contain the exact expected values and column names.
*   **Cache Manager Tests**: Use Pytest's `tmp_path` fixture extensively. Test writing a dummy DataFrame to the temporary path and reading it back. Test the TTL logic by manually manipulating the file's modification time (using `os.utime`) to simulate an expired cache and verify that the manager correctly identifies it as invalid and returns `None`.

### Integration Testing Approach
Integration tests will verify the orchestration logic.
*   **Cache Hit/Miss Simulation**: Write a test that mocks the API client. Call the main extraction flow twice. Assert that the mocked API client is called exactly once during the first invocation (Cache Miss), and zero times during the second invocation (Cache Hit), proving that the caching mechanism successfully intercepts redundant requests.
## Test Strategy

### Unit Testing Approach
Unit tests must verify the Polars logic and the file system operations in complete isolation.
*   **Transformer Tests**: Supply a static list of hardcoded `CommitRecord` mock objects representing various scenarios (multiple commits on the same day, ties in commit counts). Assert that the resulting Polars DataFrames contain the exact expected values and column names.
*   **Cache Manager Tests**: Use Pytest's `tmp_path` fixture extensively. Test writing a dummy DataFrame to the temporary path and reading it back. Test the TTL logic by manually manipulating the file's modification time (using `os.utime`) to simulate an expired cache and verify that the manager correctly identifies it as invalid and returns `None`.

### Integration Testing Approach
Integration tests will verify the orchestration logic.
*   **Cache Hit/Miss Simulation**: Write a test that mocks the API client. Call the main extraction flow twice. Assert that the mocked API client is called exactly once during the first invocation (Cache Miss), and zero times during the second invocation (Cache Hit), proving that the caching mechanism successfully intercepts redundant requests.
