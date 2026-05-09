# GitHub Repository Analytics Dashboard

A simple and powerful tool built to retrieve and transform GitHub repository analytics locally. It leverages the robust Polars library to process data seamlessly.

## Features

- **Strict Validation:** Guarantees structural integrity for ingested GitHub repository metrics and commits.
- **High-Performance Data Transformation:** Uses `polars` to quickly identify the top 5 committers and calculate the number of commits per day.
- **Local Parquet Caching:** Features a fast local Cache Manager that serializes DataFrame outputs into Parquet files, implementing a built-in TTL caching layer to manage API rate limits efficiently.
- **Robust Type Safety:** Fully typed across all configuration and structural bounds.

## Installation

Ensure you have Python 3.12+ and `uv` installed.

1. Clone the repository and navigate to the project directory.
2. Create your `.env` configuration file by copying the template:
   ```bash
   cp .env.example .env
   ```
   Add your GitHub token to the `.env` file (e.g. `GITHUB_TOKEN=ghp_...`).
3. Install dependencies and synchronize your environment:
   ```bash
   uv sync
   ```

## Usage

You can use the modules directly in your Python code:

```python
from src.transformation.data_processor import DataProcessor
from src.storage.cache_manager import CacheManager
import polars as pl

# Mocking some input DataFrame
df = pl.DataFrame({
    "author_name": ["Alice", "Bob", "Alice"],
    "author_date": ["2023-10-01T10:00:00Z", "2023-10-01T12:00:00Z", "2023-10-02T10:00:00Z"]
})

# Get commits per day
daily_commits = DataProcessor.commits_per_day(df)
print(daily_commits)

# Get top committers
top_committers = DataProcessor.top_committers(df, limit=2)
print(top_committers)

# Save and load with the CacheManager
cache = CacheManager(cache_dir_name="github_cache", ttl_seconds=3600)
cache.save("top_committers", top_committers)
loaded = cache.load("top_committers")
```

### Running Tests

Execute the unit tests to ensure everything functions perfectly:
```bash
uv run pytest
```

## Structure

- `src/domain_models/`: Enforces strict schema validations for GitHub components and system settings.
- `src/transformation/`: Logic pipelines using Polars to extract meaningful insights.
- `src/storage/`: Parquet caching solutions.
- `tests/`: End-to-end user tests alongside modular unit tests to maintain over 85% coverage threshold.
