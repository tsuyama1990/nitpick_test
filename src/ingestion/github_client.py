"""GitHub API HTTP Client."""

import logging
from typing import Any

import httpx

from src.domain_models.config import get_settings

logger = logging.getLogger(__name__)
# Prevent httpx from logging sensitive headers (if not already disabled globally)
logging.getLogger("httpx").setLevel(logging.WARNING)


def _get_headers() -> dict[str, str]:
    """Get HTTP headers for GitHub API requests."""
    settings = get_settings()
    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {settings.GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _handle_response(response: httpx.Response) -> Any:
    """Handle HTTP response and raise appropriate errors before parsing JSON."""
    if response.status_code == 403:
        msg = (
            f"GitHub API Error: 403 Forbidden. Rate limit or permissions? Response: {response.text}"
        )
        raise PermissionError(msg)
    if response.status_code == 429:
        msg = f"GitHub API Error: 429 Too Many Requests. Response: {response.text}"
        raise ConnectionError(msg)
    if response.status_code == 404:
        msg = f"GitHub API Error: 404 Not Found. Invalid repository? Response: {response.text}"
        raise ValueError(msg)
    response.raise_for_status()
    return response.json()


def get_repo_info(owner: str, repo: str) -> dict[str, Any]:
    """Fetch repository basic info."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    with httpx.Client() as client:
        response = client.get(url, headers=_get_headers())
        res: dict[str, Any] = _handle_response(response)
        return res


def get_repo_commits(owner: str, repo: str, per_page: int = 100) -> list[dict[str, Any]]:
    """Fetch recent commits for a repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    with httpx.Client() as client:
        response = client.get(url, headers=_get_headers(), params={"per_page": per_page})
        res: list[dict[str, Any]] = _handle_response(response)
        return res
