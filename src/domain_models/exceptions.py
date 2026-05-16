class RepositoryNotFoundError(Exception):
    """Raised when a GitHub repository is not found (404)."""


class RateLimitExceededError(Exception):
    """Raised when the GitHub API rate limit is exceeded (403 or 429)."""
