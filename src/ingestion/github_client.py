import logging
from typing import Any

import httpx

from src.config import get_settings
from src.domain_models.exceptions import GitHubAPIError, RateLimitError, RepositoryNotFoundError
from src.domain_models.github import CommitRecord, RepoMetadata

logger = logging.getLogger(__name__)

# Exclude sensitive headers from logging
logging.getLogger("httpx").setLevel(logging.WARNING)


def _get_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    settings = get_settings()
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"
    return headers


def _handle_response_errors(response: httpx.Response) -> None:
    if response.status_code == 404:
        msg = "Repository not found."
        raise RepositoryNotFoundError(msg)
    if response.status_code in {403, 429}:
        msg = "GitHub API rate limit exceeded."
        raise RateLimitError(msg)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        msg = f"GitHub API Error: {e}"
        raise GitHubAPIError(msg) from e


def fetch_repo_metadata(repo_name: str) -> RepoMetadata:
    """Fetches repository metadata from GitHub."""
    url = f"https://api.github.com/repos/{repo_name}"
    try:
        response = httpx.get(url, headers=_get_headers(), timeout=10.0)
    except httpx.RequestError as e:
        msg = f"Network error: {e}"
        raise GitHubAPIError(msg) from e

    _handle_response_errors(response)
    data = response.json()

    return RepoMetadata(
        stargazers_count=data.get("stargazers_count", 0),
        forks_count=data.get("forks_count", 0),
        open_issues_count=data.get("open_issues_count", 0),
    )


def fetch_commits(repo_name: str, limit: int = 100) -> list[CommitRecord]:
    """Fetches the latest commits from GitHub."""
    url = f"https://api.github.com/repos/{repo_name}/commits"
    params: dict[str, Any] = {"per_page": limit}
    try:
        response = httpx.get(url, headers=_get_headers(), params=params, timeout=10.0)
    except httpx.RequestError as e:
        msg = f"Network error: {e}"
        raise GitHubAPIError(msg) from e

    _handle_response_errors(response)
    data = response.json()

    commits = []
    for item in data:
        commit_data = item.get("commit", {})
        author_data = commit_data.get("author", {})

        # fallback to empty string if missing
        author_name = author_data.get("name") or "Unknown"
        message = commit_data.get("message") or ""
        date_str = author_data.get("date")

        if date_str:
            commits.append(
                CommitRecord(
                    date=date_str,
                    author_name=author_name,
                    message=message,
                )
            )

    return commits
