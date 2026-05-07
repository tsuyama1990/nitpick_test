import streamlit as st

from src.presentation.controller import DashboardController


def main() -> None:
    st.set_page_config(page_title="GitHub Analytics Dashboard", page_icon="📊", layout="wide")
    st.title("GitHub Analytics Dashboard")
    st.markdown("Enter a repository in `owner/repo` format to view metrics.")

    repo_input = st.text_input("Repository (e.g., streamlit/streamlit):", value="")

    if st.button("Analyze") and repo_input:
        if "/" not in repo_input:
            st.error("Invalid format. Please use 'owner/repo'.")
            return

        owner, repo = repo_input.split("/", 1)
        owner = owner.strip()
        repo = repo.strip()

        if not owner or not repo:
            st.error("Owner or repository cannot be empty.")
            return

        with st.spinner("Fetching data..."):
            controller = DashboardController()
            repo_info, commits_by_date, top_committers, error = controller.get_dashboard_data(owner, repo)

            if error:
                st.error(f"Error fetching data: {error}")
                return

            if repo_info is None:
                st.error("Could not fetch repository information.")
                return

            st.header("Repository Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("⭐ Stars", repo_info.stargazers_count)
            col2.metric("🍴 Forks", repo_info.forks_count)
            col3.metric("🐛 Open Issues", repo_info.open_issues_count)

            st.markdown("---")

            if commits_by_date is not None and not commits_by_date.is_empty():
                st.header("Commits by Date (Last 100)")
                # Convert to pandas for easier streamlit plotting
                df_date = commits_by_date.to_pandas()
                df_date.set_index("date", inplace=True)
                st.line_chart(df_date)
            else:
                st.info("No commit history found.")

            if top_committers is not None and not top_committers.is_empty():
                st.header("Top 5 Committers (Last 100)")
                df_users = top_committers.to_pandas()
                df_users.set_index("name", inplace=True)
                st.bar_chart(df_users)
            else:
                st.info("No top committers found.")

if __name__ == "__main__":
    main()
