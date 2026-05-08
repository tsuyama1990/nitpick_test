# GitHub Repository Analytics Dashboard PoC

## Overview
This is a Proof of Concept (PoC) dashboard for analyzing GitHub repositories. It fetches repository metrics (Stars, Forks, Open Issues) and commit history (Last 100 commits), processes the data, and visualizes it through an interactive Streamlit UI.

## Features
- Fetches real-time repository metrics and commit history using the official GitHub REST API.
- Caches data locally to respect API rate limits and improve dashboard performance.
- Visualizes the number of commits per day and top committers.
- Robust error handling for non-existent repositories, authentication failures, and rate limiting.

## Installation
Ensure you have `uv` installed, then run:

```bash
uv sync
```

## Configuration
Before running the application, you must provide a valid GitHub Personal Access Token.
Copy the example environment file and add your token:

```bash
cp .env.example .env
# Edit .env and set your GITHUB_TOKEN
```

## Usage
Start the Streamlit application by running the following command:

```bash
uv run streamlit run src/presentation/app.py
```

## Structure
- `src/domain_models`: Pydantic models enforcing strict schemas.
- `src/ingestion`: GitHub REST API client using `httpx`.
- `src/transformation`: Polars processing and local caching.
- `src/presentation`: Streamlit dashboard and UI logic.
