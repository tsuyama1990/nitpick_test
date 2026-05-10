class RepositoryNotFoundError(Exception):
    """Raised when a requested GitHub repository is not found."""


class RateLimitExceededError(Exception):
    """Raised when GitHub API rate limits are exceeded."""
