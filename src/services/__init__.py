"""Service orchestrators."""

from src.domain_models import Settings


class GitHubAnalyticsService:
    """Core analytics service orchestration."""

    def __init__(self, settings: Settings) -> None:
        """Initialize with app settings."""
        self.settings = settings
        self.repo_name = "default/repo"
