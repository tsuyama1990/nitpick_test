# GitHub Analytics Dashboard

## Title & Overview
GitHub Analytics Dashboard is a simple, lightweight Streamlit application designed to fetch, transform, and visualize key metrics from any public GitHub repository. It quickly provides insights into a repository's health by displaying its basic statistics (Stars, Forks, Open Issues) alongside a visual history of daily commits and the most active committers.

This application acts as a Proof of Concept (PoC) for data ingestion from the GitHub REST API, utilizing Polars for high-performance data transformation and PyArrow for local parquet file caching to respect API rate limits.

## Features
- **Live GitHub API Integration:** Fetches real-time repository metadata and recent commit history.
- **Fast Data Transformation:** Leverages Polars to calculate daily commit frequencies and identify top committers.
- **Smart Caching:** Avoids rate-limiting and speeds up repeated queries by caching processed data to local Parquet files.
- **Interactive UI:** Built on Streamlit, providing an easy-to-use search bar and clear, responsive visualizations.
- **Secure Configuration:** Ensures personal access tokens are securely loaded via `.env` files and never hardcoded.

## Architecture & Design Rationale
- **Schema Validation with Pydantic:** We use Pydantic models with `extra="ignore"` to safely ingest massive payloads from the GitHub API while explicitly typing only the required fields. This prevents validation errors from unexpected new fields added by GitHub in the future.
- **Singleton Settings:** Configuration is loaded lazily using a singleton pattern via `pydantic-settings`, ensuring environment variables (like `GITHUB_TOKEN`) are parsed exactly once upon startup.
- **Local Caching Strategy:** Processed dataframes are serialized using PyArrow into Parquet format. Before fetching new data, the app checks the modification time (`st_mtime`) of the cached files. If the files exist and are within the TTL (Time-To-Live, e.g., 1 hour), the app skips the external API calls, reducing latency and saving API quota.

## Installation
Ensure you have Python 3.12+ installed. The project uses `uv` for dependency management.

1. Clone the repository and navigate to the project root.
2. Sync the dependencies using `uv`:
   ```bash
   uv sync
   ```
3. Copy the `.env.example` file to create your local `.env` configuration:
   ```bash
   cp .env.example .env
   ```
4. Open the `.env` file and insert your GitHub Personal Access Token:
   ```env
   GITHUB_TOKEN=ghp_your_personal_access_token_here
   ```

## Usage
To start the Streamlit dashboard, run the following command from the project root:

```bash
uv run streamlit run src/presentation/app.py
```

Once the application launches in your browser:
1. Navigate to the sidebar on the left.
2. Enter the target repository in the format `owner/repo` (e.g., `streamlit/streamlit`).
3. Click **Fetch Data** to retrieve and visualize the repository analytics.

### Testing the Application
This project maintains >85% test coverage. You can run the test suite (excluding live API calls to prevent CI hangs) using:
```bash
uv run pytest
```
To run the live integration tests, ensure your `.env` file is set up and execute:
```bash
uv run pytest -m live
```
