import re

import streamlit as st

from src.dashboard_service import DashboardService
from src.github_client import AuthError, NotFoundError, RateLimitError


def render_metrics(metrics: dict[str, int]) -> None:
    st.subheader("Repository Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Stars", metrics.get("stargazers_count", 0))
    col2.metric("Forks", metrics.get("forks_count", 0))
    col3.metric("Open Issues", metrics.get("open_issues_count", 0))


def render_charts(service: DashboardService, owner: str, repo: str) -> None:
    df_date, df_top = service.get_commit_data(owner, repo)
    st.subheader("Commit Activity (Last 100 Commits)")
    if not df_date.is_empty():
        st.line_chart(df_date.to_pandas().set_index("date"))
    else:
        st.info("No commit data found.")
    st.subheader("Top 5 Committers")
    if not df_top.is_empty():
        st.bar_chart(df_top.to_pandas().set_index("name"))
    else:
        st.info("No committer data found.")


def main() -> None:
    st.set_page_config(page_title="GitHub Analytics", layout="wide")
    st.title("GitHub Repository Analytics PoC")
    try:
        service = DashboardService()
    except Exception as e:
        st.error(f"Failed to initialize service: {e}")
        return
    repo_input = st.text_input(
        "Enter repository (owner/repo):", value="", placeholder="e.g., streamlit/streamlit"
    )
    if st.button("Analyze"):
        if not repo_input:
            st.warning("Please enter a repository name.")
            return
        if not re.match(r"^[^/]+/[^/]+$", repo_input):
            st.warning("Please enter the repository in the format 'owner/repo'.")
            return
        owner, repo = repo_input.split("/")
        with st.spinner(f"Fetching data for {repo_input}..."):
            try:
                metrics = service.get_repo_metrics(owner, repo)
                render_metrics(metrics)
                render_charts(service, owner, repo)
            except NotFoundError:
                st.error("Repository not found. Please check the owner and repository name.")
            except AuthError:
                st.error("Authentication failed. Please verify your GITHUB_TOKEN.")
            except RateLimitError:
                st.error("GitHub API rate limit exceeded. Please try again later.")
            except Exception:
                st.error("An unexpected error occurred while fetching data.")


if __name__ == "__main__":
    main()
