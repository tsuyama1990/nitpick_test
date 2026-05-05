import streamlit as st

from src.presentation.controller import get_dashboard_data


def render_dashboard() -> None:
    """Renders the Streamlit dashboard."""
    st.set_page_config(page_title="GitHub Repo Analysis", page_icon="📊", layout="wide")

    st.title("GitHub Repository Analysis Dashboard")
    st.write("Enter a repository name to view its commits and statistics.")

    repo_name = st.text_input("Repository (owner/repo):", placeholder="e.g. streamlit/streamlit")

    if not repo_name:
        return

    with st.spinner("Fetching and processing data..."):
        result = get_dashboard_data(repo_name)

    if isinstance(result, str):
        st.error(result)
        return

    # Render KPIs
    st.header("Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Stars", result.repo_metadata.stargazers_count)
    col2.metric("Total Forks", result.repo_metadata.forks_count)
    col3.metric("Open Issues", result.repo_metadata.open_issues_count)

    st.divider()

    # Render Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Daily Commit Trends")
        # Ensure we're passing standard data to Streamlit line_chart
        st.line_chart(data=result.daily_commits_df.to_pandas().set_index("date"), y="commit_count")

    with col2:
        st.subheader("Top 5 Committers")
        st.bar_chart(
            data=result.top_committers_df.to_pandas().set_index("author_name"), y="commit_count"
        )


if __name__ == "__main__":
    render_dashboard()
