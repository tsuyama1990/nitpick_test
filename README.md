# GitHub Repository Analytics Dashboard

## Overview
The GitHub Repository Analytics Dashboard is a comprehensive tool designed to retrieve, process, and visualize insights from GitHub repositories. By securely connecting to the GitHub REST API, it allows users to deeply understand repository performance metrics, track commit history, and analyze contributor activity in a streamlined application.

## Features
- **Secure Configuration Management**: Safely loads and validates required credentials (like your `GITHUB_TOKEN`) using Pydantic Settings, preventing insecure initialization.
- **Robust Domain Modeling**: Enforces strict, type-safe data validation using Pydantic models to ensure only correctly formatted repository metrics and commit histories are processed.

*(More features such as Data Transformation, Caching, and the Streamlit Visual UI will be available soon as the application evolves.)*

## Installation

1. Clone the repository and navigate into it.
2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```
3. Set up your environment variables:
   - Copy the `.env.example` file to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and add your GitHub Personal Access Token:
     ```env
     GITHUB_TOKEN=your_personal_access_token_here
     ```

## Usage

Currently, the foundation of the project is verified, meaning the configuration loader and strict data schemas are actively working in the background.

You can run the User Acceptance Tests (UAT) to see the application's configuration checks and schema validations in action:
```bash
uv run python tests/uat/UAT_AND_TUTORIAL.py
```

## Architecture & Design Rationale
- **Domain-Driven Design**: By leveraging strictly validated Pydantic models at the very boundaries of the application, we proactively defend the system against malformed data and unexpected schema changes from upstream APIs.
- **Fail-Fast Configuration**: `pydantic-settings` is utilized to mandate the existence of critical environment variables (like `GITHUB_TOKEN`). The application safely crashes during initialization rather than failing unpredictably mid-execution.
- **Cache-Optimized Strip Filtering**: To manage the massive data payloads from GitHub, unknown keys are stripped proactively *before* instantiation via a pre-validator that utilizes a module-level cached key set. This ensures O(1) attribute lookup and preserves CPU cycles.

## Structure
```text
.
├── .env.example       # Template for environment variables
├── pyproject.toml     # Project dependencies and tool configurations
├── src/
│   └── domain_models/ # Core Pydantic models and Configuration classes
│       ├── config.py
│       ├── exceptions.py
│       └── schemas.py
└── tests/
    ├── uat/           # User Acceptance Testing scripts
    └── unit/          # Automated Unit Tests
```
