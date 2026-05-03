# CYCLE 01 SPECIFICATION: API Client and Data Extraction

## Summary
The primary goal of Cycle 01 is to establish a secure, reliable, and well-structured connection to the GitHub REST API. This cycle focuses on building the foundational "Ingestion Layer" of our architecture, which is responsible for authenticating with the external service, executing HTTP GET requests, and retrieving raw JSON data concerning repository metadata and commit history. A paramount concern in this cycle is the strict adherence to security best practices regarding credential management. Under no circumstances will GitHub Personal Access Tokens be hardcoded or logged. The system will rely exclusively on environment variables for configuration. By the conclusion of this cycle, the application will possess the capability to target specific repositories, handle pagination if necessary (or limit to the most recent 100 commits as per requirements), and gracefully manage API-specific errors such as rate limiting and authentication failures. This ingestion mechanism acts as the critical entry point for all data flowing into the subsequent transformation and visualisation layers.
# CYCLE 01 SPECIFICATION: API Client and Data Extraction

## Summary
The primary goal of Cycle 01 is to establish a secure, reliable, and well-structured connection to the GitHub REST API. This cycle focuses on building the foundational "Ingestion Layer" of our architecture, which is responsible for authenticating with the external service, executing HTTP GET requests, and retrieving raw JSON data concerning repository metadata and commit history. A paramount concern in this cycle is the strict adherence to security best practices regarding credential management. Under no circumstances will GitHub Personal Access Tokens be hardcoded or logged. The system will rely exclusively on environment variables for configuration. By the conclusion of this cycle, the application will possess the capability to target specific repositories, handle pagination if necessary (or limit to the most recent 100 commits as per requirements), and gracefully manage API-specific errors such as rate limiting and authentication failures. This ingestion mechanism acts as the critical entry point for all data flowing into the subsequent transformation and visualisation layers.
# CYCLE 01 SPECIFICATION: API Client and Data Extraction

## Summary
The primary goal of Cycle 01 is to establish a secure, reliable, and well-structured connection to the GitHub REST API. This cycle focuses on building the foundational "Ingestion Layer" of our architecture, which is responsible for authenticating with the external service, executing HTTP GET requests, and retrieving raw JSON data concerning repository metadata and commit history. A paramount concern in this cycle is the strict adherence to security best practices regarding credential management. Under no circumstances will GitHub Personal Access Tokens be hardcoded or logged. The system will rely exclusively on environment variables for configuration. By the conclusion of this cycle, the application will possess the capability to target specific repositories, handle pagination if necessary (or limit to the most recent 100 commits as per requirements), and gracefully manage API-specific errors such as rate limiting and authentication failures. This ingestion mechanism acts as the critical entry point for all data flowing into the subsequent transformation and visualisation layers.
# CYCLE 01 SPECIFICATION: API Client and Data Extraction

## Summary
The primary goal of Cycle 01 is to establish a secure, reliable, and well-structured connection to the GitHub REST API. This cycle focuses on building the foundational "Ingestion Layer" of our architecture, which is responsible for authenticating with the external service, executing HTTP GET requests, and retrieving raw JSON data concerning repository metadata and commit history. A paramount concern in this cycle is the strict adherence to security best practices regarding credential management. Under no circumstances will GitHub Personal Access Tokens be hardcoded or logged. The system will rely exclusively on environment variables for configuration. By the conclusion of this cycle, the application will possess the capability to target specific repositories, handle pagination if necessary (or limit to the most recent 100 commits as per requirements), and gracefully manage API-specific errors such as rate limiting and authentication failures. This ingestion mechanism acts as the critical entry point for all data flowing into the subsequent transformation and visualisation layers.
# CYCLE 01 SPECIFICATION: API Client and Data Extraction

