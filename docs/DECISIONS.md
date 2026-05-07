# Architecture & Design Rationale

## Pydantic Domain Models
When fetching raw data from GitHub's REST API, the payload is extremely large, often containing dozens of fields we do not intend to use. Therefore, rather than strictly rejecting extra fields via `extra="forbid"`, we use `extra="ignore"` for the `RepositoryInfo` and `CommitData` domain models. This prevents `ValidationError` on massive third-party JSON data and allows us to safely ingest and flatten the specific fields we need while retaining strict typing.
