class GitHubAPIError(Exception):
    """Base class for all exceptions related to the GitHub API."""


class AuthenticationError(GitHubAPIError):
    """Raised when authentication fails (HTTP 401 or 403 due to auth)."""


class RateLimitError(GitHubAPIError):
    """Raised when the rate limit is exceeded (HTTP 429)."""


class RepositoryNotFoundError(GitHubAPIError):
    """Raised when the target repository does not exist (HTTP 404)."""
