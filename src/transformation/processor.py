import os
import pathlib
import time

import polars as pl

from src.domain_models.github import CommitInfo


def aggregate_commits_per_day(commits: list[CommitInfo]) -> pl.DataFrame:
    if not commits:
        return pl.DataFrame(
            {"date": [], "commit_count": []}, schema={"date": pl.String, "commit_count": pl.UInt32}
        )

    data = [{"date": c.date.strftime("%Y-%m-%d")} for c in commits]
    df = pl.DataFrame(data)

    return df.group_by("date").len(name="commit_count").sort("date")


def get_top_committers(commits: list[CommitInfo]) -> pl.DataFrame:
    if not commits:
        return pl.DataFrame(
            {"name": [], "commit_count": []}, schema={"name": pl.String, "commit_count": pl.UInt32}
        )

    data = [{"name": c.name} for c in commits]
    df = pl.DataFrame(data)

    return (
        df.group_by("name").len(name="commit_count").sort("commit_count", descending=True).head(5)
    )


def get_cache_path(filename: str) -> pathlib.Path:
    cache_dir_env = os.getenv("CACHE_DIR")
    if cache_dir_env:
        cache_dir = pathlib.Path(cache_dir_env)
    else:
        cache_dir = pathlib.Path.cwd() / ".cache" / "github_poc"

    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / filename


def load_from_cache(filename: str, ttl_seconds: int = 3600) -> pl.DataFrame | None:
    filepath = get_cache_path(filename)
    if not filepath.exists():
        return None

    mtime = filepath.stat().st_mtime
    if time.time() - mtime > ttl_seconds:
        return None

    try:
        return pl.read_parquet(filepath)
    except Exception:
        return None


def save_to_cache(df: pl.DataFrame, filename: str) -> None:
    filepath = get_cache_path(filename)
    df.write_parquet(filepath)
