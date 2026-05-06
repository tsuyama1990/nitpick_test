from datetime import UTC, datetime

import pytest

from src.config.settings import AppConfig
from src.domain_models.commit import CommitData
from src.domain_models.repository import RepositoryInfo


def test_repository_info_ignores_extra() -> None:
    data: dict[str, object] = {
        "name": "test-repo",
        "owner": "test-owner",
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "extra_field": "should be ignored",
        "another_extra": 123,
    }
    repo = RepositoryInfo(**data)  # type: ignore[arg-type]
    assert repo.name == "test-repo"
    assert repo.stargazers_count == 100
    assert not hasattr(repo, "extra_field")


def test_commit_data_flattening() -> None:
    payload: dict[str, object] = {
        "sha": "abcdef123456",
        "commit": {
            "author": {"name": "John Doe", "date": "2023-10-01T12:00:00Z"},
            "message": "Initial commit",
        },
        "url": "https://api.github.com/repos/test/commit/abcdef",
    }
    commit = CommitData(**payload)  # type: ignore[arg-type]
    assert commit.sha == "abcdef123456"
    assert commit.author_name == "John Doe"
    assert commit.date == datetime(2023, 10, 1, 12, 0, 0, tzinfo=UTC)


def test_app_config_forbids_extra() -> None:
    with pytest.raises(ValueError, match="extra_forbidden"):
        AppConfig(GITHUB_TOKEN="dummy_token", UNKNOWN_VAR="test")  # noqa: S106
