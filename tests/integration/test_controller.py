from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from src.application.controller import orchestrate_repository_processing
from src.domain_models import CommitRecord
from src.processing.cache_manager import save_to_cache


def test_orchestrate_repository_processing_cache_miss(tmp_path: Path) -> None:
    repo_name = "test/repo_miss"

    # Mock API fetch that we know gets called
    called = False

    def mock_fetch(repo: str) -> list[CommitRecord]:
        nonlocal called
        called = True
        return [
            CommitRecord(commit_hash="123", author="alice", date=datetime(2023, 1, 1, tzinfo=UTC))
        ]

    from src.config import settings

    settings.cache_dir = tmp_path

    df = orchestrate_repository_processing(repo_name, mock_fetch)

    assert called is True
    assert isinstance(df, pl.DataFrame)
    assert len(df) == 1


def test_orchestrate_repository_processing_cache_hit(tmp_path: Path) -> None:
    repo_name = "test/repo_hit"

    # Pre-populate cache
    df_cache = pl.DataFrame({"date": ["2023-01-01"], "commit_count": [1]})

    from src.config import settings

    settings.cache_dir = tmp_path
    save_to_cache(repo_name, df_cache)

    called = False

    def mock_fetch(repo: str) -> list[CommitRecord]:
        nonlocal called
        called = True
        return []

    df = orchestrate_repository_processing(repo_name, mock_fetch)

    assert called is False
    assert isinstance(df, pl.DataFrame)
    assert len(df) == 1
