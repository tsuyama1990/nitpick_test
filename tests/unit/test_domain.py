import os
from datetime import UTC, datetime
from unittest import mock

import pytest
from pydantic import ValidationError

from src.domain_models import (
    CommitAuthor,
    CommitData,
    CommitItem,
    GitHubAnalyticsError,
    RateLimitExceededError,
    RepositoryMetrics,
    RepositoryNotFoundError,
    Settings,
    get_settings,
)
from src.domain_models.manifest import Manifest


@pytest.fixture(autouse=True)
def clear_lru_cache() -> None:
    """Clear LRU cache before each test to ensure fresh settings loading."""
    get_settings.cache_clear()


class TestSettings:
    def test_settings_successful_initialization(self) -> None:
        """Test Settings init with valid GITHUB_TOKEN."""
        with mock.patch.dict(
            os.environ, {"GITHUB_TOKEN": "ghp_fake_token", "ENV_FILE": ".env.fake"}, clear=True
        ):
            settings = Settings()  # type: ignore[call-arg]
            assert settings.GITHUB_TOKEN == "ghp_fake_token"  # noqa: S105

    def test_settings_missing_token_raises_error(self) -> None:
        """Test Settings init fails if GITHUB_TOKEN is missing."""
        with (
            mock.patch.dict(os.environ, {"ENV_FILE": ".env.fake"}, clear=True),
            pytest.raises(ValidationError),
        ):
            Settings()  # type: ignore[call-arg]

    def test_get_settings_caching(self) -> None:
        """Test that get_settings caches the Settings instance."""
        with mock.patch.dict(
            os.environ, {"GITHUB_TOKEN": "ghp_fake_token", "ENV_FILE": ".env.fake"}, clear=True
        ):
            settings_1 = get_settings()
            settings_2 = get_settings()
            assert settings_1 is settings_2


class TestRepositoryMetrics:
    def test_successful_parsing(self) -> None:
        data = {
            "stargazers_count": 100,
            "forks_count": 50,
            "open_issues_count": 10,
            "extra_field": "ignored",
        }
        model = RepositoryMetrics(**data)  # type: ignore[arg-type]
        assert model.stargazers_count == 100
        assert model.forks_count == 50
        assert model.open_issues_count == 10
        assert not hasattr(model, "extra_field")

    def test_missing_field(self) -> None:
        data = {"stargazers_count": 100, "forks_count": 50}
        with pytest.raises(ValidationError):
            RepositoryMetrics(**data)

    def test_invalid_type_raises_typeerror(self) -> None:
        with pytest.raises(TypeError):
            RepositoryMetrics._strip_extra.__get__(None, RepositoryMetrics)("not a dict")  # type: ignore[operator]


class TestCommitItemAndNestedModels:
    def test_successful_parsing(self) -> None:
        data = {
            "commit": {
                "author": {
                    "name": "Octocat",
                    "date": "2023-10-27T10:00:00Z",
                    "email": "octocat@github.com",
                },
                "message": "Initial commit",
            },
            "sha": "1234567890",
        }
        model = CommitItem(**data)  # type: ignore[arg-type]
        assert isinstance(model.commit, CommitData)
        assert isinstance(model.commit.author, CommitAuthor)
        assert model.commit.author.name == "Octocat"
        assert model.commit.author.date == datetime(2023, 10, 27, 10, 0, tzinfo=UTC)

        # Verify stripping extra fields
        assert not hasattr(model, "sha")
        assert not hasattr(model.commit, "message")
        assert not hasattr(model.commit.author, "email")

    def test_missing_author_name(self) -> None:
        data = {"commit": {"author": {"date": "2023-10-27T10:00:00Z"}}}
        with pytest.raises(ValidationError):
            CommitItem(**data)  # type: ignore[arg-type]

    def test_invalid_date_format(self) -> None:
        data = {"commit": {"author": {"name": "Octocat", "date": "not-a-date"}}}
        with pytest.raises(ValidationError):
            CommitItem(**data)  # type: ignore[arg-type]

    def test_strip_extra_type_error(self) -> None:
        with pytest.raises(TypeError):
            CommitItem._strip_extra.__get__(None, CommitItem)("not a dict")  # type: ignore[operator]

        with pytest.raises(TypeError):
            CommitData._strip_extra.__get__(None, CommitData)("not a dict")  # type: ignore[operator]

        with pytest.raises(TypeError):
            CommitAuthor._strip_extra.__get__(None, CommitAuthor)("not a dict")  # type: ignore[operator]


class TestExceptions:
    def test_exceptions(self) -> None:
        assert issubclass(GitHubAnalyticsError, Exception)
        assert issubclass(RepositoryNotFoundError, GitHubAnalyticsError)
        assert issubclass(RateLimitExceededError, GitHubAnalyticsError)


class TestManifest:
    def test_manifest(self) -> None:
        model = Manifest(version="1.0.0")
        assert model.version == "1.0.0"

        with pytest.raises(ValidationError):
            Manifest(version="1.0", extra="forbid")  # type: ignore[call-arg]
