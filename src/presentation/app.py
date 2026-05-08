"""Streamlit UI Application."""

import streamlit as st
from httpx import HTTPStatusError

# Must add project root to sys.path to run via streamlit cleanly if needed, though 'uv run' handles it
from src.presentation.controller import get_dashboard_data


def _handle_api_errors(e: Exception) -> None:
    """Helper to handle specific API errors to reduce complexity."""
    err_str = str(e)
    if isinstance(e, ValueError):
        if "404" in err_str:
            st.error("リポジトリが見つかりません。オーナー名とリポジトリ名を確認してください")
        else:
            st.error(f"Error: {e}")
    elif isinstance(e, PermissionError):
        if "403" in err_str:
            st.error("認証エラーが発生しました。トークンが有効か確認してください")
        else:
            st.error(f"Permission Error: {e}")
    elif isinstance(e, ConnectionError):
        if "429" in err_str:
            st.error("認証エラーが発生しました。トークンが有効か確認してください")
        else:
            st.error(f"Connection Error: {e}")
    elif isinstance(e, HTTPStatusError):
        st.error("認証エラーが発生しました。トークンが有効か確認してください")
    else:
        st.error("予期せぬエラーが発生しました。")


def _render_dashboard(owner: str, repo: str) -> None:
    """Render the dashboard elements."""
    with st.spinner(f"Fetching data for {owner}/{repo}..."):
        try:
            repo_info, daily_df, top_df = get_dashboard_data(owner, repo)

            # KPIs
            st.subheader("基本情報")
            col1, col2, col3 = st.columns(3)
            col1.metric("スター数", repo_info.stargazers_count)
            col2.metric("フォーク数", repo_info.forks_count)
            col3.metric("オープンIssue数", repo_info.open_issues_count)

            # Charts
            st.subheader("コミット履歴")
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.markdown("**日付ごとのコミット数推移**")
                if not daily_df.is_empty():
                    # Streamlit line_chart expects pandas dataframe or dict. Polars to_pandas handles it.
                    st.line_chart(daily_df.to_pandas(), x="date", y="commits")
                else:
                    st.info("No commit data found.")

            with col_chart2:
                st.markdown("**コミッター別コミット数（上位5名）**")  # noqa: RUF001
                if not top_df.is_empty():
                    st.bar_chart(top_df.to_pandas(), x="committer", y="commits")
                else:
                    st.info("No commit data found.")

        except Exception as e:
            _handle_api_errors(e)


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title="GitHub Analytics Dashboard", layout="wide")
    st.title("GitHub Analytics Dashboard")
    st.markdown("A simple PoC for analyzing GitHub repository metrics.")

    # Search bar
    repo_input = st.text_input(
        "Enter Repository (owner/repo):", placeholder="e.g., streamlit/streamlit"
    )

    if st.button("Analyze"):
        if not repo_input or "/" not in repo_input:
            st.warning("`owner/repo` の形式で入力してください")
            return

        owner, repo = repo_input.split("/", 1)
        owner = owner.strip()
        repo = repo.strip()

        if not owner or not repo:
            st.warning("`owner/repo` の形式で入力してください")
            return

        _render_dashboard(owner, repo)


if __name__ == "__main__":
    main()
