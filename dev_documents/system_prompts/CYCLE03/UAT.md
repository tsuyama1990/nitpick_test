# CYCLE03: Data Transformation (Polars) (UAT)

## Test Scenarios

### Scenario 1: Accurate Date Aggregation
**ID**: UAT-C03-01
**Priority**: High
**Description**: Verify that the Polars processing engine correctly groups continuous streams of timestamps into daily buckets, summing the commits correctly for chronological charting.

### Scenario 2: Accurate Leaderboard Extraction (Top 5)
**ID**: UAT-C03-02
**Priority**: High
**Description**: Prove that the engine can accurately identify and extract the most active developers from a noisy list of commits, handling sorting and thresholding correctly.

## Behavior Definitions

### UAT-C03-01: Accurate Date Aggregation
**GIVEN** a dataset containing 10 commits spread across 3 unique days (e.g., 5 on Monday, 3 on Tuesday, 2 on Wednesday)
**WHEN** the dataset is processed by `aggregate_commits_by_date`
**THEN** the resulting DataFrame has exactly 3 rows
**AND** the `commit_count` column matches the expected distribution (5, 3, 2)
**AND** the data is sorted chronologically by date.

### UAT-C03-02: Accurate Leaderboard Extraction (Top 5)
**GIVEN** a dataset containing commits from 10 distinct authors with varying frequencies
**WHEN** the dataset is processed by `aggregate_top_committers`
**THEN** the resulting DataFrame has exactly 5 rows
**AND** the author with the highest frequency is in the first row
**AND** the counts are in strictly descending order.

**GIVEN** a dataset containing commits from only 3 distinct authors
**WHEN** the dataset is processed by `aggregate_top_committers` with `top_n=5`
**THEN** the resulting DataFrame has exactly 3 rows (no crashes or padded dummy rows).
