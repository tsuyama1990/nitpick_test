import logging

import streamlit as st

from src.ingestion.api_client import GitHubAPIClient
from src.transformation.processor import DataProcessor

logger = logging.getLogger(__name__)


def main() -> None:
    st.set_page_config(page_title="GitHub Analytics Dashboard", layout="wide")
    st.title("GitHub Analytics Dashboard")

    with st.sidebar:
        st.header("Repository Configuration")
        repo_input = st.text_input(
            "Enter Owner/Repo (e.g., streamlit/streamlit)", value="streamlit/streamlit"
        )
        fetch_button = st.button("Fetch Data")

    if fetch_button and repo_input:
        if "/" not in repo_input or len(repo_input.split("/")) != 2:
            st.warning("Please enter the repository in 'owner/repo' format.")
            return

        owner, repo = repo_input.split("/")

        try:
            client = GitHubAPIClient()
            processor = DataProcessor()

            with st.spinner("Fetching data from GitHub API..."):
                # Fetch Repo Info
                repo_info = client.get_repo_info(owner, repo)

                # Render KPIs
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Stars", repo_info.stargazers_count)
                with col2:
                    st.metric("Forks", repo_info.forks_count)
                with col3:
                    st.metric("Open Issues", repo_info.open_issues_count)

                # Fetch and Process Commits via Cache
                from pathlib import Path

                cache_dir = Path(processor.settings.CACHE_DIR)
                daily_cache = cache_dir / f"{owner}_{repo}_daily_commits.parquet"
                top_cache = cache_dir / f"{owner}_{repo}_top_committers.parquet"

                if processor._is_cache_valid(daily_cache) and processor._is_cache_valid(top_cache):
                    daily_df = processor.process_daily_commits(owner, repo)
                    top_df = processor.process_top_committers(owner, repo)
                else:
                    commits = client.get_recent_commits(owner, repo, limit=100)
                    daily_df = processor.process_daily_commits(owner, repo, commits)
                    top_df = processor.process_top_committers(owner, repo, commits)

                st.subheader("Daily Commits")
                if not daily_df.is_empty():
                    # Streamlit natively handles Polars dataframes
                    st.line_chart(daily_df, x="date", y="commit_count")
                else:
                    st.info("No commit data available.")

                st.subheader("Top 5 Committers")
                if not top_df.is_empty():
                    st.bar_chart(top_df, x="committer_name", y="commit_count")
                else:
                    st.info("No committer data available.")

        except Exception as e:
            logger.exception("Error fetching data")
            st.error(str(e))


if __name__ == "__main__":
    main()
