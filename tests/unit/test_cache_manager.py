from pathlib import Path
from unittest.mock import MagicMock, patch

import polars as pl

from src.processing.cache_manager import (
    load_from_cache,
    load_metadata_cache,
    save_metadata_cache,
    save_to_cache,
)


@patch("src.processing.cache_manager.CACHE_DIR")
def test_save_and_load_cache(mock_dir: MagicMock, tmp_path: Path) -> None:
    mock_dir.exists.return_value = True
    mock_dir.__truediv__.return_value = tmp_path / "test_key.parquet"

    df = pl.DataFrame({"a": [1, 2, 3]})
    save_to_cache("test/key", df)

    loaded = load_from_cache("test/key")
    assert loaded is not None
    assert loaded.equals(df)

@patch("src.processing.cache_manager.CACHE_DIR")
def test_load_cache_miss(mock_dir: MagicMock, tmp_path: Path) -> None:
    mock_dir.exists.return_value = True
    mock_dir.__truediv__.return_value = tmp_path / "missing.parquet"

    loaded = load_from_cache("missing")
    assert loaded is None

@patch("src.processing.cache_manager.CACHE_DIR")
def test_load_corrupted_cache(mock_dir: MagicMock, tmp_path: Path) -> None:
    mock_dir.exists.return_value = True
    bad_file = tmp_path / "bad.parquet"
    bad_file.write_text("not a parquet file")
    mock_dir.__truediv__.return_value = bad_file

    loaded = load_from_cache("bad")
    assert loaded is None

@patch("src.processing.cache_manager.CACHE_DIR")
def test_metadata_cache(mock_dir: MagicMock, tmp_path: Path) -> None:
    mock_dir.exists.return_value = True
    mock_dir.__truediv__.return_value = tmp_path / "meta.json"

    save_metadata_cache("meta", {"hello": "world"})
    loaded = load_metadata_cache("meta")
    assert loaded == {"hello": "world"}

@patch("src.processing.cache_manager.CACHE_DIR")
def test_metadata_cache_corrupted(mock_dir: MagicMock, tmp_path: Path) -> None:
    mock_dir.exists.return_value = True
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not a json file")
    mock_dir.__truediv__.return_value = bad_file

    loaded = load_metadata_cache("bad")
    assert loaded is None