## Summary
The primary goal of Cycle 01 is to establish a secure, reliable, and well-structured connection to the GitHub REST API. This cycle focuses on building the foundational "Ingestion Layer" of our architecture, which is responsible for authenticating with the external service, executing HTTP GET requests, and retrieving raw JSON data concerning repository metadata and commit history. A paramount concern in this cycle is the strict adherence to security best practices regarding credential management. Under no circumstances will GitHub Personal Access Tokens be hardcoded or logged. The system will rely exclusively on environment variables for configuration. By the conclusion of this cycle, the application will possess the capability to target specific repositories, handle pagination if necessary (or limit to the most recent 100 commits as per requirements), and gracefully manage API-specific errors such as rate limiting and authentication failures. This ingestion mechanism acts as the critical entry point for all data flowing into the subsequent transformation and visualisation layers.


## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
*   **GITHUB_TOKEN**: A GitHub Personal Access Token required for authenticating with the GitHub REST API to avoid severe rate limits.
    *   **Instruction for Coder**: Append this key to the `.env.example` file with a clear comment: `# Target Project Secrets: GitHub Personal Access Token (Leave empty in example file)`. Ensure `python-dotenv` is used to load this secret securely.

### B. System Configurations (`docker-compose.yml`)
*   (No specific system configurations for this cycle beyond standard Python environment setup.)
    *   **Instruction for Coder**: If setting up a local development environment using Docker, expose the application port (e.g., 8501 for Streamlit) and mount the source code volume. Preserve valid YAML formatting and idempotency.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
*   **Mandate Mocking**: You **MUST** explicitly mock all external API calls relying on the newly defined secrets in `.env.example` in unit and integration tests (using `unittest.mock` or `pytest-mock`). The Sandbox environment executing automated tests will not possess valid real API keys. If tests attempt actual network calls without valid `.env` values, the pipeline will inevitably fail, leading to infinite retry loops. Live API tests must be strictly segregated and optionally executed only when a valid token is explicitly provided by a human operator.

## System Architecture
The architecture for Cycle 01 centers on establishing the Ingestion Layer, ensuring clear separation from future processing and presentation logic.

```text
.
├── .env.example
├── src/
│   ├── __init__.py
│   ├── config.py             # Configuration management (dotenv)
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py         # Pydantic models for repo and commit data
│   │   └── exceptions.py     # Custom domain exceptions
│   └── ingestion/
│       ├── __init__.py
│       └── github_client.py  # Core HTTP client logic
└── tests/
    ├── conftest.py
    └── unit/
        └── test_github_client.py
```

*   `src/config.py`: Responsible for loading environment variables securely using `python-dotenv`.
*   `src/domain/models.py`: Defines the strict data structures (Pydantic models) representing the expected JSON payload from GitHub.
*   `src/domain/exceptions.py`: Centralizes error definitions (e.g., `AuthenticationError`, `RateLimitError`).
*   `src/ingestion/github_client.py`: The primary engine for HTTP requests, utilizing libraries like `httpx` or `requests`. It consumes configuration, executes requests, parses JSON, and instantiates the domain models.
## System Architecture
The architecture for Cycle 01 centers on establishing the Ingestion Layer, ensuring clear separation from future processing and presentation logic.

```text
.
├── .env.example
├── src/
│   ├── __init__.py
│   ├── config.py             # Configuration management (dotenv)
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py         # Pydantic models for repo and commit data
│   │   └── exceptions.py     # Custom domain exceptions
│   └── ingestion/
│       ├── __init__.py
│       └── github_client.py  # Core HTTP client logic
└── tests/
    ├── conftest.py
    └── unit/
        └── test_github_client.py
```

*   `src/config.py`: Responsible for loading environment variables securely using `python-dotenv`.
*   `src/domain/models.py`: Defines the strict data structures (Pydantic models) representing the expected JSON payload from GitHub.
*   `src/domain/exceptions.py`: Centralizes error definitions (e.g., `AuthenticationError`, `RateLimitError`).
*   `src/ingestion/github_client.py`: The primary engine for HTTP requests, utilizing libraries like `httpx` or `requests`. It consumes configuration, executes requests, parses JSON, and instantiates the domain models.
## System Architecture
The architecture for Cycle 01 centers on establishing the Ingestion Layer, ensuring clear separation from future processing and presentation logic.

```text
.
├── .env.example
├── src/
│   ├── __init__.py
│   ├── config.py             # Configuration management (dotenv)
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py         # Pydantic models for repo and commit data
│   │   └── exceptions.py     # Custom domain exceptions
│   └── ingestion/
│       ├── __init__.py
│       └── github_client.py  # Core HTTP client logic
└── tests/
    ├── conftest.py
    └── unit/
        └── test_github_client.py
```

