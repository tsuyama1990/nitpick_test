class GitHubAPIError(Exception):
    """Base class for all custom GitHub API exceptions."""


class AuthenticationError(GitHubAPIError):
    """Raised when authentication with the GitHub API fails (e.g., 401 or 403 status due to missing/invalid token)."""


class RateLimitError(GitHubAPIError):
    """Raised when the GitHub API rate limit is exceeded (429 status)."""


class RepositoryNotFoundError(GitHubAPIError):
    """Raised when a requested repository is not found (404 status)."""
