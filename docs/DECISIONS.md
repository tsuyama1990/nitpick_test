# Architecture & Design Rationale

## Pydantic Models: `extra="ignore"` vs `extra="forbid"`
- **Settings Model:** Uses `extra="forbid"` to strictly ensure that no extraneous or misspelled environment variables are ingested, preventing misconfiguration.
- **API Models (GitHub):** Uses `extra="ignore"`. The GitHub API returns massive payloads with many fields not needed by our application. Ignoring extras allows us to safely extract only what is needed (e.g. `stargazers_count`) without failing when GitHub adds new fields. Flattening nested JSON is handled via a `@model_validator(mode="before")`.

## Data Transformation
Polars is used for data manipulation to quickly aggregate daily commit counts and top committers, providing a faster and memory-efficient alternative to Pandas.

## Caching Strategy
A 1-hour local caching system using Parquet format via `pyarrow`. File modification times (`st_mtime`) are checked against current `time.time()` to enforce the TTL without complex database tracking.