*   `src/config.py`: Responsible for loading environment variables securely using `python-dotenv`.
*   `src/domain/models.py`: Defines the strict data structures (Pydantic models) representing the expected JSON payload from GitHub.
*   `src/domain/exceptions.py`: Centralizes error definitions (e.g., `AuthenticationError`, `RateLimitError`).
*   `src/ingestion/github_client.py`: The primary engine for HTTP requests, utilizing libraries like `httpx` or `requests`. It consumes configuration, executes requests, parses JSON, and instantiates the domain models.
## System Architecture
The architecture for Cycle 01 centers on establishing the Ingestion Layer, ensuring clear separation from future processing and presentation logic.

```text
.
├── .env.example
├── src/
│   ├── __init__.py
│   ├── config.py             # Configuration management (dotenv)
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py         # Pydantic models for repo and commit data
│   │   └── exceptions.py     # Custom domain exceptions
│   └── ingestion/
│       ├── __init__.py
│       └── github_client.py  # Core HTTP client logic
└── tests/
    ├── conftest.py
    └── unit/
        └── test_github_client.py
```

*   `src/config.py`: Responsible for loading environment variables securely using `python-dotenv`.
*   `src/domain/models.py`: Defines the strict data structures (Pydantic models) representing the expected JSON payload from GitHub.
*   `src/domain/exceptions.py`: Centralizes error definitions (e.g., `AuthenticationError`, `RateLimitError`).
*   `src/ingestion/github_client.py`: The primary engine for HTTP requests, utilizing libraries like `httpx` or `requests`. It consumes configuration, executes requests, parses JSON, and instantiates the domain models.
## System Architecture
The architecture for Cycle 01 centers on establishing the Ingestion Layer, ensuring clear separation from future processing and presentation logic.

```text
.
├── .env.example
├── src/
│   ├── __init__.py
│   ├── config.py             # Configuration management (dotenv)
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py         # Pydantic models for repo and commit data
│   │   └── exceptions.py     # Custom domain exceptions
│   └── ingestion/
│       ├── __init__.py
│       └── github_client.py  # Core HTTP client logic
└── tests/
    ├── conftest.py
    └── unit/
        └── test_github_client.py
```

*   `src/config.py`: Responsible for loading environment variables securely using `python-dotenv`.
*   `src/domain/models.py`: Defines the strict data structures (Pydantic models) representing the expected JSON payload from GitHub.
*   `src/domain/exceptions.py`: Centralizes error definitions (e.g., `AuthenticationError`, `RateLimitError`).
*   `src/ingestion/github_client.py`: The primary engine for HTTP requests, utilizing libraries like `httpx` or `requests`. It consumes configuration, executes requests, parses JSON, and instantiates the domain models.

## Design Architecture
This cycle relies heavily on Pydantic to define the system's contract with the external GitHub API.

*   **`domain.models.RepositoryMetadata`**: Represents the core information of a repository.
    *   *Constraints*: Owner and Repo name must be strings. Star count, fork count, and open issue count must be non-negative integers.
    *   *Consumers*: The future Transformation Layer and the Presentation Layer.
*   **`domain.models.CommitRecord`**: Represents an individual commit within the history.
    *   *Constraints*: Commit hash must be a string. Author name is a string. Date must be parsable into a Python `datetime` or `date` object.
    *   *Consumers*: The Transformation Layer for aggregation.
*   **Extensibility**: By defining these as base Pydantic models, we allow for future attributes (e.g., repository language, pull request counts) to be added effortlessly without breaking existing validation logic. The strict typing ensures that the system fails fast if the GitHub API payload unexpectedly changes format.
## Design Architecture
This cycle relies heavily on Pydantic to define the system's contract with the external GitHub API.

*   **`domain.models.RepositoryMetadata`**: Represents the core information of a repository.
    *   *Constraints*: Owner and Repo name must be strings. Star count, fork count, and open issue count must be non-negative integers.
    *   *Consumers*: The future Transformation Layer and the Presentation Layer.
