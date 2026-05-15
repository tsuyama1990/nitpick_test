import os
import unittest.mock
from datetime import UTC, datetime

from src.config import get_settings
from src.domain_models.schemas import CommitItem, RepositoryMetrics


def test_e2e_full_domain_pipeline() -> None:
    """End to end test simulating domain layer pipeline configuration & parsing."""
    get_settings.cache_clear()
    with unittest.mock.patch.dict(os.environ, {"GITHUB_TOKEN": "e2e_mock_token"}):
        settings = get_settings()
        assert settings.GITHUB_TOKEN == "e2e_mock_token"  # noqa: S105
        assert settings.CACHE_TTL == 3600
        assert settings.CACHE_DIR == "./.cache"

    from typing import Any

    metrics_payload: dict[str, Any] = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "extra_api_noise": "should be stripped",
    }

    metrics = RepositoryMetrics(**metrics_payload)
    assert metrics.stargazers_count == 100
    assert not hasattr(metrics, "extra_api_noise")

    commit_payload: dict[str, Any] = {
        "commit": {
            "author": {"name": "E2E Tester", "date": "2024-01-01T12:00:00Z", "extra": "strip me"}
        },
        "node_id": "sha_123",
    }

    commit_item = CommitItem(**commit_payload)
    assert commit_item.commit.author.name == "E2E Tester"
    assert commit_item.commit.author.date == datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
    assert not hasattr(commit_item, "node_id")
