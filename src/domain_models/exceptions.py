class APIError(Exception):
    """Base class for all API-related errors."""


class NotFoundError(APIError):
    """Raised when a generic 404 is encountered."""


class RepositoryNotFoundError(NotFoundError):
    """Raised when a specific repository is not found (404)."""


class RateLimitExceededError(APIError):
    """Raised when the API rate limit is exceeded (403 or 429)."""
