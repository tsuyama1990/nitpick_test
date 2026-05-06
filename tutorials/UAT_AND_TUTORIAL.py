import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def __():
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from datetime import datetime, timezone

    import pytest
    from pydantic import ValidationError

    import src.config.settings as settings_module
    from src.config.settings import AppConfig, get_settings
    from src.domain_models.commit import CommitData
    from src.domain_models.repository import RepositoryInfo

    return (
        AppConfig,
        CommitData,
        Path,
        RepositoryInfo,
        ValidationError,
        datetime,
        get_settings,
        pytest,
        settings_module,
        sys,
        timezone,
    )


@app.cell
def __(ValidationError, get_settings, settings_module):
    import os

    if "GITHUB_TOKEN" in os.environ:
        del os.environ["GITHUB_TOKEN"]
    settings_module._settings = None

    try:
        get_settings()
        _msg1 = "Should have raised ValidationError"
        raise AssertionError(_msg1)
    except ValidationError:
        print("UAT-C01-01 (Missing Token): Passed")
    return (os,)


@app.cell
def __(AppConfig, os, settings_module):
    os.environ["GITHUB_TOKEN"] = "test_token"
    settings_module._settings = None

    config = AppConfig()
    assert config.GITHUB_TOKEN == "test_token"

    try:
        AppConfig(GITHUB_TOKEN="test_token", INVALID="extra")  # type: ignore[call-arg]
        _msg2 = "Should have raised ValueError for extra_forbidden"
        raise AssertionError(_msg2)
    except ValueError as e:
        assert "extra_forbidden" in str(e)
        print("UAT-C01-01 (Valid Token & Extra Forbidden): Passed")
    return (config,)


@app.cell
def __(RepositoryInfo):
    massive_payload = {
        "name": "react",
        "owner": "facebook",
        "stargazers_count": 200000,
        "forks_count": 40000,
        "open_issues_count": 1000,
        "has_wiki": True,
        "has_issues": True,
        "license": {"key": "mit"},
        "irrelevant_data": [1, 2, 3],
    }
    repo = RepositoryInfo(**massive_payload)
    assert repo.stargazers_count == 200000
    assert not hasattr(repo, "has_wiki")
    print("UAT-C01-02 (RepositoryInfo Flattening): Passed")
    return massive_payload, repo


@app.cell
def __(CommitData, datetime, timezone):
    nested_payload = {
        "sha": "1234567890abcdef",
        "commit": {
            "author": {"name": "Jane Smith", "date": "2023-11-01T15:30:00Z"},
            "tree": {"sha": "abc"},
            "message": "Update README",
        },
        "parents": [],
    }
    commit = CommitData(**nested_payload)
    assert commit.sha == "1234567890abcdef"
    assert commit.author_name == "Jane Smith"
    assert commit.date == datetime(2023, 11, 1, 15, 30, 0, tzinfo=timezone.utc)
    print("UAT-C01-02 (CommitData Flattening): Passed")
    return commit, nested_payload


if __name__ == "__main__":
    app.run()
