import logging
import re

import streamlit as st

from src.ingestion import GitHubClient, GitHubClientError
from src.storage import load_cached_dataframe, save_dataframe_to_cache
from src.transformation import aggregate_commits_by_author, aggregate_commits_by_date

logger = logging.getLogger(__name__)


def is_valid_repo_format(repo_str: str) -> bool:
    return bool(re.match(r"^[\w.-]+/[\w.-]+$", repo_str))


def main() -> None:
    st.title("GitHub Repository Analytics Dashboard")

    repo_input = st.text_input("オーナー名/リポジトリ名", placeholder="例: streamlit/streamlit")

    if st.button("データ取得"):
        if not repo_input:
            st.warning("リポジトリ名を入力してください。")
            return

        if not is_valid_repo_format(repo_input):
            st.warning("`owner/repo` の形式で入力してください")
            return

        owner, repo = repo_input.split("/")

        client = GitHubClient()

        try:
            # 1. Fetch KPI Metrics
            with st.spinner("リポジトリ情報を取得中..."):
                repo_info = client.get_repository_info(owner, repo)

            # Display KPIs
            col1, col2, col3 = st.columns(3)
            col1.metric("Stars", repo_info.stargazers_count)
            col2.metric("Forks", repo_info.forks_count)
            col3.metric("Open Issues", repo_info.open_issues_count)

            # 2. Fetch or Load Commits
            cache_key = f"commits_{owner}_{repo}".replace("-", "_")

            commits_date_df = load_cached_dataframe(f"{cache_key}_date")
            commits_author_df = load_cached_dataframe(f"{cache_key}_author")

            if commits_date_df is None or commits_author_df is None:
                with st.spinner("コミット履歴を取得し処理しています..."):
                    commits = client.get_commits(owner, repo)

                    commits_date_df = aggregate_commits_by_date(commits)
                    commits_author_df = aggregate_commits_by_author(commits)

                    # Save to cache
                    save_dataframe_to_cache(commits_date_df, f"{cache_key}_date")
                    save_dataframe_to_cache(commits_author_df, f"{cache_key}_author")

            else:
                st.info("キャッシュからデータを読み込みました。")

            # 3. Display Visualizations
            st.subheader("日付ごとのコミット数推移")
            if not commits_date_df.is_empty():
                # Convert to pandas for Streamlit if needed, although native polars support might exist
                st.line_chart(
                    data=commits_date_df.to_pandas(), x="date", y="commit_count"
                )
            else:
                st.write("コミットデータがありません。")

            st.subheader("コミッター別コミット数(上位5名)")
            if not commits_author_df.is_empty():
                st.bar_chart(
                    data=commits_author_df.to_pandas(), x="author", y="commit_count"
                )
            else:
                st.write("コミットデータがありません。")

        except GitHubClientError as e:
            st.error(str(e))
        except Exception as e:
            logger.exception("予期せぬエラーが発生しました")
            st.error(f"予期せぬエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
