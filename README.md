# GitHub Repository Data Extractor

A secure and robust Python-based ingestion tool designed to extract essential repository metadata and chronological commit histories from the GitHub REST API.

## Features

- **Strict Type Validation**: Leverages Pydantic schemas to ensure all retrieved data rigidly adheres to expected formats.
- **Resilient Error Handling**: Safely intercepts common API failures—including invalid credentials, 404 Not Found, and rate-limiting—translating them into descriptive Python exceptions.
- **Environment Isolation**: Designed with security in mind, it reads authentication configurations dynamically using `python-dotenv`, avoiding hardcoded secrets.
- **Ready for Processing**: Produces strongly typed `RepositoryMetadata` and `CommitRecord` models, perfectly prepared for further aggregations or dataframe transformations.

## Installation

Ensure you have a modern version of Python (>=3.12) installed. We recommend using `uv` for lightning-fast dependency management.

```bash
# Clone the repository
git clone <your-repo-url>
cd <repo-name>

# Install the required dependencies securely
uv sync
```

## Setup

Before executing the tool, you must configure your secure API credentials:

1. Copy the provided environment template:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and assign your personal GitHub Access Token to `GITHUB_TOKEN`.

## Usage

You can use the `GithubClient` in your own scripts as follows:

```python
from src.config import get_config
from src.ingestion.github_client import GithubClient

# Safely load the environment variables
config = get_config()
client = GithubClient(config)

try:
    # Retrieve fundamental repository metrics
    metadata = client.fetch_repository_metadata(owner="streamlit", repo="streamlit")
    print(f"Repo: {metadata.name}, Stars: {metadata.stargazers_count}")

    # Retrieve the latest commits
    commits = client.fetch_latest_commits(owner="streamlit", repo="streamlit", limit=5)
    for commit in commits:
        print(f"[{commit.date}] {commit.author_name}: {commit.sha}")
except Exception as e:
    print(f"An error occurred: {e}")
```

## Project Structure

```text
.
├── src/
│   ├── config.py                   # Secure environment configuration using Pydantic Settings
│   ├── domain_models/              # Core Pydantic contracts and custom Exception definitions
│   └── ingestion/
│       └── github_client.py        # Core, resilient HTTP client connecting to GitHub
├── tests/                          # Extensive mock-based unit and live E2E tests
└── tutorials/                      # Interactive usage scenarios (Marimo Notebooks)
```
