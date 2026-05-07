import logging
import os

from src.ingestion import GitHubClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def test_uat() -> None:
    client = GitHubClient()
    repo_info = client.fetch_repository_info("streamlit", "streamlit")
    commits = client.fetch_recent_commits("streamlit", "streamlit", limit=5)
    logger.info("Stars: %s", repo_info.stargazers_count)
    for commit in commits:
        logger.info("Commit Author: %s", commit.author_name)


if __name__ == "__main__":
    if os.environ.get("GITHUB_TOKEN"):
        test_uat()
    else:
        logger.info("Skip UAT, GITHUB_TOKEN not provided")
