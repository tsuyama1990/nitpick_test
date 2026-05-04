# GitHub Repository Analysis Dashboard PoC

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A high-performance, strictly typed Proof of Concept (PoC) for analyzing GitHub repositories. This initial ingestion system safely and securely extracts live metadata and commit history data from the GitHub REST API, while enforcing strict architectural boundaries and security best practices.

## Features

*   **Live API Integration**: Connects directly to the GitHub REST API to fetch real-time repository metadata and commit histories.
*   **Zero-Exposure Security**: Strictly enforces environment-variable-only credential management (`dotenv`), ensuring GitHub Personal Access Tokens are never hardcoded or leaked in logs.
*   **Robust Error Handling**: Domain-specific exceptions intercept API failures (e.g., 404 Not Found, 403 Rate Limit), translating them into predictable errors.
*   **Strict Type Contracts**: Heavily utilizes Pydantic to ensure all data precisely matches mathematical contracts and architectural expectations.

## Installation

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

### Basic Python Usage

You can use the ingestion layer directly from Python to fetch repository metadata and the latest 100 commits:

```python
from src.ingestion.github_client import GitHubClient

# The client automatically picks up GITHUB_TOKEN from your .env
client = GitHubClient()

# Fetch repository details
repo = client.fetch_repository_metadata("streamlit", "streamlit")
print(f"{repo.name} has {repo.stargazers_count} stars.")

# Fetch the last 100 commits
commits = client.fetch_commit_history("streamlit", "streamlit")
for commit in commits[:5]:
    print(f"Commit {commit.sha[:7]} by {commit.author_name} at {commit.date}")
```

### Run the Interactive Tutorial

To understand the system's inner workings and execute an interactive User Acceptance Test (UAT):

```bash
uv run marimo edit tutorials/UAT_AND_TUTORIAL.py
```

## Structure

```text
.
├── .env.example
├── pyproject.toml
├── src/
│   ├── config.py
│   ├── domain_models/ # Pydantic Models & Exceptions
│   └── ingestion/     # Core GitHub API Client
├── tests/
│   ├── e2e/           # Live API execution testing
│   ├── uat/           # User Acceptance Testing scripts
│   └── unit/          # Isolated mocked tests
└── tutorials/         # Marimo UAT notebooks
```

## License

This project is licensed under the MIT License.
