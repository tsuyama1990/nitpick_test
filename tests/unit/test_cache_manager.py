import os
import sys
import time
from pathlib import Path

# Fix module imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import polars as pl
from pytest_mock import MockerFixture

from src.cache_manager import load_from_cache, save_to_cache


def test_cache_manager_save_and_load(tmp_path: Path, mocker: MockerFixture) -> None:
    # Set cache dir to tmp_path
    mock_settings = mocker.patch("src.cache_manager.get_settings").return_value
    mock_settings.CACHE_DIR = str(tmp_path)
    mock_settings.CACHE_TTL_SECONDS = 3600

    df = pl.DataFrame({"date": ["2023-01-01"], "commit_count": [5]})
    repo_name = "test_owner/test_repo"

    # Save
    save_to_cache(repo_name, df)

    # Load
    loaded_df = load_from_cache(repo_name)
    assert loaded_df is not None
    assert loaded_df.equals(df)


def test_cache_manager_ttl_expiry(tmp_path: Path, mocker: MockerFixture) -> None:
    mock_settings = mocker.patch("src.cache_manager.get_settings").return_value
    mock_settings.CACHE_DIR = str(tmp_path)
    mock_settings.CACHE_TTL_SECONDS = 3600

    df = pl.DataFrame({"date": ["2023-01-01"], "commit_count": [5]})
    repo_name = "test_owner/test_repo_expired"

    # Save
    save_to_cache(repo_name, df)

    # Manually modify the file timestamp to simulate an expired cache (> 3600s)
    cache_file = tmp_path / "test_owner_test_repo_expired_commits.parquet"
    past_time = time.time() - 4000
    os.utime(cache_file, (past_time, past_time))

    # Load should return None
    loaded_df = load_from_cache(repo_name)
    assert loaded_df is None


def test_load_from_cache_not_exist(tmp_path: Path, mocker: MockerFixture) -> None:
    mock_settings = mocker.patch("src.cache_manager.get_settings").return_value
    mock_settings.CACHE_DIR = str(tmp_path)
    mock_settings.CACHE_TTL_SECONDS = 3600

    loaded_df = load_from_cache("non_existent/repo")
    assert loaded_df is None
