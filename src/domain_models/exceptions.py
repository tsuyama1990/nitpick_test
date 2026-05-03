class GitHubClientError(Exception):
    """Base exception for GitHub client errors."""


class AuthenticationError(GitHubClientError):
    """Raised when authentication with the GitHub API fails (e.g., invalid token)."""


class RateLimitError(GitHubClientError):
    """Raised when the GitHub API rate limit is exceeded."""


class RepositoryNotFoundError(GitHubClientError):
    """Raised when the requested repository is not found."""
