# Cycle 04: Local Caching Implementation Specification

## Summary
This cycle addresses the critical requirement of protecting the external API from excessive requests and ensuring application responsiveness. The objective is to design and implement a robust file-system caching layer specifically tailored for Polars DataFrames. This caching layer acts as an intermediary storage, serializing the results of the heavy Polars transformations (from Cycle 03) into highly efficient Parquet files. By implementing a Time-To-Live (TTL) mechanism based on file system metadata, the application will intelligently serve data from local storage when appropriate, drastically reducing latency and mitigating the risk of encountering GitHub's strict rate limits. This component is foundational for transforming the PoC from a simple script into a resilient, production-oriented application architecture.

## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
This cycle requires no external secrets. However, the cache directory location should be configurable via environment variables to prevent hardcoded paths.
- **Action for Coder:** Instruct the implementation to read a `CACHE_DIR` environment variable, defaulting to `.cache` in the current working directory if not present. This prevents CI/CD pipeline breakage caused by writing to unauthorized locations like `/tmp/`.

### B. System Configurations (`docker-compose.yml`)
No specific configurations are required.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
**MANDATORY INSTRUCTION:** Testing file I/O operations directly against the project directory is strictly forbidden as it pollutes the workspace and leads to flaky tests across parallel runs.
- **Mandate Pytest Fixtures:** The test suite MUST utilize Pytest's built-in `tmp_path` fixture to dynamically generate isolated temporary directories for cache file operations during testing.
- The `LocalCache` class must accept the directory path as an initialization parameter to allow seamless dependency injection of the `tmp_path` during testing.

## System Architecture
The file structure adds the cache module to the processing package. The files explicitly marked in bold represent the targets for creation during this cycle.

```text
.
├── src/
│   ├── config.py
│   ├── processing/
│   │   ├── transformations.py
│   │   └── **cache.py**
└── tests/
    └── **test_cache.py**
```

## Design Architecture
The design centers around the `LocalCache` class within `src/processing/cache.py`. This class encapsulates all knowledge of file paths, serialization formats, and expiration logic.

The initialization of `LocalCache` requires the base directory path and an optional TTL (Time To Live) in seconds (defaulting to 3600 seconds, or 1 hour). During initialization, the class must use `pathlib.Path` to ensure the target directory exists, creating it if necessary (`mkdir(parents=True, exist_ok=True)`).

The class exposes two core methods:
1. `set(self, key: str, df: pl.DataFrame) -> None`: This method handles the storage. The `key` (e.g., `streamlit_streamlit_commits_by_date`) acts as the base file name. The method constructs the full path appending `.parquet` and uses the Polars built-in `df.write_parquet(path)` method to serialize the DataFrame efficiently.
2. `get(self, key: str) -> pl.DataFrame | None`: This method handles retrieval and the critical cache expiration logic. It first checks if the `.parquet` file exists. If not, it immediately returns `None` (a cache miss). If the file exists, it retrieves the file's modification time using `pathlib.Path.stat().st_mtime` (avoiding the outdated `os.path.getmtime`). It then compares this timestamp against the current system time (`time.time()`). If the difference exceeds the configured TTL, the cache is considered stale, and the method returns `None` (forcing a fresh API pull). Only if the file exists and is within the TTL window does the method use `pl.read_parquet(path)` to deserialize and return the DataFrame (a cache hit).

## Implementation Approach
1. **Implement Cache Class:** Create `src/processing/cache.py`. Import `pathlib`, `time`, and `polars as pl`. Define the `LocalCache` class.
2. **Initialization:** Implement `__init__(self, cache_dir: str | Path, ttl_seconds: int = 3600)`. Convert `cache_dir` to a `pathlib.Path` object and call `.mkdir(parents=True, exist_ok=True)`. Store the path and TTL as instance variables.
3. **Implement Storage:** Define `set(self, key: str, df: pl.DataFrame)`. Construct the target file path safely. Use `df.write_parquet()` to save the data.
4. **Implement Retrieval:** Define `get(self, key: str) -> pl.DataFrame | None`. Check `.exists()`. If true, retrieve `st_mtime`. Calculate the age of the file. If `age > self.ttl_seconds`, return `None`. Otherwise, return `pl.read_parquet()`.

## Test Strategy

### Unit Testing Approach
Unit testing is strictly confined to `tests/test_cache.py` using the `tmp_path` fixture.
- **Directory Creation:** Initialize the `LocalCache` with a nested path inside `tmp_path` (e.g., `tmp_path / 'nested' / 'dir'`). Assert that the directory structure is successfully created upon initialization.
- **Cache Hit Workflow:** Create a dummy Polars DataFrame. Save it using `cache.set("test_key", df)`. Immediately retrieve it using `cache.get("test_key")`. Assert that the returned object is a Polars DataFrame and that its contents exactly match the original DataFrame (using Polars' `.equals()` method).
- **Cache Miss (File Not Found):** Call `cache.get("non_existent_key")`. Assert that the return value is exactly `None`.
- **Cache Expiration (TTL Check):** This requires manipulating the file system metadata. Save a dummy DataFrame. Use `os.utime()` (or patch `time.time()`) to artificially backdate the file's modification timestamp so that it appears older than the configured TTL. Call `cache.get("test_key")`. Assert that the method correctly calculates the expiration and returns `None`, rejecting the stale data.
