# GitHub Analytics Dashboard

A simple web dashboard to analyze public GitHub repositories. Built with Streamlit and Polars.

## Features
- **Repository KPIs**: View basic repository stats such as Stars, Forks, and Open Issues.
- **Commit History**: Visualizations for the daily commit activity over the last 100 commits.
- **Top Committers**: View the top 5 contributors based on the commit history.
- **Caching**: Local caching mechanism to prevent hitting GitHub API rate limits.

## Installation

This project manages dependencies via [uv](https://github.com/astral-sh/uv).

1. Clone the repository and move into the directory.
2. Ensure you have `uv` installed.
3. Install dependencies:
   ```bash
   uv sync
   ```
4. Copy the `.env.example` file to `.env` and fill in your GitHub Personal Access Token.
   ```bash
   cp .env.example .env
   ```

## Usage

To start the Streamlit web server locally:

```bash
uv run streamlit run src/visualization.py
```

After starting the server, open your browser to the URL displayed in the terminal. Type in an `owner/repo` string (e.g. `streamlit/streamlit`) to view the analytics dashboard.

## Structure
```
.
├── .env.example        # Environment variable template
├── pyproject.toml      # Dependency management via uv
├── src/                # Application source code
│   ├── domain_models/  # Pydantic schemas mapping GitHub API payloads
│   ├── ingestion.py    # GitHub REST API client
│   ├── storage.py      # Local parquet caching logic
│   ├── transformation.py # Polars logic for aggregations
│   └── visualization.py  # Streamlit UI
├── tests/              # Pytest logic tests
└── tutorials/          # Marimo Notebooks for UAT and onboarding
```
