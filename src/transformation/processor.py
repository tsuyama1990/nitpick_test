import polars as pl

from src.domain_models.github import CommitDetail


def process_commits_per_day(commits: list[CommitDetail]) -> pl.DataFrame:
    """Aggregate commits by date (YYYY-MM-DD)."""
    if not commits:
        return pl.DataFrame({"date": [], "commit_count": []})

    # Convert to list of dicts, ensuring author_date is isolated correctly
    data = [{"date": commit.author_date.date()} for commit in commits]
    df = pl.DataFrame(data)

    return df.group_by("date").agg(pl.len().alias("commit_count")).sort("date", descending=True)


def process_commits_per_committer(commits: list[CommitDetail]) -> pl.DataFrame:
    """Aggregate commits by committer, taking the top 5."""
    if not commits:
        return pl.DataFrame({"author_name": [], "commit_count": []})

    data = [{"author_name": commit.author_name} for commit in commits]
    df = pl.DataFrame(data)

    return (
        df.group_by("author_name")
        .agg(pl.len().alias("commit_count"))
        .sort("commit_count", descending=True)
        .head(5)
    )
