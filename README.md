# GitHub Repository Analysis Dashboard (PoC)

## Title & Overview
This project provides a simple GitHub repository analysis system. It fetches repository metadata and commit history using the live GitHub REST API. Future updates will introduce data processing and a web dashboard via Streamlit for user-friendly visualizations.

## Features
- **Live GitHub API Integration:** Fetches accurate repository information such as stars, forks, and open issues.
- **Commit History Retrieval:** Gathers recent commits and seamlessly extracts author details and timestamps.
- **Robust Error Handling:** Safely manages authentication issues, non-existent repositories, and API rate limits.
- **Secure Configuration:** Ensures personal access tokens are not leaked and are securely loaded from a `.env` file.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd <repository-directory>

# Copy the example environment file and add your token
cp .env.example .env
# Edit .env and set GITHUB_TOKEN=your_personal_access_token

# Sync dependencies using uv
uv sync
```

## Usage

```python
from src.ingestion import GitHubClient

client = GitHubClient()

# Fetch Repository Information
repo_info = client.fetch_repository_info("streamlit", "streamlit")
print(f"Stars: {repo_info.stargazers_count}")
print(f"Forks: {repo_info.forks_count}")
print(f"Open Issues: {repo_info.open_issues_count}")

# Fetch Recent Commits
commits = client.fetch_recent_commits("streamlit", "streamlit", limit=5)
for commit in commits:
    print(f"Author: {commit.author_name}, Date: {commit.date}")
```

## Structure
- `src/config/`: Configuration settings and secure loading methods.
- `src/domain_models/`: Validated Pydantic models for repository data.
- `src/ingestion/`: API Client modules to retrieve raw data securely.
- `tests/`: Pytest suite covering unit and exception test cases.
