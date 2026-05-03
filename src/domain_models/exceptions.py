class GitHubAPIError(Exception):
    """Base class for all custom GitHub API exceptions."""


class AuthenticationError(GitHubAPIError):
    """Raised when authentication with the GitHub API fails (e.g., invalid token)."""


class RateLimitError(GitHubAPIError):
    """Raised when the GitHub API rate limit has been exceeded."""


class RepositoryNotFoundError(GitHubAPIError):
    """Raised when the requested repository is not found."""
