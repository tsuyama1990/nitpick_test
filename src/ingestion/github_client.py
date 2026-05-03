import httpx

from src.domain.exceptions import (
    AuthenticationError,
    GitHubAPIError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.domain.models import CommitRecord, RepositoryMetadata


class GitHubClient:
    """Client to interact with the GitHub REST API securely."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, timeout: float = 10.0) -> None:
        self._token = token
        self._timeout = timeout
        self._headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self._token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _handle_response_error(self, response: httpx.Response) -> None:
        """Translates HTTP error status codes to custom domain exceptions."""
        if response.status_code == 200:
            return
        if response.status_code in {401, 403}:
            msg = "Authentication failed. Invalid or missing token."
            raise AuthenticationError(msg)
        if response.status_code == 404:
            msg = "Repository not found."
            raise RepositoryNotFoundError(msg)
        if response.status_code == 429:
            msg = "GitHub API rate limit exceeded."
            raise RateLimitError(msg)
        msg = f"GitHub API Error: {response.status_code}"
        raise GitHubAPIError(msg)

    def fetch_repository_metadata(self, repo: str) -> RepositoryMetadata:
        """Fetches repository metadata from the GitHub API."""
        url = f"{self.BASE_URL}/repos/{repo}"

        with httpx.Client(timeout=self._timeout) as client:
            try:
                response = client.get(url, headers=self._headers)
                self._handle_response_error(response)

                data = response.json()
                # Parse untyped dict to our Pydantic model
                return RepositoryMetadata(
                    name=data.get("name", ""),
                    owner=data.get("owner", {}).get("login", ""),
                    stargazers_count=data.get("stargazers_count", 0),
                    forks_count=data.get("forks_count", 0),
                    open_issues_count=data.get("open_issues_count", 0),
                )
            except httpx.RequestError as e:
                msg = f"Network error while connecting to GitHub API: {e}"
                raise GitHubAPIError(msg) from e

    def fetch_commits(self, repo: str, limit: int = 100) -> list[CommitRecord]:
        """Fetches the commit history from the GitHub API."""
        url = f"{self.BASE_URL}/repos/{repo}/commits"
        params = {"per_page": limit}

        with httpx.Client(timeout=self._timeout) as client:
            try:
                response = client.get(url, headers=self._headers, params=params)
                self._handle_response_error(response)

                data = response.json()
                commits = []
                for item in data:
                    commits.append(
                        CommitRecord(
                            sha=item.get("sha", ""),
                            author_name=item.get("commit", {}).get("author", {}).get("name", ""),
                            date=item.get("commit", {}).get("author", {}).get("date", ""),
                        )
                    )
                return commits
            except httpx.RequestError as e:
                msg = f"Network error while connecting to GitHub API: {e}"
                raise GitHubAPIError(msg) from e
