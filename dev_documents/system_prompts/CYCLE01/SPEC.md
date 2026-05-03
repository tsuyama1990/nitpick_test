# CYCLE 01 SPECIFICATION: API Client and Data Extraction

## Summary
The primary goal of Cycle 01 is to establish a highly secure, mathematically reliable, and impeccably structured connection to the official GitHub REST API. This specific development cycle focuses entirely on building the foundational "Ingestion Layer" of our system architecture. This critical layer is solely responsible for securely authenticating with the external service using sensitive tokens, executing highly robust HTTP GET requests with strict timeout policies, and successfully retrieving raw JSON data payloads concerning target repository metadata and the chronological commit history. A paramount, non-negotiable concern throughout this entire cycle is the strict, uncompromising adherence to modern security best practices regarding credential management. Under absolutely no circumstances will GitHub Personal Access Tokens be hardcoded into the source code, nor will they ever be printed to standard output or logging frameworks. The system will rely exclusively and entirely on environment variables for all sensitive configuration. By the successful conclusion of this cycle, the core application will possess the robust capability to precisely target specific user-defined repositories, handle data pagination if necessary (or strictly limit extraction to the most recent 100 commits as explicitly dictated by the requirements), and gracefully, safely manage complex API-specific HTTP errors such as punitive rate limiting and unauthorized authentication failures without crashing the runtime environment. This ingestion mechanism acts as the absolute critical entry point for all data flowing into the subsequent, heavy-duty transformation and visualisation layers.

## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
*   **GITHUB_TOKEN**: A GitHub Personal Access Token is strictly required for successfully authenticating with the GitHub REST API to actively avoid severe, restrictive rate limits imposed on anonymous traffic.
    *   **Instruction for Coder**: You must explicitly append this exact key to the `.env.example` file accompanied by a highly clear, descriptive comment: `# Target Project Secrets: GitHub Personal Access Token (Leave empty in example file)`. Ensure the `python-dotenv` library is explicitly used within `config.py` to load this secret securely into the Python `os.environ` dictionary.

### B. System Configurations (`docker-compose.yml`)
*   (No specific system configurations for this cycle beyond standard Python environment setup.)
    *   **Instruction for Coder**: If setting up a local development environment using Docker, expose the application port (e.g., 8501 for Streamlit) and mount the source code volume. Preserve valid YAML formatting and idempotency.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
*   **Mandate Mocking**: You **MUST** explicitly and comprehensively mock all external API network calls that rely on the newly defined secrets in `.env.example` across all standard unit and integration tests (using libraries like `unittest.mock` or `pytest-mock`). The isolated Sandbox environment executing automated tests will fundamentally not possess valid, real API keys. If automated tests attempt actual outbound network calls without valid `.env` values, the continuous integration pipeline will inevitably fail catastrophically, potentially leading to infinite retry loops and resource exhaustion. Live API E2E tests must be strictly, explicitly segregated and optionally executed only when a valid, working token is explicitly provided by a human operator.

## System Architecture
The architecture for Cycle 01 centers entirely on establishing the isolated Ingestion Layer, ensuring mathematical separation from all future processing and presentation logic.

```text
.
├── .env.example
├── src/
│   ├── __init__.py
│   ├── config.py             # Configuration management (strictly using dotenv)
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py         # Strictly typed Pydantic models for repo and commit data
│   │   └── exceptions.py     # Custom, descriptive domain exceptions for error handling
│   └── ingestion/
│       ├── __init__.py
│       └── github_client.py  # Core, robust HTTP client logic handling requests
└── tests/
    ├── conftest.py
    └── unit/
        └── test_github_client.py
```

*   `src/config.py`: Exclusively responsible for loading environment variables securely using the `python-dotenv` library, ensuring failure if required keys are missing.
*   `src/domain/models.py`: Defines the strict, mathematically rigid data structures (utilizing Pydantic base models) representing the exact expected JSON payload from GitHub, ensuring runtime type safety.
*   `src/domain/exceptions.py`: Centralizes and mathematically defines error states (e.g., `AuthenticationError`, `RateLimitError`, `RepositoryNotFoundError`) to prevent raw HTTP errors from leaking.
*   `src/ingestion/github_client.py`: The absolute primary engine for outbound HTTP requests, utilizing robust libraries like `httpx` or `requests` configured with strict timeouts. It consumes the secure configuration, executes requests, parses raw JSON, and instantly instantiates the strictly typed domain models.

## Design Architecture
This specific cycle relies heavily and exclusively on the Pydantic library to precisely define the system's strict mathematical contract with the external, volatile GitHub API.

