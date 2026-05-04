# GitHub Repository Analysis Dashboard PoC

A robust Python-based Proof of Concept (PoC) for a GitHub Repository Analysis Dashboard. This tool extracts raw data from the GitHub REST API efficiently while strictly adhering to data contracts and resilience principles.

## Features

- **Robust Ingestion**: Safely connects to the GitHub REST API to pull repository metadata (stars, forks, open issues) and historical commit data.
- **Resilient Error Handling**: Specifically handles GitHub authentication issues, non-existent repositories, and gracefully addresses API rate limiting, ensuring the tool never crashes unexpectedly.
- **Strict Data Contracts**: Enforces the integrity of API responses at the edge utilizing Pydantic models to mathematically validate the payload before further processing.
- **Secure Configuration**: Employs environment-variable-based configuration using `.env` files to safeguard personal access tokens from being inadvertently committed to version control.

## Installation

Ensure you have Python 3.12+ and `uv` installed.

1. Clone the repository and navigate to the project root.
2. Install dependencies via `uv`:
   ```bash
   uv sync
   ```
3. Copy the `.env.example` file to `.env` and fill in your GitHub Personal Access Token:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to set `GITHUB_TOKEN=your_token_here`.*

## Usage

You can use the built-in UAT tutorial notebook (built with Marimo) to interactively verify the core GitHub API ingestion capabilities:

```bash
uv run marimo edit tests/uat/UAT_AND_TUTORIAL.py
```

Or programmatically access it in Python:

```python
from src.config import get_settings
from src.ingestion.github_client import GitHubClient

settings = get_settings()
client = GitHubClient(token=settings.github_token)

metadata = client.fetch_repository_metadata("streamlit/streamlit")
print(f"Repository: {metadata.name}, Stars: {metadata.stars}")
```

## Structure

```
.
├── .env.example              # Template for environment secrets
├── src/
│   ├── config.py             # Configuration loader
│   ├── domain_models/        # Pydantic schemas and domain exceptions
│   └── ingestion/            # Core HTTP Client interacting with GitHub API
└── tests/                    # Unit, integration and UAT tests
```
