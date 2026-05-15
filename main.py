import logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point for the dashboard CLI.

    The function orchestrates the loading of settings, the GitHub client,
    and the Streamlit UI. It does not return a value; `None` is the
    intentional return type.
    """
    logger.info("Hello from app!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
