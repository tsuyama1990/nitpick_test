import marimo

__generated_with = "0.4.0"
app = marimo.App()


@app.cell
def __():
    import sys
    from pathlib import Path

    # Add project root to sys.path
    project_root = str(Path(__file__).parent.parent.parent.resolve())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    return (project_root,)


@app.cell
def __(project_root):
    import os

    from pydantic import ValidationError

    from src.domain_models.config import Settings, get_settings
    from src.domain_models.schemas import CommitItem, RepositoryMetrics

    print("Executing UAT-C01-01: Environment Configuration Enforcement")

    # Store original and clear
    original_token = os.environ.get("GITHUB_TOKEN")
    if "GITHUB_TOKEN" in os.environ:
        del os.environ["GITHUB_TOKEN"]
    get_settings.cache_clear()

    try:
        Settings()
        msg = "Should have raised ValidationError"
        raise AssertionError(msg)
    except ValidationError as e:
        assert "GITHUB_TOKEN" in str(e)
        print("✓ UAT-C01-01 Passed: Configuration correctly enforced GITHUB_TOKEN presence.")

    # Restore original if present for future cells
    if original_token is not None:
        os.environ["GITHUB_TOKEN"] = original_token
    else:
        # Give it a dummy token for the rest of the tests to pass safely
        os.environ["GITHUB_TOKEN"] = "dummy_token"

    print("\nExecuting UAT-C01-02: Domain Model Validation")
    mock_payload = {
        "sha": "123",
        "commit": {
            "author": {
                "name": "Test Author",
                "date": "2023-12-01T12:00:00Z",
                "email": "test@example.com",
            },
            "message": "test message",
        },
    }

    commit_item = CommitItem(**mock_payload)
    assert commit_item.commit.author.name == "Test Author"
    from datetime import UTC, datetime

    assert commit_item.commit.author.date == datetime(2023, 12, 1, 12, 0, tzinfo=UTC)

    try:
        CommitItem(commit={"author": {"date": "invalid"}})
        msg = "Should have raised ValidationError"
        raise AssertionError(msg)
    except ValidationError:
        pass

    print("✓ UAT-C01-02 Passed: Domain Model correctly validated data and parsed dates.")

    print("\nExecuting UAT-C01-03: Ingestion Client Integration")
    from unittest.mock import patch

    import httpx

    from src.ingestion.github_client import GitHubClient

    mock_req_metrics = httpx.Request("GET", "https://api.github.com/repos/owner/repo")
    mock_response_metrics = httpx.Response(
        200,
        json={"stargazers_count": 100, "forks_count": 50, "open_issues_count": 5},
        request=mock_req_metrics,
    )

    mock_req_commits = httpx.Request("GET", "https://api.github.com/repos/owner/repo/commits")
    mock_response_commits = httpx.Response(
        200,
        json=[{"commit": {"author": {"name": "Jane Doe", "date": "2023-12-01T12:00:00Z"}}}],
        request=mock_req_commits,
    )

    def side_effect(url, *args, **kwargs):
        if "commits" in str(url):
            return mock_response_commits
        return mock_response_metrics

    with patch("httpx.Client.get", side_effect=side_effect):
        client = GitHubClient()
        metrics_data = client.get_repository_metrics("owner", "repo")
        commits_data = client.get_recent_commits("owner", "repo", limit=1)

        metrics = RepositoryMetrics(**metrics_data)
        assert metrics.stargazers_count == 100

        commit = CommitItem(**commits_data[0])
        assert commit.commit.author.name == "Jane Doe"
        print(
            "✓ UAT-C01-03 Passed: Ingestion client successfully mocked and integrated with schemas."
        )

    return (
        CommitItem,
        RepositoryMetrics,
        Settings,
        ValidationError,
        get_settings,
        mock_payload,
        original_token,
        GitHubClient,
    )


if __name__ == "__main__":
    app.run()
