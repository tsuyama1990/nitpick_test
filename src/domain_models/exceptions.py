class DomainError(Exception):
    """Base class for all domain exceptions."""


class AuthenticationError(DomainError):
    """Raised when authentication fails (e.g., 401, 403 due to invalid token)."""


class RateLimitError(DomainError):
    """Raised when the API rate limit is exceeded (e.g., 429, or 403 due to rate limit)."""


class RepositoryNotFoundError(DomainError):
    """Raised when the requested repository is not found (e.g., 404)."""


class APIConnectionError(DomainError):
    """Raised when there is a connection issue with the API."""
