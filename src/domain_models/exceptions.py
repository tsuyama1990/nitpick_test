class GitHubAPIError(Exception):
    """Base exception for all GitHub API related errors."""


class AuthenticationError(GitHubAPIError):
    """Raised when authentication with the GitHub API fails (e.g., 401, 403)."""


class RateLimitError(GitHubAPIError):
    """Raised when the GitHub API rate limit is exceeded (e.g., 429)."""


class RepositoryNotFoundError(GitHubAPIError):
    """Raised when the requested repository does not exist or is inaccessible (e.g., 404)."""
