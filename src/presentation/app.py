import logging

import streamlit as st

from src.services.dashboard_controller import DashboardController
from src.services.exceptions import DashboardError

logger = logging.getLogger(__name__)


def main() -> None:
    st.set_page_config(page_title="GitHub Analytics Dashboard", layout="wide")
    st.title("GitHub Repository Analytics PoC")

    st.write("Enter a GitHub repository in the format `owner/repo` to analyze its recent metrics.")

    repo_input = st.text_input("Repository (e.g. streamlit/streamlit):", placeholder="owner/repo")
    analyze_button = st.button("Analyze")

    if analyze_button and repo_input:
        controller = DashboardController()

        try:
            with st.spinner("Fetching data..."):
                result = controller.get_dashboard_data(repo_input)

            if result.cached:
                st.success("Data loaded from local cache.")

            # Render KPIs
            col1, col2, col3 = st.columns(3)
            col1.metric("Stars", str(result.repo_info.stargazers_count))
            col2.metric("Forks", str(result.repo_info.forks_count))
            col3.metric("Open Issues", str(result.repo_info.open_issues_count))

            st.divider()

            # Render Charts
            st.subheader("Commit History (Recent)")
            # Convert Polars DataFrame to Pandas for Streamlit compatibility if needed, but Streamlit often handles Arrow/Polars
            st.line_chart(result.commits_by_date.to_pandas(), x="date", y="commit_count")

            st.subheader("Top Committers")
            st.bar_chart(result.top_committers.to_pandas(), x="name", y="commit_count")

        except DashboardError as e:
            st.error(e.message)
        except Exception:
            logger.exception("Unexpected error in UI")
            st.error("An unexpected error occurred. Please check the logs.")


if __name__ == "__main__":
    main()
