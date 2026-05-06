# GitHub Repository Analysis Dashboard PoC

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A high-performance, strictly typed Proof of Concept (PoC) for analyzing GitHub repositories. This system ingests live data from the GitHub REST API, processing it locally with high efficiency.

## Key Features

*   **Live API Integration**: Connects directly to the GitHub REST API to fetch real-time repository metadata and commit histories.
*   **Zero-Exposure Security**: Strictly enforces environment-variable-only credential management (`dotenv`), ensuring GitHub Personal Access Tokens are never hardcoded, leaked in logs, or exposed in the UI.
*   **Robust Error Handling**: Domain-specific exceptions intercept API failures (e.g., 404 Not Found, 403 Rate Limit), translating them safely to the rest of the application.

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

### Run the Interactive Tutorial

To understand the system's inner workings and validate the data flow step-by-step:

```bash
uv run marimo edit tests/uat/UAT_AND_TUTORIAL.py
```

## Project Structure

```text
.
├── .env.example
├── pyproject.toml
├── src/
│   ├── config.py
│   ├── domain_models/ # Pydantic Models & Exceptions
│   └── ingestion/     # GitHub API Client
├── tests/
│   ├── e2e/           # Live E2E tests
│   ├── uat/           # Marimo UAT notebooks
│   └── unit/          # Mocked Unit tests
└── README.md
```

## License

This project is licensed under the MIT License.
