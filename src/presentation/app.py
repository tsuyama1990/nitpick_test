import logging

import streamlit as st
from dotenv import load_dotenv

from src.ingestion.github_client import GitHubAPIError
from src.services.dashboard_controller import DashboardController

# Load variables from .env
load_dotenv()

# Setup pure logger
logger = logging.getLogger(__name__)

def main() -> None:
    st.set_page_config(page_title="GitHub Analytics", layout="wide")
    st.title("GitHub Repository Analytics PoC")
    st.write("Enter a repository in `owner/repo` format to view real-time metrics and commit trends.")

    # We use a form to prevent API calls on every keystroke
    with st.form("repo_input_form"):
        repo_input = st.text_input("Repository (e.g., streamlit/streamlit)", placeholder="owner/repo")
        submitted = st.form_submit_button("Analyze")

    if submitted:
        if not repo_input or "/" not in repo_input:
            st.warning("Please enter the repository in the format `owner/repo`.")
            return

        parts = repo_input.strip().split("/")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            st.warning("Please enter a valid `owner/repo` format.")
            return

        owner, repo = parts[0], parts[1]

        try:
            with st.spinner(f"Fetching data for {owner}/{repo}..."):
                controller = DashboardController()
                dashboard_data = controller.get_dashboard_data(owner, repo)

            # Display KPIs
            st.subheader("Repository Metrics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Stars", dashboard_data.metrics.stars)
            with col2:
                st.metric("Forks", dashboard_data.metrics.forks)
            with col3:
                st.metric("Open Issues", dashboard_data.metrics.open_issues)

            st.divider()

            # Display Charts
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.subheader("Daily Commits (Last 100)")
                # Streamlit line_chart expects data to be formatted, Polars handles this easily
                if not dashboard_data.daily_commits.is_empty():
                    df_daily = dashboard_data.daily_commits.to_pandas().set_index("date")
                    st.line_chart(df_daily)
                else:
                    st.info("No commit data available.")

            with col_chart2:
                st.subheader("Top 5 Committers")
                if not dashboard_data.top_committers.is_empty():
                    df_top = dashboard_data.top_committers.to_pandas().set_index("author_name")
                    st.bar_chart(df_top)
                else:
                    st.info("No committer data available.")

        except GitHubAPIError as e:
            # Handle specific API errors nicely without stack traces
            st.error(str(e))
        except Exception:
            # Catch unexpected errors to prevent stack trace leak
            logger.exception("An unexpected error occurred.")
            st.error("An unexpected internal error occurred. Please try again later.")

if __name__ == "__main__":
    main()
