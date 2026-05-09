import pathlib
from collections.abc import Generator
from unittest.mock import patch

import pytest
from pytest_httpx import HTTPXMock
from streamlit.testing.v1 import AppTest

from src.domain_models.config import Settings


@pytest.fixture(autouse=True)
def mock_settings(tmp_path: pathlib.Path) -> Generator[Settings, None, None]:
    settings = Settings(GITHUB_TOKEN="test_token", CACHE_DIR=tmp_path)  # noqa: S106
    with (
        patch("src.clients.github_client.get_settings", return_value=settings),
        patch("src.services.data_processor.get_settings", return_value=settings),
        patch("src.domain_models.config.get_settings", return_value=settings),
    ):
        yield settings


def test_app_happy_path(httpx_mock: HTTPXMock) -> None:
    # Mock Repo info
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        json={"stargazers_count": 100, "forks_count": 50, "open_issues_count": 5},
    )
    # Mock Commits
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/commits?per_page=100",
        json=[
            {"sha": "123", "commit": {"author": {"name": "Alice", "date": "2023-01-01T10:00:00Z"}}}
        ],
    )

    at = AppTest.from_file("src/app.py")
    at.run()

    # Enter repo
    at.text_input[0].input("owner/repo").run()
    # Click analyze
    at.button[0].click().run(timeout=10)

    assert not at.exception
    # Check metrics
    assert len(at.metric) == 3
    assert at.metric[0].label == "Stars"
    assert at.metric[0].value == "100"


def test_app_invalid_input() -> None:
    at = AppTest.from_file("src/app.py")
    at.run()
    at.text_input[0].input("invalid").run()
    at.button[0].click().run()

    assert any("Please enter in 'owner/repo' format." in str(w.value) for w in at.warning)


def test_app_404_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/owner/repo", status_code=404)

    at = AppTest.from_file("src/app.py")
    at.run()
    at.text_input[0].input("owner/repo").run()
    at.button[0].click().run()

    assert any("Repository not found" in str(e.value) for e in at.error)


def test_app_403_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/owner/repo", status_code=403)

    at = AppTest.from_file("src/app.py")
    at.run()
    at.text_input[0].input("owner/repo").run()
    at.button[0].click().run()

    assert any("Authentication error" in str(e.value) for e in at.error)
