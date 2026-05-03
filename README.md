# GitHub Repository Analysis Dashboard (Ingestion Layer)

## Overview
This tool is a Python-based utility that securely extracts comprehensive repository metadata and commit history from the official GitHub REST API. It serves as the high-performance foundation for analyzing repository trends, prioritizing data structure strictness and error resilience without exposing sensitive credentials.

## Features
- **Secure Authentication**: Uses environment variables to protect GitHub Personal Access Tokens.
- **Robust Ingestion**: Retrieves repository metrics (stars, forks, open issues) and chronological commit records.
- **Strong Typing**: Implements rigorous Pydantic-based mathematical validation ensuring data fidelity right from the edge API call.
- **Error Handling**: Gracefully handles API failures (like invalid repositories and token expirations) using descriptive custom exceptions.
- **Performance Optimized**: Configured with strict timeouts and designed to fetch required data rapidly using standard Python HTTP libraries.

## Installation
Ensure you have `uv` installed, then synchronize the environment:
```bash
uv sync
```

## Configuration
Before running any scripts, you must configure your local environment:
1. Copy the example configuration:
   ```bash
   cp .env.example .env
   ```
2. Edit the `.env` file and insert your valid GitHub Personal Access Token next to `GITHUB_TOKEN=`.

## Usage
Currently, the tool can be invoked programmatically via its client interface:

```python
from src.config import get_github_token
from src.ingestion.github_client import GitHubClient

# Securely load the token
token = get_github_token()

# Initialize the API client
client = GitHubClient(token=token)

# Fetch Metadata
repo_info = client.fetch_repository_metadata("streamlit/streamlit")
print(f"Repository: {repo_info.name}, Stars: {repo_info.stargazers_count}")

# Fetch the latest commits
commits = client.fetch_commits("streamlit/streamlit", limit=5)
for commit in commits:
    print(f"Commit {commit.sha} by {commit.author_name} at {commit.date}")
```

## Structure
- `src/domain/`: Core Pydantic models (`RepositoryMetadata`, `CommitRecord`) and custom domain exceptions.
- `src/ingestion/`: The robust `GitHubClient` handling all HTTP requests.
- `tests/`: Comprehensive unit and User Acceptance Testing (UAT) scripts.
