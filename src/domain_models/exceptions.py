class RepositoryNotFoundError(Exception):
    """Exception raised when a repository is not found (404)."""


class RateLimitExceededError(Exception):
    """Exception raised when API rate limit is exceeded (403 or 429)."""
