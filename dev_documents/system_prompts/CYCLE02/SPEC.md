# Cycle 02 Specification: Data Transformation and Local Caching

## 1. Overview
Cycle 2 focuses on processing the raw JSON data extracted from the GitHub API and preparing it for final presentation. The processed results are efficiently aggregated using `polars` and aggressively cached locally to minimize redundant network requests and avoid API rate limits.

## 2. Core Components

### 2.1 Pydantic Domain Models (`src/domain_models/github.py`)
To ensure robust validation of API data and enforce strict adherence to our structural requirements without boilerplate code, the architecture adopts a DRY inheritance structure based on `StrictBaseModel`.

- **`StrictBaseModel`**:
  - Extends Pydantic's `BaseModel`.
  - Configures `model_config = ConfigDict(extra="forbid")`.
  - Implements a generic `@model_validator(mode="before")` that purges any top-level key not defined in the class schema prior to Pydantic's native validation.
- **Derived Models**: `GitHubRepository`, `GitHubCommitAuthor`, `GitHubCommitDetails`, and `GitHubCommit`.
  - Inherit directly from `StrictBaseModel`.
  - `GitHubRepository` additionally overrides the `model_validator` to flatten nested `owner` login information before passing processing back to `super().filter_extra_fields()`.

### 2.2 Local Caching Layer (`src/storage/cache_manager.py`)
The system employs a fast, disk-backed cache.

- **Storage Method**: DataFrames are securely persisted as `.parquet` files.
- **Cache Location**: Target directories are defined by a `CACHE_DIR_NAME` setting (default `github_dashboard`). This path is dynamically configurable via the `CACHE_DIR` environment variable to support local `.cache/` scoping.
- **TTL Strategy**:
  - Each item caches for a configurable default TTL (3600 seconds).
  - Validation calculates age using `.stat().st_mtime` to prevent arbitrary date-time parser overhead.
  - Expired files are lazily unlinked upon load attempts using safe `contextlib.suppress(OSError)` patterns.

### 2.3 Data Transformation (`src/transformation/data_processor.py`)
All aggregation pipelines use vectorized `polars` logic for ultimate performance.
- **`commits_per_day`**: Projects `author_date` from ISO strings down to pure `pl.Date`, groups by this date, and aggregates the count of commits. Sorts ascending.
- **`top_committers`**: Groups by `author_name`, aggregates by count, and limits to the top 5 contributors.

## 3. Interfaces and Expectations
- Fully typed data ingestion relying on `StrictBaseModel`.
- High efficiency with pure Polars implementations.
- Zero unnecessary web requests via robust cache reloading behavior.
