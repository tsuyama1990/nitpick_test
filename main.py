import logging

from src.domain_models import get_settings
from src.services import GitHubAnalyticsService

logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    service = GitHubAnalyticsService(settings)
    logger.info("GitHub Analytics Service initialized for repo: %s", service.repo_name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
