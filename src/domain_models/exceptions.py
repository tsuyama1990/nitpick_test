class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""


class AuthenticationError(GitHubAPIError):
    """Raised when authentication fails (401, 403 due to invalid token)."""


class RateLimitError(GitHubAPIError):
    """Raised when the GitHub API rate limit is exceeded (429 or 403 due to rate limit)."""


class RepositoryNotFoundError(GitHubAPIError):
    """Raised when the requested repository is not found (404)."""
