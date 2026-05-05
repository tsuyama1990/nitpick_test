# GitHub Repository Analysis Dashboard PoC

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A high-performance, strictly typed Proof of Concept (PoC) for analyzing GitHub repositories. This system ingests live data from the GitHub REST API, processes commit histories at lightning speed using Polars, and presents interactive visualizations via Streamlit, all while enforcing strict architectural boundaries and security best practices.

## Key Features

*   **Live API Integration**: Connects directly to the GitHub REST API to fetch real-time repository metadata and commit histories.
*   **High-Performance Aggregation**: Leverages `polars` to transform and aggregate thousands of commit records efficiently, calculating daily trends and identifying top contributors.
*   **Intelligent Local Caching**: Implements a Time-to-Live (TTL) Parquet-based caching mechanism to drastically reduce API latency and completely prevent rate-limiting penalties.
*   **Zero-Exposure Security**: Strictly enforces environment-variable-only credential management (`dotenv` and `pydantic-settings`), ensuring GitHub Personal Access Tokens are never hardcoded, leaked in logs, or exposed in the UI.
*   **Robust Error Handling**: Domain-specific exceptions intercept API failures (e.g., 404 Not Found, 403 Rate Limit), translating them into user-friendly UI alerts without crashing the application.

## Architecture Overview

The system is built on a tiered architecture ensuring separation of concerns:
1.  **Ingestion Layer**: Safely interacts with the GitHub API, parses JSON, and validates data using strict Pydantic models.
2.  **Processing & Storage Layer**: Aggregates data using Polars and manages the local disk cache via Parquet.
3.  **Presentation Layer**: A lightweight Streamlit UI that orchestrates the backend and renders charts.

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

### Process Commits Locally

The system is able to fetch records using the HTTP client, store the cached responses in highly-compressed Parquet files, and quickly transform them using Polars avoiding redundant API calls.

### Run the Interactive Tutorial

To understand the system's inner workings and validate the data flow step-by-step, including the new caching and Polars transformation flows:

```bash
uv run marimo edit tests/uat/c02_uat.py
```

## Development Workflow

This project adheres to strict quality standards. Ensure you run the following commands before submitting code:

*   **Run Linters & Formatting (Ruff)**:
    ```bash
    uv run ruff check .
    uv run ruff format .
    ```

*   **Run Type Checking (Mypy)**:
    ```bash
    uv run mypy src tests
    ```

*   **Run Tests (Pytest)**:
    ```bash
    # Run isolated unit tests (Mocked API)
    uv run pytest tests/unit

    # Run full test suite with coverage
    uv run pytest
    ```

## Project Structure

```text
.
├── .env.example
├── pyproject.toml
├── src/
│   ├── cache_manager.py # Parquet Cache manager
│   ├── transformer.py   # Polars Transformer
│   ├── domain_models/   # Pydantic Models & Exceptions
├── tests/
│   ├── unit/
│   └── uat/             # Marimo UAT notebooks
```

## License

This project is licensed under the MIT License.