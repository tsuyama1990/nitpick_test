# GitHub Repository Analysis Dashboard

## Overview
A secure, strictly typed Python ingestion client to interact with the GitHub REST API. This foundational layer securely fetches and strongly validates repository metadata and commit histories into Pydantic models.

## Features
- **Secure Authentication**: Loads GitHub tokens strictly from environment variables.
- **Strict Data Validation**: Utilizes Pydantic to ensure all ingested data strictly matches expected schemas.
- **Robust Error Handling**: Automatically catches and translates external API errors (e.g., rate limits, missing repos) into descriptive Python domain exceptions.
- **Automatic Pagination Control**: Limits data extraction natively to recent records for optimal performance.

## Installation

1. Make sure you have `uv` installed.
2. Clone the repository.
3. Setup the local virtual environment and install dependencies:
   ```bash
   uv sync
   ```
4. Copy `.env.example` to `.env` and fill in your `GITHUB_TOKEN`:
   ```bash
   cp .env.example .env
   ```

## Usage

Here is a basic example of how to use the ingestion client to fetch data from GitHub:

```python
from src.ingestion import GitHubClient
from src.domain_models import RepositoryNotFoundError, AuthenticationError

try:
    # Client will automatically load token from the environment variable / .env file
    client = GitHubClient()

    # Fetch repository metadata
    metadata = client.get_repository_metadata(owner="streamlit", repo="streamlit")
    print(f"Repository {metadata.repo_name} has {metadata.star_count} stars.")

    # Fetch the last 10 commits
    commits = client.get_commits(owner="streamlit", repo="streamlit", limit=10)
    for commit in commits:
        print(f"Commit {commit.sha} by {commit.author_name} at {commit.date}")

except RepositoryNotFoundError:
    print("The repository was not found!")
except AuthenticationError:
    print("Invalid or expired GitHub Token!")
```

## Structure
- `src/config.py`: Environment and configuration management.
- `src/domain_models/`: Pydantic domain schemas and core exception classes.
- `src/ingestion/`: Core GitHub REST API client.
- `tests/`: Automated unit, integration, and E2E tests.
- `tutorials/`: Marimo notebooks for user acceptance testing and tutorials.
