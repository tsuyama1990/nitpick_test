# CYCLE01: System Setup, Domain Models & Configuration (UAT)

## Test Scenarios

### Scenario 1: Strict Environment Configuration Verification
**ID**: UAT-C01-01
**Priority**: High
**Description**: Verify that the system correctly mandates the presence of secure configuration variables and prevents application start if secrets are missing. This is a foundational scenario, ensuring we never run the app without the required GitHub token, avoiding immediate rate-limits. Since this is an internal schema cycle, verification will be done via Marimo notebook testing the configuration loader logic.

### Scenario 2: Data Schema Flattening and Validation
**ID**: UAT-C01-02
**Priority**: High
**Description**: Prove that the application can correctly ingest deeply nested, chaotic JSON payloads from GitHub and cleanly flatten them into our robust, typed Domain Models. We want to ensure that massive API payloads do not crash the system due to unexpected fields, keeping the data layer pristine.

## Behavior Definitions

### UAT-C01-01: Strict Environment Configuration Verification
**GIVEN** the application environment is missing the `GITHUB_TOKEN` variable
**WHEN** the configuration loader (`get_settings()`) is invoked
**THEN** the system must raise a clear validation error preventing initialization
**AND** it must not log any fallback dummy tokens to the console

**GIVEN** a valid `GITHUB_TOKEN` exists in the environment variables
**WHEN** the configuration loader is invoked
**THEN** the `AppConfig` object is successfully instantiated containing the token
**AND** an attempt to inject arbitrary extra configuration variables must be strictly forbidden by the system (throwing an `extra_forbidden` error).

### UAT-C01-02: Data Schema Flattening and Validation
**GIVEN** a massive, complex dictionary representing a raw GitHub Repository API payload with hundreds of extraneous fields
**WHEN** the `RepositoryInfo` model processes the dictionary
**THEN** it successfully instantiates without validation errors
**AND** it safely ignores all extra fields
**AND** successfully types `stargazers_count` and `forks_count` as integers.

**GIVEN** a heavily nested dictionary representing a raw GitHub Commit API payload (e.g., `payload['commit']['author']['name']`)
**WHEN** the `CommitData` model processes the payload
**THEN** the pre-validator traverses the nesting
**AND** flattens the data into an object where `author_name` is directly accessible at the top level
**AND** the timestamp is strictly verified as a valid Python Datetime object.
