# Cycle 01: Domain Modeling and Configuration Setup Specification

## Summary
This cycle forms the bedrock of the GitHub Repository Analytics Dashboard. The objective here is to establish a secure, strongly-typed foundation capable of handling external configuration and defining the exact shape of the data the application expects to process. This foundational layer ensures that subsequent cycles, which will introduce network I/O and complex data transformations, can rely on predictable, validated inputs and secure credential management. This phase involves no external network calls or user interface rendering. Instead, it focuses entirely on the application's internal domain models and its interface with the host environment. By the end of this cycle, the system will possess a robust configuration loader using `pydantic-settings` that guarantees the presence of required environment variables, alongside a suite of Pydantic models that strictly define the structure of GitHub's repository metrics and commit data. This approach prevents downstream failures caused by malformed data or missing credentials, thereby elevating the overall resilience of the PoC.

## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
This project requires interaction with the GitHub REST API, which strictly requires a Personal Access Token (PAT) to ensure sufficient rate limits for the application's operation.
- **Action for Coder:** Create a `.env.example` file in the root of the project repository.
- **Content:** Append the following configuration key, ensuring the value remains empty to act as a safe template.
  ```env
  # Target Project Secrets
  GITHUB_TOKEN=
  ```
- **Rule:** Under no circumstances should real tokens be committed to version control. The application must crash during initialization if this token is missing in the actual environment.

### B. System Configurations (`docker-compose.yml`)
At this stage, there are no complex external databases or services requiring a `docker-compose.yml` configuration. The local development environment relies entirely on the host operating system and local Python environment managed by `uv`.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
**MANDATORY INSTRUCTION:** Because this cycle implements the foundational configuration meant to load external secrets, it is imperative that the testing strategy respects the isolated nature of the CI sandbox.
- All external API calls that would rely on the `GITHUB_TOKEN` defined in `.env.example` **MUST** be mocked in unit and integration tests.
- When testing the `Settings` class, use `unittest.mock.patch.dict(os.environ)` to simulate both the presence and absence of the `GITHUB_TOKEN`.
- The sandbox will not possess real API keys during the automated evaluation phase. Failing to mock these dependencies will result in test pipeline failures and infinite retry loops.

## System Architecture
The file structure for this cycle introduces the core directories and the initial files required for configuration and domain modeling. The files explicitly marked in bold represent the targets for creation during this cycle.

```text
.
├── **.env.example**
├── src/
│   ├── __init__.py
│   ├── **config.py**
│   └── domain/
│       ├── __init__.py
│       ├── **exceptions.py**
│       └── **schemas.py**
└── tests/
    ├── __init__.py
    └── **test_domain.py**
```

## Design Architecture
This cycle is deeply rooted in Domain-Driven Design principles, specifically relying on Pydantic to enforce data integrity at the system boundaries.

The central component is `src/config.py`, which defines the application's configuration contract. The `Settings` class inherits from `pydantic_settings.BaseSettings`. Its primary invariant is the existence of the `GITHUB_TOKEN` string. It uses `SettingsConfigDict(env_file=".env", extra="forbid")` to ensure that it only loads expected variables and strictly fails if unexpected variables are injected, preventing configuration drift. A singleton function, `get_settings()`, will provide lazy evaluation and globally accessible, cached configuration instances.

The domain concepts are defined in `src/domain_models/schemas.py`. These models represent the expected shape of the data retrieved from GitHub.
- `RepositoryMetrics` acts as the container for KPI data. It strictly requires `stargazers_count` (integer), `forks_count` (integer), and `open_issues_count` (integer).
- To model the commit history, a nested structure is required to match GitHub's JSON schema. The `CommitAuthor` model defines the author's `name` (string) and the commit `date` (datetime, enforcing ISO 8601 parsing). This is nested within a `CommitData` model, which represents the inner commit payload. Finally, the `CommitItem` model acts as the root object for a single item in the commit array returned by the API, containing the `commit` field.
- **Rule:** All models must enforce strict validation using `model_config = ConfigDict(extra="forbid")`. Because GitHub's payloads are massive, the implementation must use a pure-function filter (e.g., extracting a `_strip_extra` logic called within a `@model_validator(mode="before")`) to strip unknown keys matching against `model.model_fields` *before* constructing the model instance. This guarantees that only explicitly defined fields enter the system.

Furthermore, `src/domain_models/exceptions.py` establishes the vocabulary for error handling. A base class, `GitHubAnalyticsError(Exception)`, will be defined. Specific subclasses like `RepositoryNotFoundError` and `RateLimitExceededError` will inherit from this, allowing the upstream orchestrator and UI to catch and handle these specific business-logic errors gracefully, rather than dealing with raw `HTTPError` objects.

## Implementation Approach
1. **Initialize Directory Structure:** Ensure the `src/` and `src/domain_models/` directories exist, along with their respective `__init__.py` files to establish them as Python packages.
2. **Create the Environment Template:** Create the `.env.example` file in the project root containing the single line `# Target Project Secrets
GITHUB_TOKEN=`.
3. **Implement Domain Exceptions:** Create `src/domain_models/exceptions.py`. Define `GitHubAnalyticsError` inheriting from Python's built-in `Exception`. Define `RepositoryNotFoundError` and `RateLimitExceededError` inheriting from `GitHubAnalyticsError`. Ensure they accept informative string messages upon initialization.
4. **Implement Pydantic Schemas:** Create `src/domain_models/schemas.py`. Import necessary types (`datetime` from `datetime`, `BaseModel`, `ConfigDict` from `pydantic`). Define the models `RepositoryMetrics`, `CommitAuthor`, `CommitData`, and `CommitItem` precisely as described in the Design Architecture. Ensure correct typing for every field to leverage mypy's strict checks.
5. **Implement Configuration Management:** Create `src/config.py`. Import `BaseSettings`, `SettingsConfigDict` from `pydantic_settings`. Define the `Settings` class with the `GITHUB_TOKEN` attribute. Implement the `get_settings` function using `functools.lru_cache` to ensure the settings are only parsed once during the application's lifecycle, providing a robust singleton pattern.

## Test Strategy

### Unit Testing Approach
The unit tests for this cycle will live in `tests/unit/test_domain_models.py` and must achieve 100% coverage for the newly created files.
- **Schema Validation:** Write tests to instantiate the Pydantic models with valid mock dictionaries representing GitHub's JSON. Assert that the models parse the data correctly, specifically checking that string dates in the `CommitAuthor` payload are correctly cast to Python `datetime` objects.
- **Schema Rejection:** Write tests passing invalid data (e.g., passing a string where an integer is expected for `stargazers_count`, or omitting a required field like `name` in the author data). Assert that Pydantic correctly raises a `ValidationError`. This proves the system will defend itself against malformed API responses.

### Integration Testing Approach
While this cycle does not involve network integration, it does involve integration with the host operating system's environment.
- **Configuration Loading:** Write tests utilizing `unittest.mock.patch.dict` to manipulate the `os.environ`.
- In one test, set a valid dummy `GITHUB_TOKEN` and assert that `Settings()` successfully initializes and correctly exposes the token.
- In a second, critical test, clear the environment variables and ensure that `Settings()` raises a Pydantic validation error, proving that the application will refuse to start in an insecure or improperly configured state. Note: Ensure `get_settings.cache_clear()` is called between tests to prevent singleton state pollution.
