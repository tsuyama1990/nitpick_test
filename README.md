# GitHub Repository Analytics Dashboard (Core Platform)

A strongly-typed foundation capable of handling external configuration and defining the exact shape of GitHub repository data. This core handles secure credential management and predictable, validated inputs for downstream analytics.

## Features

- **Strict Environment Configuration:** Enforces presence of required secrets like `GITHUB_TOKEN` to fail fast securely.
- **Robust Domain Models:** Strictly validates GitHub repository metrics and commit data shapes, shedding unknown keys for performance.

## Installation

1. Clone the repository and navigate into the project directory.
2. Sync dependencies:
   ```bash
   uv sync
   ```
3. Set up the environment:
   ```bash
   cp .env.example .env
   # Open .env and populate GITHUB_TOKEN
   ```

## Usage

To run the interactive User Acceptance Tutorial verifying the environment and schema setup:

```bash
uv run python tests/uat/UAT_AND_TUTORIAL.py
```

## Structure

```text
.
├── .env.example         # Template for environment variables
├── pyproject.toml       # Project configuration
├── src/
│   └── domain_models/   # Pydantic schemas, exceptions, and configuration singletons
└── tests/
    ├── uat/             # Marimo notebooks for interactive User Acceptance Testing
    └── unit/            # Pytest unit tests
```

## Architecture & Design Rationale

- **Schema-First Design:** Implements `pydantic` schemas before any external I/O or business logic. This guarantees the system defends itself against malformed responses.
- **Isolated Configuration:** Utilizes `pydantic-settings` via `BaseSettings` forcing `.env` validations, effectively removing hardcoded configurations and enhancing security.
