# CYCLE 02 SPECIFICATION: Data Transformation and Local Storage

## Summary
The primary objective of Cycle 02 is to meticulously build the complex "Transformation and Storage Layer" of the overarching system architecture. This critical layer serves as the high-performance engine for processing raw ingested data and managing overall application performance. Using the exceptionally performant, Rust-backed Polars library, we will implement sophisticated mathematical logic to rapidly transform the structured, object-oriented Pydantic models (obtained during Cycle 01) into highly aggregated, columnar DataFrames required for final UI visualization. Specifically, we will calculate exact daily commit counts over a specific timeline and determine the definitive top committer rankings. Furthermore, to aggressively and effectively protect against punitive GitHub API rate limits and drastically improve the application's perceived responsiveness for the end-user, we will implement a highly robust, file-based local caching mechanism. This intelligent cache will serialize the fully processed Polars DataFrames directly into highly compressed Apache Parquet files on the local disk, rigorously utilizing a Time-to-Live (TTL) expiry strategy to ensure data freshness while absolutely minimizing redundant, slow outbound network calls. By the exact end of this development cycle, the system will efficiently process massive amounts of historical data and serve repeated UI requests almost instantaneously from the local disk drive.

## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
*   (No new external service secrets are technically required for this specific cycle. The existing GitHub authentication token generated from Cycle 01 remains applicable for the broader system.)

### B. System Configurations (`docker-compose.yml`)
*   **Local Storage Directory**: Define a clear, standard environment variable (e.g., `CACHE_DIR=./.cache`) to explicitly specify where the generated Parquet files should be physically stored on the host machine.
    *   **Instruction for Coder**: Ensure this specific directory is created automatically during application startup if it doesn't currently exist, and verify it is strictly excluded from Git version control via the `.gitignore` file to prevent committing binary cache files.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
*   **Mandate Mocking**: All automated tests verifying the complex Polars transformation logic and the file-system caching logic MUST operate entirely independently of the external network. The GitHub API client must be fully and completely mocked. Furthermore, any tests actively interacting with the host file system (for cache writing and validation) MUST utilize Pytest's standard `tmp_path` fixture to guarantee absolute test isolation and prevent tests from polluting the local developer environment or failing randomly due to file permission issues within the automated CI sandbox runner.

## System Architecture
This specific cycle introduces the heavy processing and local caching components, strategically positioned between the data ingestion layer and the future user interface layer.

```text
.
├── src/
│   ├── config.py             # Updated to read the CACHE_DIR variable
│   ├── domain/
│   │   └── models.py         # Reused directly from Cycle 01
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── transformer.py    # Complex Polars DataFrame aggregations
│   │   └── cache_manager.py  # Local Parquet file storage logic
└── tests/
    └── unit/
        ├── test_transformer.py
        └── test_cache_manager.py
```

*   `src/processing/transformer.py`: Designed to consume a potentially massive Python list of `CommitRecord` Pydantic models, convert them rapidly into a unified Polars DataFrame, and execute the exact required aggregations (specifically, group by the exact calendar date, count by specific author name).
*   `src/processing/cache_manager.py`: Meticulously handles the complex file I/O operations. It checks for the physical existence of valid Parquet files based on a strict TTL timestamp, reads them back into memory using Polars, and safely writes newly transformed DataFrames back to the disk.

## Design Architecture
This development cycle focuses intensely on the architectural transition from strictly typed Pydantic domain models to highly optimized, columnar Polars DataFrames.

*   **Polars DataFrames**: Serve as the absolute primary, high-performance data structure for numerical aggregation. We deliberately transition from object-oriented Pydantic models to vectorized, columnar data processing at this specific boundary to achieve vastly superior performance, especially when handling thousands or tens of thousands of individual commits.
*   **`CacheEntry` Metadata**: While the actual numerical data is stored securely in the Parquet format, the cache manager must rigorously track metadata (specifically, the exact timestamp of file creation and the target repository name) to precisely enforce the mathematical TTL logic. This can be efficiently achieved through strict file naming conventions (e.g., `facebook_react_commits_1678886400.parquet`) or a separate, lightweight index file.
*   **Invariants**: The Transformer logic must mathematically guarantee that the final output DataFrames strictly adhere to the exact schema expected by the future UI layer (for example, generating a DataFrame with exactly the columns `['date', 'commit_count']` and another distinct DataFrame with exactly `['author', 'commit_count']`).
*   **Backward Compatibility**: The Apache Parquet format is specifically chosen for caching due to its extreme robustness and advanced schema evolution capabilities, mathematically ensuring that if we add new columns in the future, older binary cache files might still be readable (or at least easily and safely invalidated).

## Implementation Approach
1.  **Dependency Addition**: Add the `polars` library and `pyarrow` (strictly required for Parquet file support within Polars) to the primary project dependencies using `uv`.
2.  **Transformer Logic**: Implement the `transformer.py` module. Write a highly optimized function that takes a list of `CommitRecord`s, instantly creates a Polars DataFrame, extracts the pure date string from the complex datetime object, and performs a vectorized `group_by('date').count()` aggregation. Write a second function to precisely `group_by('author').count().sort('count', descending=True).head(5)`.
3.  **Cache Manager Implementation**: Implement the `cache_manager.py` module. Define a strict mathematical TTL variable (e.g., exactly 3600 seconds). Implement a `save_to_cache(repo_name, df)` function which writes the DataFrame directly to `{CACHE_DIR}/{repo_name}_commits.parquet`. Implement a robust `load_from_cache(repo_name)` function which mathematically checks the physical file's modification time against the defined TTL; if mathematically valid, read and return the DataFrame, otherwise return the Python `None` object.
4.  **Integration**: Ensure the main application logic cleanly and predictably orchestrates checking the local cache first, gracefully falling back to the external API client only if absolutely necessary, and then safely saving the new data back to the local cache.

## Test Strategy

### Unit Testing Approach
Unit tests must rigorously verify the complex mathematical Polars logic and the volatile file system operations in complete, absolute isolation.
*   **Transformer Tests**: Supply a static, hardcoded list of mathematically perfect `CommitRecord` mock objects representing various complex edge case scenarios (e.g., multiple massive commits on the exact same calendar day, exact numerical ties in total commit counts between multiple authors). Mathematically assert that the resulting Polars DataFrames contain the exact expected numerical values and exact column string names.
*   **Cache Manager Tests**: Use Pytest's built-in `tmp_path` fixture extensively. Test successfully writing a massive dummy DataFrame to the isolated temporary path and reading it back into memory perfectly intact. Test the strict TTL logic by manually, programmatically manipulating the physical file's OS-level modification time (using `os.utime`) to successfully simulate an expired, stale cache and mathematically verify that the manager correctly identifies it as totally invalid and returns `None`.

### Integration Testing Approach
Complex integration tests will verify the broader orchestration logic between processing and caching.
*   **Cache Hit/Miss Simulation**: Write an advanced test that completely mocks the external API client. Call the main application extraction flow twice sequentially. Mathematically assert that the mocked API client is called exactly once during the first invocation (proving a Cache Miss scenario), and exactly zero times during the second invocation (proving a Cache Hit scenario), definitively proving that the caching mechanism successfully and completely intercepts redundant outbound network requests.
