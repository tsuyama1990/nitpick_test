# GitHub Repository Analytics Dashboard

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A modern, high-performance Proof-of-Concept (PoC) dashboard for analysing GitHub repository data. This application securely connects to the GitHub REST API to fetch, process, cache, and visualise repository metrics and commit histories, offering an intuitive interface built entirely in Python.

## Key Features

- **Automated Data Ingestion:** Seamlessly connects to the GitHub REST API with robust error handling and strict rate limit protection.
- **High-Performance Aggregation:** Leverages `Polars` for zero-copy, lightning-fast tabular data transformations.
- **Zero-Config Local Caching:** Implements an intelligent, Time-To-Live (TTL) based local Parquet file cache to drastically reduce API latency and respect network constraints.
- **Interactive Visualisations:** Provides a clean, responsive web interface using `Streamlit` to display core repository KPIs and interactive charts of developer activity over time.
- **Type-Safe Architecture:** Built with strict `Pydantic` domain models and rigorous MyPy static typing, ensuring data integrity from network response to frontend rendering.

## Current Verified Capabilities

- **Local Data Caching:** Implemented and thoroughly verified local file-system caching mechanism specifically tailored for Polars DataFrames using efficient Parquet storage.
- **Smart Data Invalidation:** Includes a Time-To-Live (TTL) feature to automatically invalidate stale data, preventing external API overload and respecting GitHub rate limits.

## Installation

1. **Install dependencies using `uv`:**
   ```bash
   uv sync
   ```

2. **Configure Environment Variables:**
   Copy the example environment file and populate it with your GitHub Personal Access Token.
   ```bash
   cp .env.example .env
   # Edit .env and set GITHUB_TOKEN=your_token_here
   ```

## Usage

**Run caching logic:**
To test the caching utilities directly in your Python code, you can use the `LocalCache` module in `src.processing.cache`:

```python
import polars as pl
from src.processing.cache import LocalCache

# Setup cache
cache = LocalCache(cache_dir=".cache", ttl_seconds=3600)
df = pl.DataFrame({"a": [1, 2, 3]})

# Save to cache
cache.set("my_key", df)

# Retrieve from cache
retrieved_df = cache.get("my_key")
```

## Structure

```text
.
├── .env.example         # Template for environment variables
├── pyproject.toml       # Dependency and linter configuration
├── README.md            # Project documentation
├── src/
│   ├── app.py           # Streamlit frontend application
│   ├── config.py        # Pydantic-based configuration management
│   ├── domain/          # Pydantic schemas and custom exceptions
│   ├── ingestion/       # GitHub API client
│   └── processing/      # Orchestrator, Polars transformations, and Cache
└── tests/
    ├── uat/             # Scripts for user experience and testing
    └── ...              # Unit and integration tests
```

## License

MIT License



## Local Caching

- **Local Data Caching:** Implemented and thoroughly verified local file-system caching mechanism specifically tailored for Polars DataFrames using efficient Parquet storage.
- **Smart Data Invalidation:** Includes a Time-To-Live (TTL) feature to automatically invalidate stale data, preventing external API overload and respecting GitHub rate limits.
