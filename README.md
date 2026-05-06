# GitHub Analytics Dashboard

## Overview

The GitHub Analytics Dashboard is a simplified system for extracting and analyzing GitHub repository data, such as basic metrics (stars, forks) and commit histories. This foundation provides securely typed data ingestion tools designed to safely process complex and deeply nested payloads returned from the GitHub REST API.

## Features

- **Strict Environment Configuration**: Ensures robust token management, preventing the application from initializing without necessary API secrets, and securely managing API limits.
- **Robust Schema Validation**: Employs Pydantic models with `extra="ignore"` and pre-validators to seamlessly ingest and flatten complex, multi-level JSON payloads from GitHub APIs directly into manageable Python objects.
- **Fail-Safe Design**: Strictly prevents loading arbitrary environmental properties into configurations.

## Installation

Ensure you have Python 3.12+ installed, along with `uv` for dependency management.

```bash
# Clone the repository
# git clone <your-repo-url>
# cd <your-repo-directory>

# Install all dependencies and setup the virtual environment
uv sync

# Setup your environment variables
cp .env.example .env
```
Edit `.env` and add your `GITHUB_TOKEN`.

## Usage

This project currently provides strict foundational domains and configuration validation utilities. Here is a brief snippet on how to access the typed settings and use the Domain models.

```python
from src.config.settings import get_settings
from src.domain_models import RepositoryInfo, CommitData

# Load and validate settings safely
settings = get_settings()

# Example JSON mapping (simulating GitHub API payload)
repo_payload = {
    "name": "streamlit",
    "owner": "streamlit",
    "stargazers_count": 30000,
    "forks_count": 3000,
    "open_issues_count": 250,
    "ignore_this_extra_field": 1234
}

# The payload will automatically drop the unknown fields
repo = RepositoryInfo(**repo_payload)
print(f"Loaded Repository: {repo.name} with {repo.stargazers_count} stars")
```

For executing the UAT notebook and viewing interactive validation scenarios:
```bash
uv run marimo edit tutorials/UAT_AND_TUTORIAL.py
```

## Structure

```
.
├── .env.example        # Template for secrets
├── src/                # Main application source
│   ├── config/         # System settings and environment parsing
│   └── domain_models/  # Pydantic schemas for typing GitHub JSON
├── tests/              # Extensive validation suite for Unit testing
└── tutorials/          # UAT and demo scripts
```
