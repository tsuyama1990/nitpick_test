# GitHub Repository Analytics Dashboard

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A modern, high-performance dashboard for analysing GitHub repository data. This application securely connects to the GitHub REST API to fetch, process, cache, and visualise repository metrics and commit histories, offering an intuitive interface built entirely in Python.

## Features

- **Secure Configuration Management:** Robustly validates and enforces the presence of required credentials (like GitHub tokens) before application startup, ensuring secure execution.
- **Strict Data Validation:** Utilizes strict Pydantic schemas to parse and validate incoming data from the GitHub API, cleanly rejecting malformed data to ensure stability.
- **Automated Data Ingestion:** Seamlessly connects to the GitHub REST API with robust error handling and strict rate limit protection.
- **High-Performance Aggregation:** Leverages `Polars` for zero-copy, lightning-fast tabular data transformations.
- **Zero-Config Local Caching:** Implements an intelligent, Time-To-Live (TTL) based local Parquet file cache to drastically reduce API latency and respect network constraints.
- **Interactive Visualisations:** Provides a clean, responsive web interface using `Streamlit` to display core repository KPIs and interactive charts of developer activity over time.

## Installation

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

To launch the interactive dashboard, run the application via `uv`.

Ensure your `.env` file is properly configured with your `GITHUB_TOKEN` before running the command below. The application will immediately halt if the token is missing.

```bash
uv run streamlit run src/app.py
```

Once the server starts, open your browser to `http://localhost:8501`. Enter a repository name in the format `owner/repo` (e.g., `streamlit/streamlit`) and click the analyze button to view the dashboard.

## Structure

```text
.
├── .env.example         # Template for environment variables
├── pyproject.toml       # Dependency and configuration
├── README.md            # Project documentation
├── src/
│   ├── app.py           # Streamlit frontend application
│   └── domain_models/   # Core schemas, config models, and custom exceptions
└── tests/
    ├── unit/            # Unit tests for domain logic
    └── uat/             # User acceptance tests
```

## License

MIT License
