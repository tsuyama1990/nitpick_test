from dataclasses import dataclass

import polars as pl

from src.domain_models.github import RepoInfo


@dataclass
class DashboardResult:
    """Data Transfer Object containing the aggregated dashboard metrics."""

    repo_info: RepoInfo
    commits_by_date: pl.DataFrame
    top_committers: pl.DataFrame
    cached: bool
