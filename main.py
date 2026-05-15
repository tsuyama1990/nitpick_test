import logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point for the dashboard CLI.

    The function orchestrates the loading of settings, the GitHub client,
    and the Streamlit UI. It does not return a value; `None` is the
    intentional return type.
    """
    from src.config import get_settings

    logger.info("Initializing GitHub Analytics Dashboard...")
    settings = get_settings()
    logger.info(
        f"Loaded configuration. Cache Dir: {settings.CACHE_DIR}, Cache TTL: {settings.CACHE_TTL}"
    )
    logger.info("Ready for GitHub Client and Streamlit UI in future cycles.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
