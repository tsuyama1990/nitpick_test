# GitHub Repository Analysis Dashboard PoC

## Overview
This application is a Proof of Concept (PoC) designed to extract and analyze data from GitHub repositories using the GitHub REST API. It strictly validates repository metadata (such as stars, forks, and open issues) and commit history, creating a reliable foundation for data transformation and visualization.

## Features
- **Secure Authentication**: Connects securely to the GitHub REST API using a provided Personal Access Token, protecting sensitive credentials.
- **Strict Data Validation**: Leverages Pydantic schemas to validate real-time API responses directly, ensuring high reliability and predictability of data forms.
- **Data Ingestion**: Programmatically fetches core repository metadata and retrieves up to the latest 100 commits.
- **Robust Error Handling**: Distinctly handles invalid repositories, unauthorized access, and API rate limiting without abruptly crashing the environment.

## Installation
1. Clone this repository to your local environment.
2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```
3. Copy the example environment file and add your GitHub Personal Access Token:
   ```bash
   cp .env.example .env
   # Open .env and add your valid GITHUB_TOKEN
   ```

## Usage
Currently, the extraction capabilities are available through the API client. You can use it in your own scripts as shown below:

```python
from src.ingestion.github_client import GitHubClient
from src.config import get_settings

# Load settings from the .env file
settings = get_settings()

# Initialize the client
client = GitHubClient(token=settings.github_token)

# Fetch repository metadata
repo_metadata = client.get_repository_metadata("streamlit/streamlit")
print(f"Repository: {repo_metadata.repo_name}")
print(f"Stars: {repo_metadata.star_count}")

# Fetch the recent commits
recent_commits = client.get_recent_commits("streamlit/streamlit", limit=10)
for commit in recent_commits:
    print(f"{commit.author_name}: {commit.commit_hash} on {commit.timestamp}")
```

## Structure
```
.
├── src/
│   ├── config.py             # Singleton configuration loader handling environment variables.
│   ├── domain_models/        # Pydantic schemas defining exactly how our data looks.
│   └── ingestion/            # Core logic executing HTTP requests using httpx.
└── tests/
    ├── e2e/                  # Live testing scripts hitting real endpoints.
    ├── uat/                  # Interactive tutorial and UAT via Marimo Notebooks.
    └── unit/                 # Heavily mocked strict mathematical verifications.
```
