class RepositoryNotFoundError(Exception):
    """Exception raised when a GitHub repository is not found (404)."""


class RateLimitExceededError(Exception):
    """Exception raised when GitHub API rate limit is exceeded (403/429)."""


class InvalidPayloadError(Exception):
    """Exception raised when the payload cannot be validated into a domain schema."""
