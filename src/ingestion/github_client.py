import httpx

from src.domain_models.exceptions import RateLimitExceededError, RepositoryNotFoundError
from src.domain_models.schemas import CommitHistory, RepositoryMetrics


class GitHubClient:
    """Client for interacting with the GitHub REST API."""

    def __init__(self, token: str) -> None:
        """Initialize the GitHub API client with a specific token."""
        self.client = httpx.Client(
            base_url="https://api.github.com",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {token}",
            },
            timeout=10.0,
        )

    def _handle_response(self, response: httpx.Response, owner: str, repo: str) -> None:
        """Process the httpx.Response and translate errors."""
        if response.status_code == 404:
            err_msg = f"Repository {owner}/{repo} not found."
            raise RepositoryNotFoundError(err_msg)
        if response.status_code in (403, 429):
            err_msg = "GitHub API rate limit exceeded."
            raise RateLimitExceededError(err_msg)
        response.raise_for_status()

    def get_repository_metrics(self, owner: str, repo: str) -> RepositoryMetrics:
        """Fetch core repository information metrics."""
        response = self.client.get(f"/repos/{owner}/{repo}")
        self._handle_response(response, owner, repo)
        data = response.json()
        return RepositoryMetrics(
            stargazers_count=data["stargazers_count"],
            forks_count=data["forks_count"],
            open_issues_count=data["open_issues_count"],
        )

    def get_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[CommitHistory]:
        """Fetch recent commit history for the repository."""
        response = self.client.get(f"/repos/{owner}/{repo}/commits", params={"per_page": limit})
        self._handle_response(response, owner, repo)

        commits = []
        for item in response.json():
            commits.append(
                CommitHistory(
                    sha=item["sha"],
                    date=item["commit"]["author"]["date"],
                    author=item["commit"]["author"]["name"],
                )
            )
        return commits

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self.client.close()
