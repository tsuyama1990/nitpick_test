# GitHub Repository Analytics Dashboard

An analytical engine designed to aggregate and process GitHub repository metrics and commit history locally. By leveraging Polars for highly performant tabular data manipulation and Pydantic for strict schema validation, this tool ensures robust transformation of raw API payloads into structured insights.

## Features

- **Robust Data Validation**: Enforces strict schema rules via Pydantic on incoming API payloads to prevent malformed data.
- **High-Performance Transformations**: Uses Polars to efficiently process datasets, aggregating commit counts by date.
- **Deterministic Analytics**: Accurately computes the top committers and handles tie-breaking deterministically to ensure consistent behavior.
- **Secure Configuration Management**: Enforces the presence of essential secrets without embedding them in version control.

## Installation

Ensure you have Python 3.12+ and `uv` installed. Run the following command to set up the environment:

```bash
uv sync
```

Set up your secrets by creating an environment file:
```bash
cp .env.example .env
# Edit .env to add your GITHUB_TOKEN
```

## Usage

This project currently provides internal analytics processing functions which can be executed programmatically or tested using the provided test suites.

To run the full test suite and verify functionality:
```bash
uv run pytest
```

To run the User Acceptance Testing verification script directly:
```bash
PYTHONPATH=. uv run python tests/uat/uat_cycle03.py
```

## Structure

- `src/domain_models/`: Contains the Pydantic schemas, settings, and business-logic exceptions.
- `src/processing/`: Contains the Polars transformations engine for processing repository data.
- `tests/`: Contains isolated unit tests and user acceptance test scripts.
