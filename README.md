# GitHub Repository Analysis PoC

## Overview
This application provides a simple Proof of Concept (PoC) for analyzing GitHub repositories. It fetches essential metrics (such as stars, forks, and open issues) and recent commit history directly from the live GitHub REST API. This tool acts as the foundational data ingestion layer for future dashboarding and analytics.

## Features
- **Live GitHub API Integration:** Fetches repository metrics and up to 100 recent commits using `httpx`.
- **Resilient Network Communication:** Translates raw HTTP status codes (like 404 or 403) into semantic domain exceptions.
- **Secure Authentication:** Utilizes a Personal Access Token (`GITHUB_TOKEN`) loaded from a `.env` file to maximize rate limits without hardcoding credentials.
- **Strict Data Modeling:** Employs `Pydantic` to enforce rigorous schemas on the fetched data, preparing it for subsequent transformation.

## Installation
Ensure you have `uv` installed, then synchronize the dependencies:

```bash
uv sync
```

## Configuration
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and add your GitHub Personal Access Token:
   ```env
   GITHUB_TOKEN=your_actual_token_here
   ```

## Usage
You can utilize the `GitHubClient` in your own Python scripts.

```python
from src.ingestion.github_client import GitHubClient

client = GitHubClient()

# Fetch repository metrics
try:
    metrics = client.get_repository_metrics("streamlit", "streamlit")
    print(f"Stars: {metrics['stargazers_count']}")
except Exception as e:
    print(f"Error: {e}")

# Fetch recent commits
commits = client.get_recent_commits("streamlit", "streamlit")
print(f"Total recent commits fetched: {len(commits)}")
```

## Structure
- `src/domain_models/`: Contains configuration schemas and custom domain exceptions.
- `src/ingestion/`: Houses the `GitHubClient` for data retrieval.
- `tests/`: Includes unit tests with mocked API responses to ensure robustness without hitting rate limits.
