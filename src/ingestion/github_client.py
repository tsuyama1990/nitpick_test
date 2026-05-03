import httpx

from src.config import Settings
from src.domain_models.exceptions import (
    AuthenticationError,
    GitHubAPIError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.domain_models.models import CommitRecord, RepositoryMetadata


class GitHubClient:
    """Client for interacting with the GitHub REST API."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.settings.github_token}",
        }
        self.timeout = 10.0

    def _handle_response_errors(self, response: httpx.Response) -> None:
        """Translates HTTP errors into domain exceptions."""
        if response.status_code == 200:
            return

        if response.status_code in (401, 403):
            # Check for rate limit vs generic forbidden
            if "rate limit" in response.text.lower():
                msg = "GitHub API rate limit exceeded."
                raise RateLimitError(msg)
            msg = "Authentication failed with the GitHub API. Invalid token."
            raise AuthenticationError(msg)

        if response.status_code == 404:
            msg = "The requested repository was not found."
            raise RepositoryNotFoundError(msg)

        # Generic fallback
        response.raise_for_status()

    def get_repository_metadata(self, owner: str, repo_name: str) -> RepositoryMetadata:
        """Fetches core metadata for a repository."""
        url = f"{self.base_url}/repos/{owner}/{repo_name}"

        with httpx.Client(timeout=self.timeout) as client:
            try:
                response = client.get(url, headers=self.headers)
            except httpx.RequestError as e:
                msg = f"Network error during request: {e}"
                raise GitHubAPIError(msg) from e

        self._handle_response_errors(response)

        data = response.json()

        return RepositoryMetadata(
            owner=data["owner"]["login"],
            repo_name=data["name"],
            star_count=data["stargazers_count"],
            fork_count=data["forks_count"],
            open_issue_count=data["open_issues_count"],
        )

    def get_recent_commits(self, owner: str, repo_name: str) -> list[CommitRecord]:
        """Fetches the 100 most recent commits for a repository."""
        url = f"{self.base_url}/repos/{owner}/{repo_name}/commits?per_page=100"

        with httpx.Client(timeout=self.timeout) as client:
            try:
                response = client.get(url, headers=self.headers)
            except httpx.RequestError as e:
                msg = f"Network error during request: {e}"
                raise GitHubAPIError(msg) from e

        self._handle_response_errors(response)

        data = response.json()

        commits = []
        for item in data:
            commits.append(
                CommitRecord(
                    commit_hash=item["sha"],
                    author_name=item["commit"]["author"]["name"],
                    timestamp=item["commit"]["author"]["date"],
                )
            )

        return commits
