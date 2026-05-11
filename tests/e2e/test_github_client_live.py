import pytest

from src.domain_models.config import get_settings
from src.ingestion.github_client import GitHubClient


@pytest.mark.skip(reason="Live API test")
def test_github_client_live() -> None:
    """
    Live API test for GitHubClient.
    To run this test, comment out the @pytest.mark.skip line and ensure
    a valid GITHUB_TOKEN is set in the .env file.
    """
    settings = get_settings()

    with GitHubClient(token=settings.github_token) as client:
        from src.processing.service import GitHubAnalyticsService

        service = GitHubAnalyticsService(client)

        # Fetch repository metrics for a known public repository
        metrics = service.get_metrics("streamlit", "streamlit")

        # Verify basic expected structure
        assert metrics.stargazers_count >= 0
        assert metrics.forks_count >= 0
        assert metrics.open_issues_count >= 0

        # Fetch recent commits
        commits = service.get_commits("streamlit", "streamlit", limit=5)

        # Verify basic expected structure
        assert isinstance(commits, list)
        assert len(commits) > 0
        assert commits[0].sha
