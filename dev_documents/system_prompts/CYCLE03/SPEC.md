# Cycle 03: Polars Data Transformations Specification

## Summary
This cycle implements the core analytical engine of the dashboard. The primary objective is to build pure, side-effect-free transformation functions using the Polars library. These functions will accept the raw, validated JSON data (now structured via Pydantic models from Cycle 01) and perform complex aggregations required by the UI: calculating the number of commits per day and determining the top committers. This cycle strictly isolates the data processing logic from both network ingestion (Cycle 02) and visualization (Cycle 06). By leveraging Polars, the system guarantees high-performance tabular data manipulation with strict schema enforcement, ensuring the downstream application receives clean, pre-calculated datasets ready for rendering.

## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
This cycle focuses purely on data transformation and requires no external API keys or secrets.

### B. System Configurations (`docker-compose.yml`)
No specific docker configurations are required. The processing relies entirely on the local Python runtime environment.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
**MANDATORY INSTRUCTION:** The transformation logic must be tested entirely in isolation using static mock datasets.
- Tests must instantiate Polars DataFrames using hardcoded lists of dictionaries representing the expected API output.
- No network requests (real or mocked via `httpx`) are necessary or permitted during these unit tests. This ensures tests remain lightning fast and completely resilient against any external environmental factors.

## System Architecture
The file structure introduces the processing module. The files explicitly marked in bold represent the targets for creation during this cycle.

```text
.
├── src/
│   ├── domain_models/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── manifest.py
│   │   └── schemas.py
│   └── processing/
│       ├── __init__.py
│       └── **transformations.py**
└── tests/
    ├── unit/
    │   └── **test_processing.py**
    ├── e2e/
    │   └── **test_processing_e2e.py**
    └── uat/
        └── **uat_script.py**
```

## Design Architecture
The design for the Transformation Layer focuses on functional purity within `src/processing/transformations.py`.

The module will expose two primary functions:
1. `aggregate_commits_by_date(raw_commits: list[dict]) -> pl.DataFrame`: This function accepts the raw list of dictionaries returned by the GitHub API. Its first responsibility is to validate this input against the `CommitItem` Pydantic model to ensure the payload conforms to the expected shape. Once validated, the data is loaded into a Polars DataFrame. The core logic involves extracting the date portion from the datetime string (or object), grouping the DataFrame by this date column, and counting the occurrences to produce a two-column DataFrame: `date` and `commit_count`. The schema of the resulting DataFrame must be strictly enforced (e.g., `date` column must be Polars Date/Datetime type, `commit_count` must be an integer).

2. `get_top_committers(raw_commits: list[dict], top_n: int = 5) -> pl.DataFrame`: Similar to the above, this function validates the input data and loads it into Polars. The aggregation logic groups by the author's name, counts the commits, sorts the result in descending order by the count, and then limits the output to the specified `top_n` rows. **Crucial Invariant:** To ensure deterministic testing and prevent unpredictable ties when multiple authors have the exact same number of commits, the sorting operation *must* include a secondary stable sort key (e.g., sorting descending by count, then ascending by author name alphabetically).

These functions act as strict boundaries. They take primitive types (lists of dicts) representing the external API payload, use Pydantic for validation, use Polars for calculation, and return primitive analytic types (Polars DataFrames) ready for caching or UI consumption.

## Implementation Approach
1. **Dependency Verification:** Ensure `polars` and `pydantic` are properly installed in the `uv` environment.
2. **Implement Transformation Module:** Create `src/processing/transformations.py`. Import `polars as pl` and the relevant schemas from `src.domain_models.schemas`.
3. **Implement Date Aggregation:** Define `aggregate_commits_by_date`.
   - Iterate over the `raw_commits` and instantiate the `CommitItem` model to validate the data. Extract the necessary fields (date) into a flat list of dictionaries suitable for Polars initialization.
   - Initialize a `pl.DataFrame` from the flattened data.
   - Use Polars expressions (e.g., `df.with_columns(pl.col("date").cast(pl.Date))`) to ensure schema correctness.
   - Use `df.group_by("date").agg(pl.len().alias("commit_count")).sort("date")` to perform the aggregation.
   - Return the resulting DataFrame directly (do not assign to a temporary variable to satisfy Ruff `RET504`).
4. **Implement Committer Aggregation:** Define `get_top_committers`.
   - Validate and flatten the input data, extracting the author name.
   - Initialize the `pl.DataFrame`.
   - Use `df.group_by("name").agg(pl.len().alias("commit_count"))`.
   - Apply the critical stable sort: `.sort(["commit_count", "name"], descending=[True, False])`.
   - Limit the result using `.head(top_n)`.
   - Return the DataFrame.

## Test Strategy

### Unit Testing Approach
Unit testing will reside in `tests/test_processing.py`. This phase demands meticulous testing of edge cases and data validation.
- **Valid Data Aggregation:** Create a mock list of dictionary payloads representing 10 commits spread across 3 different days by 4 different authors. Pass this to both functions. Assert that the resulting `pl.DataFrame` has the correct schema (columns and data types) and the mathematically correct counts (using `df.filter` or converting to dicts for assertion).
- **Empty Dataset Handling:** Pass an empty list `[]` to both functions. Assert that they return an empty `pl.DataFrame` with the correct column schemas rather than crashing.
- **Deterministic Sorting (Top Committers):** Create a specific mock payload where 3 authors all have exactly 2 commits. Pass this to `get_top_committers(..., top_n=2)`. Assert that the returned authors strictly follow the secondary alphabetical sort order, proving the tie-breaking logic works and tests remain deterministic.
- **Pydantic Validation Integration:** Pass a malformed mock payload (e.g., missing the author date field). Assert that the function immediately raises a Pydantic `ValidationError` before any Polars processing begins.
