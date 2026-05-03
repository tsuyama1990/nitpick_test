# GitHub Repository Analysis Ingestion Engine

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A highly secure, strictly typed data ingestion engine for connecting to the official GitHub REST API. This tool acts as the foundational layer to fetch robust repository metadata and complete commit histories for downstream analysis.

## Key Features

*   **Live API Integration**: Securely connects to the GitHub REST API to fetch target repository metadata and up to 100 recent commits.
*   **Zero-Exposure Security**: Strictly enforces environment-variable-only credential management (`dotenv`), ensuring GitHub Personal Access Tokens are never hardcoded or leaked in error messages.
*   **Strict Mathematical Contracts**: Relies on Pydantic to ensure all ingested JSON perfectly matches predefined data models, catching anomalies right at the edge.
*   **Robust Error Handling**: Safely intercepts specific HTTP API errors (401, 403, 404, 429) and translates them into actionable domain exceptions (`AuthenticationError`, `RateLimitError`, `RepositoryNotFoundError`).
*   **Timebound Requests**: Configured with strict network timeouts to ensure extraction processes never infinitely hang.

## Prerequisites

*   Python >= 3.12
*   [`uv`](https://docs.astral.sh/uv/) (Extremely fast Python package installer and resolver)
*   A GitHub Personal Access Token (for Live API access)

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install dependencies using `uv`:**
    ```bash
    uv sync
    ```

3.  **Configure Environment Variables:**
    Copy the example environment file and add your GitHub token.
    ```bash
    cp .env.example .env
    # Edit .env and insert your actual token at GITHUB_TOKEN=
    ```

## Usage

### Run the Interactive Client Tutorial

To directly experiment with the ingestion layer, simulate authentications, and view strictly typed extraction responses in an interactive environment, run:

```bash
uv run marimo edit tutorials/UAT_AND_TUTORIAL.py
```

### Direct Python Example

```python
from src.config import Settings
from src.ingestion.github_client import GitHubClient

# Securely loads the GITHUB_TOKEN from your local .env file
settings = Settings()
client = GitHubClient(settings=settings)

# Extract core metadata (returns a strictly validated RepositoryMetadata model)
metadata = client.get_repository_metadata("streamlit", "streamlit")
print(f"Repo Stars: {metadata.star_count}")

# Fetch recent commits (returns a list of strictly validated CommitRecord models)
commits = client.get_recent_commits("streamlit", "streamlit")
print(f"Latest commit by: {commits[0].author_name}")
```

## Development Workflow

This project adheres to rigorous quality standards:

*   **Run Linters & Formatting (Ruff)**:
    ```bash
    uv run ruff check .
    uv run ruff format .
    ```

*   **Run Type Checking (Mypy)**:
    ```bash
    uv run mypy src tests
    ```

*   **Run Automated Tests (Pytest)**:
    ```bash
    # Run isolated unit tests (Mocked API calls)
    uv run pytest tests/unit

    # Run all tests with coverage reports
    uv run pytest
    ```

## Project Structure

```text
.
├── .env.example
├── pyproject.toml
├── src/
│   ├── config.py              # Zero-exposure configuration loading
│   ├── domain_models/         # Strict Pydantic Models & Core Exceptions
│   └── ingestion/             # Secure GitHub API Client Engine
├── tests/
│   ├── unit/                  # Mocked tests targeting isolation
│   └── e2e/                   # Integration stubs (require real tokens)
└── tutorials/                 # Marimo UAT testing and tutorials
```

## License

This project is licensed under the MIT License.
