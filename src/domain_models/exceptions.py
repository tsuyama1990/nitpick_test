class GithubAPIError(Exception):
    """Base class for all GitHub API related errors."""

class AuthenticationError(GithubAPIError):
    """Raised when authentication fails (401/403)."""

class RateLimitError(GithubAPIError):
    """Raised when GitHub API rate limits are hit (429)."""

class RepositoryNotFoundError(GithubAPIError):
    """Raised when the requested repository is not found (404)."""
