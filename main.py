import logging
import subprocess
from pathlib import Path

from src.domain_models.config import get_settings

logger = logging.getLogger(__name__)


class GitHubAnalyticsService:
    """Orchestrator placeholder required for Cycle 03."""

    def __init__(self, token: str) -> None:
        self.token = token


def main() -> None:
    # Load configuration
    try:
        settings = get_settings()
        logger.info("Configuration loaded successfully.")
    except Exception:
        logger.exception("Configuration failed")
        return

    # Create orchestrator service
    service = GitHubAnalyticsService(token=settings.github_token)  # noqa: F841
    logger.info("GitHubAnalyticsService orchestrator instantiated.")

    # Streamlit requires a file path to run. We use subprocess to invoke it
    # rather than running standard python code since Streamlit acts as its own server.
    app_path = Path(__file__).parent / "src" / "app.py"
    if not app_path.exists():
        logger.error(f"Streamlit app file not found at {app_path}")
        return

    logger.info(f"Starting Streamlit app at {app_path}")
    # Run Streamlit non-blocking so the main function can return as instructed
    subprocess.Popen(["uv", "run", "streamlit", "run", str(app_path)])  # noqa: S603, S607
    return


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
