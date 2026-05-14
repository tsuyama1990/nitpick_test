# GitHub Repository Analytics Dashboard

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A modern, high-performance Proof-of-Concept (PoC) dashboard for analysing GitHub repository data. This application securely connects to the GitHub REST API to fetch, process, cache, and visualise repository metrics and commit histories, offering an intuitive interface built entirely in Python.

## Key Features

- **Strict Data Validation:** Utilizes Pydantic to enforce rigorous data shapes on incoming GitHub payloads (e.g., Commit data, Repository KPIs).
- **Secure Configuration Management:** Relies on robust environment variable loading through `pydantic-settings` to manage secrets securely.
- **Robust Error Handling:** Employs explicit domain-level exceptions for network failures and repository absence.
- **High-Performance Aggregation (Coming Soon):** Leverages `Polars` for zero-copy, lightning-fast tabular data transformations.
- **Interactive Visualisations (Coming Soon):** Provides a clean, responsive web interface using `Streamlit`.

## Prerequisites

- **Python:** 3.12 or newer.
- **Package Manager:** `uv` is required for dependency and environment management.
- **GitHub Token:** A Personal Access Token (PAT) is required to access the GitHub API.

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install dependencies using `uv`:**
   ```bash
   uv sync
   ```

3. **Configure Environment Variables:**
   Copy the example environment file and populate it with your GitHub Personal Access Token.
   ```bash
   cp .env.example .env
   # Edit .env and set GITHUB_TOKEN=your_token_here
   ```

## Usage

*Currently, the system's foundational configuration layer has been verified. Future cycles will implement execution scripts and a UI.*

To test the application's secure configuration state enforcement:
```bash
uv run python tests/uat/uat_script.py
```

## Development Workflow

This project adheres to strict code quality standards.

- **Run Linters (Ruff):**
  ```bash
  uv run ruff check .
  ```
- **Run Type Checker (MyPy):**
  ```bash
  uv run mypy .
  ```
- **Run Tests (Pytest):**
  ```bash
  uv run pytest
  ```

## Project Structure

```text
.
├── .env.example         # Template for environment variables
├── pyproject.toml       # Dependency and linter configuration
├── README.md            # Project documentation
├── src/
│   ├── domain_models/   # Pydantic schemas, custom exceptions, and application config
│   └── ...              # Future packages (ingestion, processing, ui)
└── tests/
    ├── uat/             # Execution verification scripts
    ├── unit/            # Unit and integration tests
    └── ...
```

## License

MIT License