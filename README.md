# GitHub Repository Analysis Dashboard PoC

## Overview

This is a Python application that fetches and analyzes GitHub repository metadata and commits. Built primarily using modern, highly strictly-typed Python libraries such as Pydantic to ensure maximum reliability and clarity.

## Features

- **GitHub Ingestion**: Fetches core repository statistics (stars, forks, open issues).
- **Commit History**: Fetches up to 100 recent commits for the repository.
- **Robustness**: Provides secure credential loading without hardcoding secrets and features typed API clients.

## Installation

1. Make sure you have `uv` installed.
2. Clone the repository and navigate to its root.
3. Install dependencies:
   ```bash
   uv sync
   ```
4. Copy `.env.example` to `.env` and fill in your GitHub Personal Access Token:
   ```bash
   cp .env.example .env
   # Edit .env and set GITHUB_TOKEN=your_token
   ```

## Structure

- `src/domain_models/`: Pydantic models acting as the core data types (e.g., `RepositoryMetadata`, `CommitRecord`, configs, and exceptions).
- `src/ingestion/`: The `github_client.py` component to securely make external API calls.
- `tests/unit/`: Comprehensive unit tests ensuring strict typing and HTTP handling without using live external endpoints.

## Usage

You can use the API client locally as follows:

```python
from src.domain_models.config import get_config
from src.ingestion.github_client import GitHubClient

config = get_config()
client = GitHubClient(config)

metadata = client.get_repository_metadata("streamlit", "streamlit")
print(metadata.model_dump())

commits = client.get_commits("streamlit", "streamlit")
print(commits[0].model_dump())
```