*   **`domain.models.CommitRecord`**: Represents an individual commit within the history.
    *   *Constraints*: Commit hash must be a string. Author name is a string. Date must be parsable into a Python `datetime` or `date` object.
    *   *Consumers*: The Transformation Layer for aggregation.
*   **Extensibility**: By defining these as base Pydantic models, we allow for future attributes (e.g., repository language, pull request counts) to be added effortlessly without breaking existing validation logic. The strict typing ensures that the system fails fast if the GitHub API payload unexpectedly changes format.
## Design Architecture
This cycle relies heavily on Pydantic to define the system's contract with the external GitHub API.

*   **`domain.models.RepositoryMetadata`**: Represents the core information of a repository.
    *   *Constraints*: Owner and Repo name must be strings. Star count, fork count, and open issue count must be non-negative integers.
    *   *Consumers*: The future Transformation Layer and the Presentation Layer.
*   **`domain.models.CommitRecord`**: Represents an individual commit within the history.
    *   *Constraints*: Commit hash must be a string. Author name is a string. Date must be parsable into a Python `datetime` or `date` object.
    *   *Consumers*: The Transformation Layer for aggregation.
*   **Extensibility**: By defining these as base Pydantic models, we allow for future attributes (e.g., repository language, pull request counts) to be added effortlessly without breaking existing validation logic. The strict typing ensures that the system fails fast if the GitHub API payload unexpectedly changes format.

## Implementation Approach
1.  **Environment Setup**: Install `python-dotenv`, `pydantic`, and an HTTP client like `httpx`. Ensure `pytest` and `pytest-mock` are ready.
2.  **Configuration Management**: Implement `config.py` to read the `.env` file and expose the `GITHUB_TOKEN`. Validate that the token is present.
3.  **Domain Models**: Define `RepositoryMetadata` and `CommitRecord` in `models.py` using Pydantic, aligning fields with the expected GitHub API JSON response. Define custom exceptions in `exceptions.py`.
4.  **API Client Implementation**: Create `github_client.py`. Implement functions to fetch repository info and the latest 100 commits.
5.  **Error Handling**: Integrate `try...except` blocks within the client to catch HTTP errors (status codes 401, 403, 404, 429) and raise the corresponding custom domain exceptions. Ensure headers include the authorization token securely.
6.  **Data Parsing**: Ensure the client parses the raw JSON directly into the defined Pydantic models before returning the data to the caller.
## Implementation Approach
1.  **Environment Setup**: Install `python-dotenv`, `pydantic`, and an HTTP client like `httpx`. Ensure `pytest` and `pytest-mock` are ready.
2.  **Configuration Management**: Implement `config.py` to read the `.env` file and expose the `GITHUB_TOKEN`. Validate that the token is present.
3.  **Domain Models**: Define `RepositoryMetadata` and `CommitRecord` in `models.py` using Pydantic, aligning fields with the expected GitHub API JSON response. Define custom exceptions in `exceptions.py`.
4.  **API Client Implementation**: Create `github_client.py`. Implement functions to fetch repository info and the latest 100 commits.
5.  **Error Handling**: Integrate `try...except` blocks within the client to catch HTTP errors (status codes 401, 403, 404, 429) and raise the corresponding custom domain exceptions. Ensure headers include the authorization token securely.
6.  **Data Parsing**: Ensure the client parses the raw JSON directly into the defined Pydantic models before returning the data to the caller.
## Implementation Approach
1.  **Environment Setup**: Install `python-dotenv`, `pydantic`, and an HTTP client like `httpx`. Ensure `pytest` and `pytest-mock` are ready.
2.  **Configuration Management**: Implement `config.py` to read the `.env` file and expose the `GITHUB_TOKEN`. Validate that the token is present.
3.  **Domain Models**: Define `RepositoryMetadata` and `CommitRecord` in `models.py` using Pydantic, aligning fields with the expected GitHub API JSON response. Define custom exceptions in `exceptions.py`.
4.  **API Client Implementation**: Create `github_client.py`. Implement functions to fetch repository info and the latest 100 commits.
5.  **Error Handling**: Integrate `try...except` blocks within the client to catch HTTP errors (status codes 401, 403, 404, 429) and raise the corresponding custom domain exceptions. Ensure headers include the authorization token securely.
6.  **Data Parsing**: Ensure the client parses the raw JSON directly into the defined Pydantic models before returning the data to the caller.

