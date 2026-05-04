class GitHubAPIError(Exception):
    """Base exception for all GitHub API related errors."""


class AuthenticationError(GitHubAPIError):
    """Raised when authentication with the GitHub API fails (e.g., invalid token)."""


class RateLimitError(GitHubAPIError):
    """Raised when the GitHub API rate limit is exceeded."""


class RepositoryNotFoundError(GitHubAPIError):
    """Raised when the requested repository cannot be found on GitHub."""
