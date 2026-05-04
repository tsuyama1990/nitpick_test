import httpx

from src.config import AppConfig
from src.domain_models import (
    AuthenticationError,
    CommitRecord,
    GitHubAPIError,
    RateLimitError,
    RepositoryMetadata,
    RepositoryNotFoundError,
)


class GithubClient:
    """Core robust HTTP client logic handling requests to the GitHub API."""

    BASE_URL = "https://api.github.com"
    TIMEOUT = 10.0  # Strict timeout

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.config.github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _handle_error(self, response: httpx.Response) -> None:
        """Translates raw HTTP errors into specific domain exceptions."""
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status in (401, 403):
                # Check if it's actually a rate limit
                remaining = e.response.headers.get("X-RateLimit-Remaining")
                if remaining == "0":
                    msg = "GitHub API rate limit exceeded."
                    raise RateLimitError(msg) from None
                # Otherwise, it's an authentication error
                msg = "Invalid or expired GitHub token."
                raise AuthenticationError(msg) from None
            if status == 404:
                msg = "Repository not found or not accessible."
                raise RepositoryNotFoundError(msg) from None
            msg = f"GitHub API returned an error: {status}"
            raise GitHubAPIError(msg) from None

    def fetch_repository_metadata(self, owner: str, repo: str) -> RepositoryMetadata:
        """Fetches core information for a specific repository."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"

        with httpx.Client(timeout=self.TIMEOUT, headers=self._headers) as client:
            try:
                response = client.get(url)
            except httpx.RequestError as e:
                msg = f"Network error while connecting to GitHub API: {e}"
                raise GitHubAPIError(msg) from e

        self._handle_error(response)
        data = response.json()

        # GitHub's API returns "owner" as a dict containing "login" among other things.
        # We need to extract this string so it fits our domain model, mapping it properly.
        owner_name = data.get("owner", {}).get("login", "")

        # Build strict model
        return RepositoryMetadata(
            owner=owner_name,
            name=data.get("name", ""),
            stargazers_count=data.get("stargazers_count", 0),
            forks_count=data.get("forks_count", 0),
            open_issues_count=data.get("open_issues_count", 0),
        )

    def fetch_latest_commits(self, owner: str, repo: str, limit: int = 100) -> list[CommitRecord]:
        """Fetches the latest commits from the specified repository."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits"
        params = {"per_page": limit}

        with httpx.Client(timeout=self.TIMEOUT, headers=self._headers) as client:
            try:
                response = client.get(url, params=params)
            except httpx.RequestError as e:
                msg = f"Network error while connecting to GitHub API: {e}"
                raise GitHubAPIError(msg) from e

        self._handle_error(response)
        commits_data = response.json()

        results = []
        for item in commits_data:
            commit_info = item.get("commit", {})
            author_info = commit_info.get("author", {})

            record = CommitRecord(
                sha=item.get("sha", ""),
                author_name=author_info.get("name", ""),
                date=author_info.get("date", ""),
            )
            results.append(record)

        return results
