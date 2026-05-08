import logging
from typing import Any

import httpx

from src.domain_models.config import get_settings
from src.domain_models.github import CommitDetail, RepositoryInfo

logger = logging.getLogger(__name__)
# Securely configure the logger to avoid logging Authorization headers
logging.getLogger("httpx").setLevel(logging.WARNING)


def _get_client() -> httpx.Client:
    settings = get_settings()
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {settings.GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    return httpx.Client(base_url="https://api.github.com", headers=headers, timeout=10.0)


def _handle_response(response: httpx.Response) -> Any:
    if response.status_code == 403:
        # Could be forbidden or rate limited. GitHub rate limits return 403 or 429
        msg = f"GitHub API Error 403: Forbidden or Rate Limited. {response.text}"
        raise PermissionError(msg)
    if response.status_code == 429:
        msg = f"GitHub API Error 429: Too Many Requests. {response.text}"
        raise PermissionError(msg)

    response.raise_for_status()
    return response.json()


def fetch_repo_info(owner: str, repo: str) -> RepositoryInfo:
    """Fetch basic repository information from GitHub API."""
    with _get_client() as client:
        response = client.get(f"/repos/{owner}/{repo}")
        data = _handle_response(response)

        if not isinstance(data, dict):
            msg = "Expected dict from GitHub API"
            raise TypeError(msg)

        return RepositoryInfo(**data)


def fetch_recent_commits(owner: str, repo: str) -> list[CommitDetail]:
    """Fetch up to 100 recent commits for a repository."""
    with _get_client() as client:
        response = client.get(f"/repos/{owner}/{repo}/commits", params={"per_page": 100})
        data = _handle_response(response)

        if not isinstance(data, list):
            msg = "Expected list from GitHub API"
            raise TypeError(msg)

        return [CommitDetail(**commit) for commit in data]
