class GitHubAPIError(Exception):
    """Base class for all custom GitHub API exceptions."""


class AuthenticationError(GitHubAPIError):
    """Raised when authentication with the GitHub API fails (e.g., 401 or 403 due to bad token)."""


class RateLimitError(GitHubAPIError):
    """Raised when the GitHub API rate limit is exceeded (429)."""


class RepositoryNotFoundError(GitHubAPIError):
    """Raised when the requested repository does not exist or is not accessible (404)."""
