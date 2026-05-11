# GitHub Repository Analytics Dashboard

## Overview
The GitHub Repository Analytics Dashboard is an application designed to securely fetch, validate, and analyze GitHub repository metrics and commit history.

## Features
- **Secure Configuration Management**: Safely manages external secrets (like `GITHUB_TOKEN`) without hardcoding them into the application, ensuring they are loaded strictly from the environment.
- **Strict Data Validation**: Validates external data retrieved from GitHub APIs securely and prevents downstream failures using rigorous internal typing logic and automated stripping of unexpected API data fields.

## Installation
Ensure you have [uv](https://github.com/astral-sh/uv) installed, then run the following command to synchronize the dependencies:
```bash
uv sync
```

## Usage
1. Copy the environment configuration template:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your GitHub Personal Access Token (`GITHUB_TOKEN=your_token_here`).

You can verify the system's setup and configurations by running the User Acceptance Testing (UAT) script:
```bash
uv run python tests/uat/UAT_AND_TUTORIAL.py
```

## Structure
- `src/domain_models/`: Contains the foundational Pydantic models for configuration (`Settings`), application exceptions, and GitHub schema data representations (`RepositoryMetrics`, `CommitAuthor`, `CommitData`, `CommitItem`).
- `tests/`: Contains the automated test suites, demonstrating functionality via Unit tests (`tests/unit`), Integration tests (`tests/e2e`), and User Acceptance Testing (`tests/uat/`).
