import logging

import httpx
import polars as pl
import streamlit as st

from src.ingestion.github_client import fetch_recent_commits, fetch_repo_info
from src.transformation.processor import process_commits_per_committer, process_commits_per_day
from src.transformation.storage import load_from_cache, save_to_cache

logger = logging.getLogger(__name__)

st.set_page_config(page_title="GitHub Analytics Dashboard", layout="wide")

st.title("GitHub Repository Analytics PoC")

repo_input = st.text_input("Enter Owner/Repo", placeholder="e.g., streamlit/streamlit")


def _get_cached_data(
    owner: str, repo: str
) -> tuple[dict[str, int], pl.DataFrame, pl.DataFrame] | None:
    cache_key_prefix = f"{owner}_{repo}"

    # Check cache for processed data
    commits_by_day = load_from_cache(f"{cache_key_prefix}_commits_by_day")
    commits_by_author = load_from_cache(f"{cache_key_prefix}_commits_by_author")

    # We also need repo stats. For simplicity in PoC, if we have cache, we just fetch stats fresh
    # (since it's 1 call) or we could cache it too. Let's fetch fresh stats but use cached commits.
    if commits_by_day is not None and commits_by_author is not None:
        try:
            repo_info = fetch_repo_info(owner, repo)
            stats = {
                "Stars": repo_info.stars,
                "Forks": repo_info.forks,
                "Open Issues": repo_info.open_issues,
            }
        except Exception:
            logger.exception("Failed to fetch fresh stats while using cached commits")
            return None
        else:
            return stats, commits_by_day, commits_by_author
    return None


if repo_input:
    if "/" not in repo_input or len(repo_input.split("/")) != 2:
        st.warning("Please enter in `owner/repo` format.")
    else:
        owner, repo = repo_input.split("/")
        owner = owner.strip()
        repo = repo.strip()

        with st.spinner(f"Fetching data for {owner}/{repo}..."):
            try:
                cached = _get_cached_data(owner, repo)
                if cached:
                    st.success("Loaded data from local cache.")
                    stats, commits_by_day, commits_by_author = cached
                else:
                    repo_info = fetch_repo_info(owner, repo)
                    stats = {
                        "Stars": repo_info.stars,
                        "Forks": repo_info.forks,
                        "Open Issues": repo_info.open_issues,
                    }

                    commits = fetch_recent_commits(owner, repo)

                    commits_by_day = process_commits_per_day(commits)
                    commits_by_author = process_commits_per_committer(commits)

                    # Save to cache
                    cache_key_prefix = f"{owner}_{repo}"
                    save_to_cache(commits_by_day, f"{cache_key_prefix}_commits_by_day")
                    save_to_cache(commits_by_author, f"{cache_key_prefix}_commits_by_author")

                # Metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Stars", stats["Stars"])
                col2.metric("Forks", stats["Forks"])
                col3.metric("Open Issues", stats["Open Issues"])

                st.subheader("Commits per Day")
                if not commits_by_day.is_empty():
                    # Streamlit expects pandas dataframe or dict for charts generally, Polars often works but let's be safe
                    # st.line_chart uses the index for X.
                    pdf = commits_by_day.to_pandas()
                    pdf = pdf.set_index("date")
                    st.line_chart(pdf)
                else:
                    st.info("No commit data found.")

                st.subheader("Top 5 Committers")
                if not commits_by_author.is_empty():
                    pdf_authors = commits_by_author.to_pandas()
                    pdf_authors = pdf_authors.set_index("author_name")
                    st.bar_chart(pdf_authors)
                else:
                    st.info("No commit data found.")

            except PermissionError:
                # E.g., 403 / 429
                st.error(
                    "認証エラーまたはレートリミットが発生しました。トークンが有効か確認してください。"
                )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    st.error(
                        "リポジトリが見つかりません。オーナー名とリポジトリ名を確認してください。"
                    )
                else:
                    st.error(f"API Error: {e.response.status_code}")
            except Exception:
                logger.exception("Unexpected error")
                st.error("予期せぬエラーが発生しました。")
