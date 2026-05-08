# GitHub Analytics Dashboard

## Overview
A robust, interactive dashboard for analyzing GitHub repositories. This tool seamlessly fetches real-time data from the GitHub REST API, processes metrics, and renders insights via a Streamlit interface. It includes rate-limit caching for high performance.

## Features
- **Live GitHub API Integration**: Securely connects to GitHub to fetch repository metrics (Stars, Forks, Issues) and recent commit histories.
- **High-Performance Processing**: Aggregates commit timelines and identifies top committers instantly.
- **Intelligent Local Caching**: Implements a Parquet-based caching mechanism to prevent exhausting API rate limits and ensure instantaneous UI updates on repeated queries.
- **Interactive UI**: A pure Streamlit presentation layer offering a clean, interactive user experience with line and bar charts.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Sync Dependencies**:
   Utilize `uv` to install the environment and requirements.
   ```bash
   uv sync
   ```

3. **Configure Environment Variables**:
   Copy the example environment file and insert your GitHub token.
   ```bash
   cp .env.example .env
   # Edit .env and add your GITHUB_TOKEN
   ```

## Usage

To launch the interactive dashboard, run the Streamlit application using `uv`:

```bash
uv run streamlit run src/app.py
```

Once the server starts, open the provided local URL in your browser. Enter a repository name in the `owner/repo` format (e.g., `streamlit/streamlit`) and click "Analyze" to view the metrics and charts.

## Structure

```text
.
├── src/
│   ├── config.py           # Application settings and environment loading
│   ├── domain_models/      # Strict data validation schemas
│   ├── github_client.py    # GitHub REST API client with error handling
│   ├── metrics.py          # High-performance Polars transformation engine
│   ├── cache.py            # Local Parquet caching
│   └── app.py              # Streamlit Presentation UI
├── tests/                  # Automated unit, E2E, and UAT tests
└── pyproject.toml          # uv dependency and tool configuration
```
