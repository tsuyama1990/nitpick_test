# GitHub Repository Analytics Dashboard (Processing Engine Update)

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A modern, high-performance dashboard for analysing GitHub repository data. This tool currently features a robust data processing engine that leverages strictly typed Pydantic models and Polars to securely validate and aggregate GitHub commit data at lightning speeds.

## Key Features

- **Strict Schema Validation:** Utilizes `Pydantic` with `extra="forbid"` to ensure that incoming API payloads strictly conform to expectations, rejecting malformed data before it pollutes the system.
- **High-Performance Aggregation:** Leverages `Polars` for zero-copy, lightning-fast tabular data transformations. It aggregates commit counts by date and accurately determines top committers using deterministic stable sorting algorithms.
- **Secure Configuration Management:** Manages sensitive API credentials securely via `pydantic-settings`, enforcing environment configuration without hardcoding secrets.
- **Test-Driven Architecture:** Backed by a comprehensive suite of isolated unit tests and User Acceptance Testing (UAT) scripts to ensure reliable, mathematically correct aggregations without risky external network calls.

## Prerequisites

- **Python:** 3.12 or newer.
- **Package Manager:** `uv` is required for dependency and environment management.

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install dependencies using `uv`:**
   ```bash
   uv sync
   ```

3. **Configure Environment Variables:**
   Create a `.env` file containing your GitHub token (or configure it in your CI pipeline):
   ```bash
   echo "GITHUB_TOKEN=your_token_here" > .env
   ```

## Usage

**Running the Data Processor Programmatically:**

The core processing functions can be imported and executed in your Python scripts:

```python
import polars as pl
from src.processing.transformations import aggregate_commits_by_date, get_top_committers

# Example raw data (e.g., fetched from GitHub)
raw_commits = [
    {"commit": {"author": {"name": "Alice", "date": "2023-01-01T10:00:00Z"}}},
    {"commit": {"author": {"name": "Bob", "date": "2023-01-02T14:00:00Z"}}}
]

# Aggregate commits by date
df_dates = aggregate_commits_by_date(raw_commits)
print(df_dates)

# Get top committers
df_top = get_top_committers(raw_commits, top_n=5)
print(df_top)
```

**Running Tests and UAT:**

To verify the deterministic nature of the sorting and the strictness of the schema, you can run the test suite:

```bash
# Run unit and integration tests
uv run pytest

# Execute UAT scripts
uv run python tests/uat/uat_script.py
```

## Project Structure

```text
.
├── .gitignore           # Ignored files (caches, envs, etc)
├── pyproject.toml       # Dependency and tool configuration
├── README.md            # Project documentation
├── src/
│   ├── domain_models/   # Pydantic schemas, manifest, and settings config
│   └── processing/      # Polars data transformations engine
└── tests/
    ├── uat/             # User Acceptance Test scripts
    └── unit/            # Unit tests for schemas and logic
```

## License

MIT License
