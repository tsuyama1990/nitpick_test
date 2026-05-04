# GitHub Repository Analysis Dashboard (PoC)

## Overview
This tool is a Proof of Concept (PoC) for a GitHub Repository Analysis Dashboard. It currently provides a robust ingestion layer capable of securely connecting to the GitHub REST API to extract crucial repository metadata (like stars, forks, and open issues) alongside complete, chronologically ordered commit histories.

## Features
- **Secure API Connectivity**: Authenticates with GitHub using a Personal Access Token via environment variables without hardcoding secrets.
- **Strict Data Validation**: Ensures all fetched data conforms to rigid mathematical contracts (Schemas) using Pydantic, preventing downstream failures due to unexpected API changes.
- **Robust Error Handling**: Gracefully catches and translates common HTTP errors (401 Unauthorized, 404 Not Found, 429 Rate Limit) into highly descriptive Python domain exceptions.
- **Interactive Verification**: Includes a reactive Marimo notebook tutorial to visually confirm extraction and error handling mechanisms.

## Installation
1. Clone the repository.
2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```
3. Set up the environment configuration by copying the example file:
   ```bash
   cp .env.example .env
   ```
4. Open the `.env` file and populate `GITHUB_TOKEN` with your valid GitHub Personal Access Token.

## Usage

### Running Tests
To ensure the system works as expected in your local environment, run the strictly mocked test suite:
```bash
uv run pytest
```

### Running the UAT Tutorial (Marimo Notebook)
To visually test the application against the real GitHub API (requires a valid token in `.env`), run the interactive notebook:
```bash
uv run marimo edit tutorials/UAT_AND_TUTORIAL.py
```

## Structure
- `src/domain_models/`: Contains the strict Pydantic data schemas (`RepositoryMetadata`, `CommitRecord`) and custom exceptions.
- `src/ingestion/`: Houses the `GithubClient` engine for making secure API requests and parsing JSON payloads.
- `src/config.py`: Securely loads required environment variables.
- `tests/`: Isolated, strictly mocked unit tests to mathematically verify the extraction logic.
- `tutorials/`: Marimo notebooks for interactive User Acceptance Testing.
