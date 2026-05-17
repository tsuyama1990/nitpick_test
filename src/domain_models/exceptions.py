class APIError(Exception):
    """Base exception for API errors."""


class NotFoundError(APIError):
    """Exception raised when an API resource is not found (404)."""


class RepositoryNotFoundError(NotFoundError):
    """Exception raised when a specific GitHub repository is not found."""
