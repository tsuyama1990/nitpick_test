GitHubリポジトリ分析ダッシュボードのPoC構築 (Live API E2E)
以下の要件定義に従い、Python（Polars + Streamlit）を用いたGitHubリポジトリの簡易分析システムのPoCを構築してください。
本プロジェクトでは、実際のGitHub REST APIへ接続し、E2Eで動作検証を行うことを必須とします。

必須要件（環境変数とシークレット管理）
クレデンシャルの分離: GitHub APIの認証情報（Personal Access Token）はコード内に絶対にハードコードしないでください。

.envの利用: python-dotenv などを利用し、実行環境のルートにある .env ファイルから環境変数を読み込む設計としてください。

.env.exampleの作成: リポジトリにコミットするための雛形として、キー名のみを記載した（値は空の）.env.example を必ず作成してください。

セキュリティ: デバッグ用のprint文やロガーで、取得したトークンを出力しないよう厳密にコーディングしてください。

開発サイクル指定 (全3サイクル)
Cycle 1: APIクライアントとデータ抽出 (Ingestion)
API Ingestion: 実際のGitHub REST APIに接続し、指定したリポジトリ（例: streamlit/streamlit）の「基本情報（スター数、フォーク数）」と「直近100件のコミット履歴」を取得するモジュールを実装すること。

.env からGitHubトークンを読み込み、リクエストヘッダに付与すること。

認証エラーやレートリミット（403/429エラー）の例外処理を実装すること。

APIのレスポンスをそのまま返す関数として定義すること。
期待する成果物: .envから認証情報を読み込み、実APIからJSONデータを取得できるPythonスクリプトと、それを検証するPytest（通信を伴うLive Testを含む）。

Cycle 2: データ加工とローカルキャッシュ (Transformation & Storage)
Transformation: Cycle 1で取得したJSONデータをPolarsを用いて以下のテーブルに加工するモジュール。

コミット履歴から、「日付（YYYY-MM-DD）ごとのコミット数」を集計したデータフレームを作成。

コミット履歴から、「コミッター別のコミット数（上位5名）」を集計したデータフレームを作成。

Storage: APIへの過剰なリクエストを防ぐため、加工済みのデータを .parquet または .csv 形式でローカルの一時ディレクトリに保存し、次回以降はキャッシュから読み込む機能（TTL: 1時間など簡易的なもので可）を実装すること。
期待する成果物: APIからのレスポンスをPolarsで処理し、意図した集計結果が得られること、およびファイルへの保存・読み込みが正常に行われることを検証するPytest。

Cycle 3: Web UIの構築 (Visualization)
Streamlit App: Cycle 2の処理結果をブラウザで表示するためのStreamlitアプリケーションを構築すること。

入力項目: ユーザーが「オーナー名/リポジトリ名」を入力できるテキストボックス。

メトリクス表示: リポジトリの基本情報（スター数、フォーク数、オープンIssue数）をKPIとして画面上部に表示。

グラフ表示: Streamlitの標準機能（st.line_chart または st.bar_chart）を利用し、「日付ごとのコミット数推移」および「コミッター別コミット数」のチャートを描画すること。
期待する成果物: streamlit run コマンドで起動し、UI上でリポジトリ名を指定するとAPIからデータが取得され、画面上にエラーなくメトリクスとグラフが表示される統合されたアプリケーションコード。
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
# CYCLE 01 UAT: API Client Validation

## Test Scenarios

### Scenario ID: C01-01 - Successful Data Extraction
*   **Priority**: High
*   **Description**: Verify that the implemented API client can successfully connect to the official GitHub API, authenticate securely using the provided token, and retrieve strictly typed repository metadata and a complete commit history for a known, highly stable public repository. This crucial scenario ensures the foundational ingestion layer operates absolutely flawlessly under ideal, expected conditions.
*   **Execution Strategy**: An interactive Marimo notebook (`tutorials/UAT_AND_TUTORIAL.py`) will be executed. It will instantiate the `github_client` with valid, secure credentials and deliberately invoke the fetch methods against a well-known repository like `streamlit/streamlit`. The resulting output will be visually inspected within the notebook cells to explicitly confirm the return types are indeed the expected, strictly validated Pydantic models.

### Scenario ID: C01-02 - Error Handling for Invalid Repositories
*   **Priority**: High
*   **Description**: Ensure the implemented API client gracefully handles requests for completely non-existent or deleted repositories (HTTP 404 Not Found). It must prove it raises a highly specific, catchable custom Python domain exception rather than crashing catastrophically or exposing raw, unintelligible HTTP library stack traces to the caller.
*   **Execution Strategy**: The interactive Marimo notebook will invoke the HTTP client against an intentionally invalid string, such as `invalid-owner/non-existent-repo-12345`, and programmatically assert that a descriptive `RepositoryNotFoundError` (or an equivalent custom exception) is correctly raised by the ingestion layer.

### Scenario ID: C01-03 - Authentication Failure Handling
*   **Priority**: Critical
*   **Description**: Validate the system's resilience against invalid or expired authentication tokens. The client must instantly recognize an HTTP 401/403 Unauthorized response and translate it into a secure, domain-specific error, absolutely guaranteeing the invalid token string is never leaked in the generated error message or system logs.
*   **Execution Strategy**: The Marimo notebook environment will be temporarily configured with a mathematically invalid token string (e.g., `ghp_invalidtoken123`). The client will attempt a data fetch. The test will rigorously assert that an `AuthenticationError` is raised and string-search the exception message to prove the secret is not present.

## Behavior Definitions

**Given** a valid `.env` file containing a correct `GITHUB_TOKEN`,
**When** the API client requests metadata for `streamlit/streamlit`,
**Then** the client must return a mathematically validated `RepositoryMetadata` object containing perfectly accurate star and fork counts matching the live GitHub repository state.

**Given** a missing or intentionally invalid `GITHUB_TOKEN` injected into the environment,
**When** the API client attempts to authenticate with the GitHub REST API,
**Then** the client must rapidly intercept the failure and raise an `AuthenticationError` securely, without logging or exposing the invalid token string in the error message.

**Given** a user input representing a repository that does not exist on GitHub,
**When** the API client executes the HTTP GET request and receives a 404 status code,
**Then** the client must catch the underlying HTTP error and translate it by raising a clearly defined `RepositoryNotFoundError` exception.
