# GitHub Repository Analytics Dashboard

A Proof-of-Concept (PoC) dashboard for analyzing GitHub repository data.

## Features
- Fetches and processes core repository metrics (stars, forks, open issues).
- Retrieves and transforms recent commit histories.
- Securely interacts with the GitHub REST API using robust error handling and token management.
- Polars and Streamlit integrations (coming in future cycles).

## Installation

Ensure you have [uv](https://github.com/astral-sh/uv) installed, then run:

```bash
uv sync
```

Set up your environment variables by creating a `.env` file based on the example:
```bash
cp .env.example .env
```
Add your `GITHUB_TOKEN` to the `.env` file.

## Usage

You can initialize the GitHub client and retrieve data programmatically:

```python
from src.domain_models.config import get_settings
from src.ingestion.github_client import GitHubClient

settings = get_settings()
client = GitHubClient(token=settings.GITHUB_TOKEN)

metrics = client.get_repository_metrics("streamlit", "streamlit")
print(metrics)

commits = client.get_recent_commits("streamlit", "streamlit", limit=5)
print(commits)
```

## Structure
- `src/domain_models/`: Contains the Pydantic data schemas, custom domain exceptions, and configuration logic.
- `src/ingestion/`: Contains the HTTP client wrapper for fetching data securely from the GitHub REST API.
- `tests/`: Contains unit tests, UAT notebooks, and mocks to ensure robust execution without making live network calls in CI.
