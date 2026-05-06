# CYCLE01: System Setup, Domain Models & Configuration

## Summary

In Cycle 01, we lay the critical foundation for the GitHub Analytics Dashboard. The objective is to establish the core environment, configuration loading mechanisms, and strictly typed Pydantic domain models that will govern the application's data flow. This cycle does not interact with the live API or render the UI; instead, it ensures the application can securely read secrets (like the `GITHUB_TOKEN`), validate configuration states, and represent GitHub data structures robustly. By adhering strictly to Schema-first principles, we guarantee that all downstream components—from Polars dataframes to the Streamlit UI—will consume pristine, validated data. We will rely on `pydantic-settings` to enforce secure configuration management.

## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
External services discovered for this project rely entirely on the GitHub REST API.
- You must create a `.env.example` file in the root directory.
- Append the following with clear `# Target Project Secrets` comments:
  ```env
  # Target Project Secrets
  GITHUB_TOKEN=
  ```
- **Strict Rule:** Never hardcode actual tokens. `GITHUB_TOKEN` is mandatory for subsequent API calls to avoid rate limits and access private scopes if needed.

### B. System Configurations (`docker-compose.yml`)
- Create or update the `docker-compose.yml` file (if applicable or requested) for the application service.
- Add the following to the `environment:` section of the relevant service:
  ```yaml
    environment:
      - PORT=8501
      - CACHE_TTL_SECONDS=3600
  ```
- Ensure valid YAML formatting and idempotency (do not overwrite existing configurations).

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
- **Mandate Mocking:** All external API calls relying on the newly defined secrets in `.env.example` MUST be mocked in unit and integration tests (using `unittest.mock` or `pytest-mock`).
- *Why:* The Sandbox will not possess real API keys during autonomous evaluations. If tests attempt real network calls to SaaS providers without valid `.env` values, the pipeline will fail, causing an infinite retry loop. This cycle focuses on internal schemas, but configurations must handle missing or dummy tokens safely.

## System Architecture

The following directories and files must be implemented or modified:

.
├── **.env.example**
├── src/
│   ├── **__init__.py**
│   ├── config/
│   │   ├── **__init__.py**
│   │   └── **settings.py**
│   └── domain_models/
│       ├── **__init__.py**
│       ├── **repository.py**
│       └── **commit.py**
└── tests/
    └── **test_domain_models.py**

## Design Architecture

This cycle revolves around robust Pydantic-based schema design.

**AppConfig (`src/config/settings.py`)**
- A Pydantic `BaseSettings` model to validate the environment variables.
- Constraints: Requires `GITHUB_TOKEN`. Use `model_config = SettingsConfigDict(env_file=".env", extra="forbid")`.
- Expected Consumers: The Ingestion Layer (API client) implemented in the next cycle.

**RepositoryInfo (`src/domain_models/repository.py`)**
- Represents basic repository metrics.
- Fields: `name` (str), `owner` (str), `stargazers_count` (int), `forks_count` (int), `open_issues_count` (int).
- Constraints: Use `model_config = ConfigDict(extra="ignore")` because the GitHub API returns massive JSON payloads. We only want strictly typed required fields and must drop the rest safely.

**CommitData (`src/domain_models/commit.py`)**
- Represents an individual commit history entry.
- Fields: `sha` (str), `author_name` (str), `date` (datetime).
- Invariants: The GitHub API nests author and date information deeply (e.g., `commit.author.name`).
- Validation Rule: Implement a `@model_validator(mode="before")` to ingest the nested JSON payload and extract/flatten the required fields prior to validation.

## Implementation Approach

1. **Setup `.env.example`**: Create the file with the required target secrets.
2. **Init Files**: Ensure `src/` and its subdirectories contain `__init__.py` files to satisfy Mypy namespace resolution.
3. **Implement Configuration**: Write `src/config/settings.py`. Implement a helper function `get_settings()` that utilizes an `lru_cache` or a global module-level singleton pattern to avoid redundant `.env` parsing. Append `# noqa: PLW0603` if using a global variable.
4. **Implement Repository Schema**: Write `src/domain_models/repository.py`. Define the `RepositoryInfo` model with strict type hints and the `extra="ignore"` configuration.
5. **Implement Commit Schema**: Write `src/domain_models/commit.py`. Create the `CommitData` model and write the pre-validator method. The validator must check if the input is a dictionary, extract `sha`, navigate to `['commit']['author']['name']` and `['commit']['author']['date']`, and map them to the flat Pydantic model.
6. **Linting and Typing**: Run `uv run ruff check .`, `uv run ruff format .`, and `uv run mypy .` incrementally to ensure all new code adheres to strict project standards. Use `# type: ignore[arg-type]` in tests if Mypy strict mode complains about unpacking untyped dicts.

## Test Strategy

**Unit Testing Approach (Min 300 words)**
We will verify that the Pydantic models strictly enforce our invariants. For the `RepositoryInfo` model, we will instantiate it using a massive dictionary mimicking a real GitHub API response (containing dozens of irrelevant fields). The test must assert that the model instantiates correctly without throwing validation errors, successfully ignores the extra fields, and correctly types the required fields (`stargazers_count`, etc.). For the `CommitData` model, we will write a unit test providing a heavily nested dictionary representing the GitHub commit node. The test will verify that the `@model_validator(mode="before")` successfully traverses the tree, extracts the author name and date, and populates the flat model correctly. Additionally, we will verify the configuration model `AppConfig` by explicitly passing keyword arguments, ensuring `extra="forbid"` rejects unknown variables (using `# type: ignore[call-arg]` to bypass static type checks during the test). Dummy tokens must append `# noqa: S105, S106` to suppress Ruff security warnings.

**Integration Testing Approach (Min 300 words)**
Since this cycle focuses on internal schemas and configuration, pure integration testing with external services is deferred. However, we will conduct an integration test between the configuration module and the `.env` file system. Using Pytest's `monkeypatch` fixture, we will simulate the presence and absence of environment variables (specifically `GITHUB_TOKEN`). We will test the `get_settings()` singleton pattern to ensure that the environment is loaded securely and successfully when variables are present. Conversely, we will assert that a `pydantic.ValidationError` is properly raised when mandatory variables are completely absent, proving the system is fail-secure. We will also utilize the `tmp_path` fixture to temporarily create a mock `.env` file, pointing the `SettingsConfigDict` to this temporary file to prove that the library correctly parses and extracts the secrets without ever loading the system's actual sensitive keys.
