# GitHub Repository Analysis Dashboard PoC

A high-performance proof of concept for analyzing GitHub repository metrics, such as stars, forks, and commit histories. This project utilizes Polars for data aggregation and Streamlit for visualizing key trends directly in your browser.

## Features

- **Robust Ingestion**: Safely connects to the official GitHub REST API to fetch targeted repository details and chronological commit histories.
- **Strict Data Validation**: Utilizes Pydantic schemas to thoroughly validate data directly at the boundary, ensuring robust behavior without silent failures.
- **Resilient Error Handling**: Safely intercepts standard HTTP rate limit responses and invalid authentications without exposing raw errors or sensitive credentials.

## Installation

Ensure you have [uv](https://github.com/astral-sh/uv) installed, then run:

```bash
uv sync
```

Set up your environment variables by copying the example file and filling in your Personal Access Token:
```bash
cp .env.example .env
```

## Usage

This module exposes the core HTTP client for data ingestion. To test it out in an interactive notebook:

```bash
uv run marimo edit tests/uat/UAT_AND_TUTORIAL.py
```

## Structure
- `src/domain_models/`: Pydantic definitions and strict custom exceptions.
- `src/ingestion/`: The robust API client.
- `tests/`: TDD suites and interactive Marimo notebooks validating user workflows.
