import httpx

from src.domain_models import (
    APIConnectionError,
    AuthenticationError,
    CommitRecord,
    RateLimitError,
    RepositoryMetadata,
    RepositoryNotFoundError,
)


class GitHubClient:
    def __init__(self, token: str) -> None:
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.timeout = 10.0

    def _handle_request_error(self, exc: Exception) -> None:
        if isinstance(exc, httpx.HTTPStatusError):
            status = exc.response.status_code
            if status == 401:
                msg = "Invalid or missing GitHub token"
                raise AuthenticationError(msg) from exc
            if status == 403:
                msg = "Rate limit exceeded or access forbidden"
                raise RateLimitError(msg) from exc
            if status == 404:
                msg = "The specified repository was not found"
                raise RepositoryNotFoundError(msg) from exc
            if status == 429:
                msg = "Rate limit exceeded"
                raise RateLimitError(msg) from exc

        msg_c = f"Connection error: {exc!s}"
        raise APIConnectionError(msg_c) from exc

    def get_repository_metadata(self, owner: str, repo: str) -> RepositoryMetadata:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            with httpx.Client(headers=self.headers, timeout=self.timeout) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()

                return RepositoryMetadata(
                    owner=data["owner"]["login"],
                    repo=data["name"],
                    stars=data["stargazers_count"],
                    forks=data["forks_count"],
                    open_issues=data["open_issues_count"]
                )
        except Exception as e:
            self._handle_request_error(e)
            raise  # Fallback

    def get_recent_commits(self, owner: str, repo: str, limit: int = 100) -> list[CommitRecord]:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {"per_page": limit}
        try:
            with httpx.Client(headers=self.headers, timeout=self.timeout) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                commits = []
                for item in data:
                    commits.append(CommitRecord(
                        commit_hash=item["sha"],
                        author_name=item["commit"]["author"]["name"],
                        timestamp=item["commit"]["author"]["date"]
                    ))
                return commits
        except Exception as e:
            self._handle_request_error(e)
            raise  # Fallback
