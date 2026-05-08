# GitHub Repository Analytics Dashboard

A streamlined Streamlit dashboard that provides real-time insights into GitHub repositories. By extracting data through the GitHub API and leveraging Polars for blazing-fast transformations, it presents clear, actionable metrics and visualizations for repository commit histories.

## Features
- **Key Metrics Overview**: Instantly view vital repo statistics including Stars, Forks, and Open Issues.
- **Commit Trends**: Analyze the repository's activity via an interactive chart showing commits grouped by day.
- **Top Contributors**: Discover the most active contributors with a bar chart highlighting the top 5 committers.
- **Smart Caching**: Implements a local caching layer to protect against GitHub API rate limits while maintaining quick load times.
- **Secure Configuration**: Uses environment variables to securely handle GitHub API tokens.

## Architecture & Design Rationale
- **Schema-First Pydantic Validation**: To ensure robustness when consuming third-party data from the GitHub API, we use strict `Pydantic` validation. We opted for `extra="ignore"` for the massive GitHub API JSON blobs, extracting and validating only the critical fields needed for the dashboard while silently discarding the rest. This provides type safety without the maintenance burden of fully mirroring the sprawling GitHub schema.
- **Polars over Pandas**: `Polars` was selected for the transformation layer due to its speed and efficiency in aggregating historical commit data.

## Installation
Ensure you have `uv` installed, then set up the project:

```bash
# Install dependencies
uv sync

# Configure your environment variables
cp .env.example .env
```
Next, open the newly created `.env` file and insert your GitHub Personal Access Token:
```env
GITHUB_TOKEN=ghp_your_token_here
```

## Usage
Run the dashboard directly using Streamlit:

```bash
uv run streamlit run src/ui/app.py
```
This will launch a local web server (typically at `http://localhost:8501`). Enter an `owner/repo` string (e.g., `streamlit/streamlit` or `tiangolo/fastapi`) into the search bar to view the analytics.

## Running the UAT
To verify the application's capabilities, you can interact with the User Acceptance Testing (UAT) tutorial powered by Marimo.
1. Run the tutorial notebook:
   ```bash
   uv run marimo edit tutorials/UAT_AND_TUTORIAL.py
   ```
2. **Mock vs Real Mode**:
   - By default, the tutorial runs in Mock Mode to safely verify the application logic.
   - If you want to hit the live GitHub API, simply provide a valid `GITHUB_TOKEN` in your `.env` file.

## Project Structure
- `src/domain_models/`: Pydantic data schemas and system configuration.
- `src/ingestion/`: API Client for fetching GitHub repository data.
- `src/transformation/`: Caching logic and Polars data aggregation.
- `src/ui/`: Streamlit web dashboard application.
- `tests/`: Comprehensive unit and End-to-End tests.
- `tutorials/`: Marimo interactive notebooks for UAT.