## Test Strategy

### Unit Testing Approach
The unit tests must rigorously verify the logic within `github_client.py` and the Pydantic models without making actual network requests.
*   **Mocking**: Use `pytest-mock` to intercept calls made by `httpx.get` (or `requests.get`).
*   **Success Scenarios**: Configure the mock to return predefined, valid JSON strings representing repository metadata and commit histories. Assert that the client correctly parses this mock data into the appropriate Pydantic models and that the values match precisely.
*   **Error Handling Verification**: Configure the mock to return HTTP error status codes (e.g., 404 Not Found, 403 Forbidden). Assert that the client intercepts these responses and raises the correct custom exceptions defined in `domain/exceptions.py`.
*   **Configuration Tests**: Verify that `config.py` correctly loads the token from a mock environment and fails gracefully if the environment variable is missing.

### Integration Testing Approach
Integration tests will verify the contract between the configuration, the client, and the domain models.
*   While avoiding actual API calls is preferred for sandbox stability, a specifically marked integration test (e.g., `@pytest.mark.live`) can be implemented to hit a highly available, public repository (like `torvalds/linux`) to ensure the real-world JSON payload matches the assumptions hardcoded into the Pydantic models. This live test must be explicitly segregated and not run during standard CI unless a token is injected.
## Test Strategy

### Unit Testing Approach
The unit tests must rigorously verify the logic within `github_client.py` and the Pydantic models without making actual network requests.
*   **Mocking**: Use `pytest-mock` to intercept calls made by `httpx.get` (or `requests.get`).
*   **Success Scenarios**: Configure the mock to return predefined, valid JSON strings representing repository metadata and commit histories. Assert that the client correctly parses this mock data into the appropriate Pydantic models and that the values match precisely.
*   **Error Handling Verification**: Configure the mock to return HTTP error status codes (e.g., 404 Not Found, 403 Forbidden). Assert that the client intercepts these responses and raises the correct custom exceptions defined in `domain/exceptions.py`.
*   **Configuration Tests**: Verify that `config.py` correctly loads the token from a mock environment and fails gracefully if the environment variable is missing.

### Integration Testing Approach
Integration tests will verify the contract between the configuration, the client, and the domain models.
*   While avoiding actual API calls is preferred for sandbox stability, a specifically marked integration test (e.g., `@pytest.mark.live`) can be implemented to hit a highly available, public repository (like `torvalds/linux`) to ensure the real-world JSON payload matches the assumptions hardcoded into the Pydantic models. This live test must be explicitly segregated and not run during standard CI unless a token is injected.
## Test Strategy

### Unit Testing Approach
The unit tests must rigorously verify the logic within `github_client.py` and the Pydantic models without making actual network requests.
*   **Mocking**: Use `pytest-mock` to intercept calls made by `httpx.get` (or `requests.get`).
*   **Success Scenarios**: Configure the mock to return predefined, valid JSON strings representing repository metadata and commit histories. Assert that the client correctly parses this mock data into the appropriate Pydantic models and that the values match precisely.
*   **Error Handling Verification**: Configure the mock to return HTTP error status codes (e.g., 404 Not Found, 403 Forbidden). Assert that the client intercepts these responses and raises the correct custom exceptions defined in `domain/exceptions.py`.
*   **Configuration Tests**: Verify that `config.py` correctly loads the token from a mock environment and fails gracefully if the environment variable is missing.

### Integration Testing Approach
Integration tests will verify the contract between the configuration, the client, and the domain models.
*   While avoiding actual API calls is preferred for sandbox stability, a specifically marked integration test (e.g., `@pytest.mark.live`) can be implemented to hit a highly available, public repository (like `torvalds/linux`) to ensure the real-world JSON payload matches the assumptions hardcoded into the Pydantic models. This live test must be explicitly segregated and not run during standard CI unless a token is injected.
