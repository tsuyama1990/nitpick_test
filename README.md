# GitHub Analytics Dashboard

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

A robust, strictly-typed Proof of Concept (PoC) for analyzing GitHub repositories. It securely loads configurations and represents data structures accurately through strictly typed Pydantic domains.

## Features
- **Strictly Typed Configurations**: Securely enforces necessary credentials.
- **Robust Domain Models**: Represents GitHub commits and repositories directly with accurate data validation and structures, while extracting and flattening useful API inputs directly.
- **Fail-Secure Environment Validation**: Blocks missing configurations right at launch.

## Architecture & Design Rationale
- `extra="forbid"` on models (e.g., config) ensures unexpected properties throw errors rather than silently bypassing validation, catching misconfigurations early.
- `extra="ignore"` on API consumption models like `RepositoryInfo` ensures that when GitHub arbitrarily adds new fields to their massive payload, our application remains robust and doesn't crash on parsing.
- The `CommitData` relies on a Pydantic pre-validator because the upstream nested GitHub node `commit.author` requires preprocessing prior to standard validation.
- Singleton implementations ensure `.env` file reading limits to the initial launch rather than hitting disk repeatedly.

## Prerequisites
- **Python**: 3.12 or higher.
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (strictly enforced for dependency management).
- **Credentials**: A valid GitHub Personal Access Token (PAT).

## Installation & Setup

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

**Running Checks and Unit Tests**:
Run the included comprehensive testing suite directly.
```bash
uv run pytest --cov
```

**Running Tutorials and Validation Notebooks**:
To interact with Marimo tutorials:
```bash
uv run marimo edit tutorials/UAT_AND_TUTORIAL.py
```

## Project Structure
```text
.
├── src/
│   ├── config/          # Pydantic Settings and env loading
│   ├── domain_models/   # Core entities (Repository, Commit schemas)
├── tests/               # Pytest suites (Unit, E2E)
├── tutorials/           # Marimo UAT Verification notebooks
├── .env.example         # Template for environment secrets
└── pyproject.toml       # uv dependency and tool configuration
```

## License
MIT License.
