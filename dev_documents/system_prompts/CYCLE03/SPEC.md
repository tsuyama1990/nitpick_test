# CYCLE03: Data Transformation (Polars)

## Summary

In Cycle 03, we build the Data Transformation Layer. The goal is to process the raw, strictly typed lists of `CommitData` objects acquired in Cycle 02 into aggregated metrics suitable for caching and visualization. Polars will be utilized for its high-performance, vectorized operations. We need to aggregate the data to calculate the number of commits per date, and identify the top 5 committers. This layer must remain purely functional, devoid of side-effects or network calls.

## Infrastructure & Dependencies

### A. Project Secrets (`.env.example`)
- Maintained from Cycle 01.

### B. System Configurations (`docker-compose.yml`)
- Maintained from Cycle 01.

### C. Sandbox Resilience (CRITICAL TEST STRATEGY)
- **Mandate Mocking:** This cycle operates strictly on in-memory data structures (Polars DataFrames and Pydantic models). No external API calls are made. Tests should utilize statically defined Pydantic objects or dictionaries to ensure zero network dependency.

## System Architecture

The following directories and files must be implemented or modified:

.
├── src/
│   ├── domain_models/
│   │   └── commit.py
│   └── transformation/
│       ├── **__init__.py**
│       └── **polars_processor.py**
└── tests/
    └── **test_transformation.py**

## Design Architecture

**PolarsProcessor (`src/transformation/polars_processor.py`)**
- A functional module that transforms Pydantic lists into Polars DataFrames and performs aggregations.
- Methods:
  - `to_dataframe(commits: list[CommitData]) -> pl.DataFrame`: Converts the typed list into a Polars DataFrame. Ensures the date column is correctly typed as Datetime/Date.
  - `aggregate_commits_by_date(df: pl.DataFrame) -> pl.DataFrame`: Groups by the date part of the timestamp and counts occurrences.
  - `aggregate_top_committers(df: pl.DataFrame, top_n: int = 5) -> pl.DataFrame`: Groups by `author_name`, counts occurrences, sorts descending, and limits to `top_n`.
- Constraints: The transformation layer must not mutate the input list. It must strictly return new Polars DataFrames.
- Consumers: The Storage layer (for caching) and the Controller (for rendering).
- Producers: Receives data strictly typed by `CommitData`.

## Implementation Approach

1. **Init File**: Ensure `src/transformation/__init__.py` exists.
2. **Implement Processor**: Create `src/transformation/polars_processor.py`.
3. **DataFrame Conversion**: Implement `to_dataframe`. Use `[commit.model_dump() for commit in commits]` to extract data and pass it to `pl.DataFrame()`.
4. **Date Aggregation**: Implement `aggregate_commits_by_date`. Use Polars expressions: `df.group_by(pl.col('date').dt.date()).agg(pl.count().alias('commit_count')).sort('date')`.
5. **Committer Aggregation**: Implement `aggregate_top_committers`. Use Polars expressions: `df.group_by('author_name').agg(pl.count().alias('commit_count')).sort('commit_count', descending=True).head(top_n)`.
6. **Linting and Typing**: Execute `uv run ruff check .` and `uv run mypy .`. Resolve any type errors stemming from Polars type hints.

## Test Strategy

**Unit Testing Approach (Min 300 words)**
Testing the transformation layer requires synthesizing mocked `CommitData` Pydantic objects to simulate a real API payload. We will construct a list of objects featuring varying authors and dates. For `to_dataframe`, we will assert that the resulting Polars DataFrame possesses the correct shape and column types (e.g., asserting the date column is a Polars Datetime type). For `aggregate_commits_by_date`, we will craft inputs with multiple commits on the same day and across different days, asserting that the Polars grouping logic accurately sums the counts and sorts them chronologically.

**Integration Testing Approach (Min 300 words)**
To integrate test the committer aggregation logic (`aggregate_top_committers`), we will feed a DataFrame populated with skewed commit frequencies (e.g., Author A has 10 commits, Author B has 5, Author C has 1, plus several others with 1 commit). The test will verify that the function accurately groups the authors, sorts them in strictly descending order, and truncates the output to exactly the `top_n` threshold (defaulting to 5). Crucially, we will verify behavior under edge conditions, such as ties in commit counts and scenarios where the total number of unique authors is fewer than 5, ensuring the DataFrame does not crash and returns the correct subset of data.