*   **`domain.models.RepositoryMetadata`**: Precisely represents the core, essential high-level information of a specific target repository.
    *   *Constraints*: Owner and Repo name fields must be strictly validated as strings. Star count, fork count, and open issue count fields must be strictly validated as non-negative integers. Any deviation must trigger a fast validation error.
    *   *Consumers*: Designed to be seamlessly consumed by the future Polars Transformation Layer and the Streamlit Presentation Layer.
*   **`domain.models.CommitRecord`**: Precisely represents a single, individual atomic commit within the repository's chronological history.
    *   *Constraints*: Commit hash must be explicitly validated as a string. Author name is explicitly validated as a string. The timestamp Date must be strictly parsable into a native Python `datetime` or `date` object to facilitate future time-series analysis.
    *   *Consumers*: Designed to be consumed by the Polars Transformation Layer for massive-scale chronological aggregation.
*   **Extensibility**: By defining these data structures entirely as foundational Pydantic base models, we mathematically allow for future, complex attributes (e.g., repository programming language, pull request counts, issue velocity) to be added effortlessly without breaking or destabilizing existing validation logic. The incredibly strict static typing mathematically ensures that the entire system fails incredibly fast right at the edge if the external GitHub API payload unexpectedly changes format.

## Implementation Approach
1.  **Environment Setup**: Install `python-dotenv` for configuration, `pydantic` for schema validation, and a robust HTTP client like `httpx`. Ensure `pytest` and `pytest-mock` are correctly configured for testing.
2.  **Configuration Management**: Implement the `config.py` module to securely read the `.env` file and expose the critical `GITHUB_TOKEN`. Rigorously validate that the token is present and not an empty string.
3.  **Domain Models**: Meticulously define `RepositoryMetadata` and `CommitRecord` in `models.py` using Pydantic, perfectly aligning the fields with the expected, documented GitHub REST API JSON response structure. Define the custom domain exceptions in `exceptions.py`.
4.  **API Client Implementation**: Architect and create `github_client.py`. Implement functions engineered to securely fetch the repository metadata and definitively fetch the latest 100 commits, implementing strict HTTP timeout values (e.g., 10 seconds) to prevent infinite hangs.
5.  **Error Handling**: Deeply integrate comprehensive `try...except` blocks within the client logic to actively intercept raw HTTP errors (specifically targeting status codes 401, 403, 404, 429) and instantly raise the corresponding, descriptive custom domain exceptions. Ensure all outbound HTTP headers correctly and securely include the authorization token.
6.  **Data Parsing**: Mathematically ensure the client immediately parses the raw, untyped JSON payload directly into the strictly defined Pydantic models *before* returning the complex data to any upstream caller.

## Test Strategy

### Unit Testing Approach
The highly isolated unit tests must absolutely rigorously verify the mathematical logic within `github_client.py` and the strict Pydantic models without ever making actual outbound network requests.
*   **Mocking Strategy**: Use the `pytest-mock` framework extensively to intercept and override calls made by `httpx.get` (or `requests.get`).
*   **Success Scenarios Verification**: Configure the testing mock to return predefined, completely valid JSON strings perfectly representing standard repository metadata and commit histories. Mathematically assert that the client correctly parses this simulated data into the appropriate Pydantic model instances and that the specific integer and string values match precisely.
*   **Error Handling Verification**: Configure the testing mock to instantly return specific HTTP error status codes (e.g., 404 Not Found, 403 Forbidden). Mathematically assert that the client successfully intercepts these raw responses and correctly raises the precise, custom exceptions strictly defined in `domain/exceptions.py`.
*   **Configuration Validation**: Definitively verify that `config.py` correctly loads the secret token from a heavily mocked OS environment and fails incredibly gracefully (e.g., by raising an initialization error) if the required environment variable is completely missing.

### Integration Testing Approach
Complex integration tests will rigorously verify the strict architectural contract between the configuration module, the HTTP client, and the deeply typed domain models.
*   While avoiding actual live API calls is strongly preferred for absolute sandbox stability, a very specifically marked integration test (e.g., decorated with `@pytest.mark.live`) can be implemented to carefully hit a highly available, extremely public repository (like `torvalds/linux`) to explicitly ensure the real-world JSON payload flawlessly matches the strict assumptions hardcoded into the Pydantic schemas. This highly volatile live test must be explicitly segregated and practically never run during standard automated CI pipelines unless a valid token is deliberately injected into the runner environment.
