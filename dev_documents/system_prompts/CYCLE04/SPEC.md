# CYCLE04: Caching Mechanism (Parquet)

## Summary

Cycle 04 focuses on performance and API compliance by implementing the Storage Layer. To prevent exhausting GitHub API rate limits, processed Polars DataFrames will be cached locally to disk. We will serialize the DataFrames to `.parquet` format (leveraging `pyarrow` underneath) due to its binary efficiency. A Time-To-Live (TTL) mechanism will evaluate file modification timestamps to determine whether to serve the cached file or trigger a fresh API fetch.

## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
- Maintained from Cycle 01.

### B. System Configurations (`docker-compose.yml`)
- Maintained from Cycle 01. The `CACHE_TTL_SECONDS` environment variable (default 3600) defined in Cycle 01 must be utilized here.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
- **Mandate Mocking:** File system interactions MUST be tested using Pytest's built-in `tmp_path` fixture. This ensures tests write files to isolated, temporary OS directories rather than polluting the local project workspace. Time-based logic (TTL expiration) MUST be tested by mocking `time.time()`.

## System Architecture

The following directories and files must be implemented or modified:

.
├── src/
│   ├── config/
│   │   └── settings.py
│   └── storage/
│       ├── **__init__.py**
│       └── **cache_manager.py**
└── tests/
    └── **test_storage.py**

## Design Architecture

**CacheManager (`src/storage/cache_manager.py`)**
- Handles serialization and deserialization of Polars DataFrames to/from disk.
- Methods:
  - `save_to_cache(df: pl.DataFrame, cache_key: str) -> None`: Writes the DataFrame to a `.parquet` file named `<cache_key>.parquet` inside a dedicated local directory (e.g., `.cache/`).
  - `load_from_cache(cache_key: str, ttl_seconds: int = 3600) -> pl.DataFrame | None`: Checks if the file exists and its modification time (`st_mtime`) is within the `ttl_seconds` window. Returns the DataFrame if valid, else returns `None`.
- Invariants & Constraints:
  - Path Resolution: Must reliably create the target `.cache` directory if it does not exist using `pathlib.Path`.
  - Date Verification: To resolve Ruff `PTH204` errors, it MUST use `pathlib.Path.stat().st_mtime` instead of `os.path.getmtime(path)`.
- Consumers: The Controller layer.
- Producers: Receives `pl.DataFrame` from the Controller (which gets it from the Transformer).

## Implementation Approach

1. **Init File**: Ensure `src/storage/__init__.py` exists.
2. **Implement Manager**: Create `src/storage/cache_manager.py`.
3. **Directory Setup**: Define a constant `CACHE_DIR = Path(".cache")` and ensure `CACHE_DIR.mkdir(parents=True, exist_ok=True)` is called.
4. **Save Logic**: In `save_to_cache`, construct the file path and use `df.write_parquet(path)`.
5. **Load Logic**: In `load_from_cache`, check `path.exists()`. Get the mod time via `path.stat().st_mtime`. Compare `(time.time() - mod_time)` against `ttl_seconds`. Return `pl.read_parquet(path)` if valid, else `None`.
6. **Linting and Typing**: Execute `uv run ruff check .` and `uv run mypy .`. Ensure `.cache/` is added to `.gitignore`.

## Test Strategy

**Unit Testing Approach (Min 300 words)**
Testing the `CacheManager` requires strict isolation of the file system. We will utilize the Pytest `tmp_path` fixture to dynamically inject a temporary directory path into the `CacheManager` during testing, ensuring no residual `.parquet` files are written to the actual project repository. For the `save_to_cache` method, we will construct a mock Polars DataFrame, execute the save method, and assert that the file is successfully created at the expected temporary path. We will then verify the integrity of the serialization by reading the file back natively and asserting the contents match the original DataFrame.

**Integration Testing Approach (Min 300 words)**
The core integration test focuses on the TTL (Time-To-Live) expiration logic within `load_from_cache`. We will create a test that first saves a valid DataFrame to the temporary cache. Then, using Python's `unittest.mock.patch` on `time.time()`, we will simulate the passage of time. The test will verify two distinct scenarios: First, when querying the cache *before* the TTL has expired (e.g., `simulated_time = original_time + ttl / 2`), the method must return the DataFrame successfully, representing a cache hit. Second, when querying the cache *after* the TTL has expired (e.g., `simulated_time = original_time + ttl * 2`), the method must return `None`, representing a cache miss and signaling the upstream controller to trigger a fresh API fetch.
