import pytest

from src.domain_models import RepositoryNotFoundError
from src.presentation.app import mock_fetch_commits, mock_fetch_metadata


def test_mock_fetch_metadata():
    with pytest.raises(RepositoryNotFoundError, match="The specified repository was not found."):
        mock_fetch_metadata("invalid-owner/repo12345")

    metadata = mock_fetch_metadata("valid/repo")
    assert metadata.owner == "valid"
    assert metadata.name == "repo"
    assert metadata.star_count == 100


def test_mock_fetch_commits():
    commits = mock_fetch_commits("valid/repo")
    assert len(commits) == 100
    assert commits[0].commit_hash.startswith("hash")
    assert commits[0].author in ["alice", "bob", "charlie", "dave"]
