# User Test Scenarios: GitHub Analytics Dashboard PoC

本ドキュメントは、GitHubリポジトリ分析ダッシュボードのPoCが要件定義（ALL_SPEC.md）を厳密に満たしているかを検証するためのE2Eテストシナリオ群です。開発サイクル完了後、自動または手動で以下のシナリオをすべてパスすることを確認してください。

## Tutorial Strategy

To ensure seamless verification and an exceptional user experience, these scenarios will be executed via an interactive Marimo notebook. The notebook serves a dual purpose: as an automated testing suite and as an onboarding tutorial for new developers.

- **Mock Mode**: By default, the tutorial runs using mocked data and `pytest-httpx` simulated responses. This ensures CI/CD stability and allows users to explore the logic without needing a real GitHub API key.
- **Real Mode**: Users can provide a `.env` file with a valid `GITHUB_TOKEN` to execute the `@pytest.mark.live` scenarios, hitting the live GitHub REST API for real-time validation.

## Tutorial Plan

A **SINGLE** Marimo Text/Python file named `tutorials/UAT_AND_TUTORIAL.py` will be created. It will contain all scenarios (Quick Start + Advanced) in one cohesive document, utilizing Marimo's reactive cells for step-by-step verification and exploration of the system's capabilities.

## Tutorial Validation

Validation involves executing the Marimo notebook and ensuring all cells run successfully without errors, properly displaying the mocked (or real) data transformations and UI component simulations.

---

## Scenario 1: 正常系フルサイクルとキャッシュ挙動の厳格検証 (Strict Happy Path & Caching)

**目的**: アプリケーションが正常に動作し、かつキャッシュ機構がAPIのレートリミット保護として確実に機能していることを確認する。

**前提条件**:
- 有効なGitHub Personal Access Tokenが `.env` に設定されていること。
- アプリケーションが `streamlit run` で起動していること。

**テスト手順**:
1. StreamlitのUIから、実在する人気リポジトリ（例: `streamlit/streamlit` または `tiangolo/fastapi`）を入力し、データ取得を実行する。
2. **[検証]**: 画面上部に「スター数」「フォーク数」「オープンIssue数」がKPIとして表示され、APIから取得した実際の数値と一致していること。
3. **[検証]**: 「日付ごとのコミット数推移」「コミッター別コミット数（上位5名）」のグラフがエラーなく描画されていること。
4. アプリケーションのターミナル出力（ログ）を確認し、APIへのHTTPリクエスト（200 OK）が飛んだことを確認する。
5. 直後に、**全く同じリポジトリ名**で再度データ取得を実行する。
6. **[厳格な検証]**: 2回目の実行時は、ローカルの `.parquet` または `.csv` キャッシュからデータが読み込まれ、**GitHub APIへの追加のHTTPリクエストが一切発生していないこと**（ログで確認、またはUIのレスポンスが1回目より劇的に高速であること）。

---

## Scenario 2: 異常系・APIエラーハンドリング (Negative Flow & Error Handling)

**目的**: 無効な入力やAPIエラー発生時に、システムがクラッシュ（スタックトレースの露出）せず、ユーザーフレンドリーなエラーメッセージを表示できるか検証する。

**前提条件**: アプリケーションが起動していること。

**テスト手順**:
1. **存在しないリポジトリ（404エラー）**:
   - UIの入力欄に `non-existent-owner/invalid-repo-12345` を入力し実行する。
   - **[検証]**: アプリケーションがダウンせず、UI上に「リポジトリが見つかりません。オーナー名とリポジトリ名を確認してください」等の適切なエラー警告（`st.error` や `st.warning`）が表示されること。
2. **無効なフォーマットの入力**:
   - 入力欄に `invalid_repo_format_without_slash` を入力する。
   - **[検証]**: APIリクエストを送信する前にバリデーションが働き、「`owner/repo` の形式で入力してください」と警告が出ること。
3. **無効なトークン（401/403エラー）**:
   - `.env` のトークンを一時的にデタラメな文字列（例: `ghp_invalidtokenxxxx`）に書き換え、アプリを再起動する。
   - 存在するリポジトリ（例: `facebook/react`）を入力する。
   - **[検証]**: 「認証エラーが発生しました。トークンが有効か確認してください」という趣旨のメッセージがUIに表示され、生のJSONエラーレスポンスやスタックトレースが画面に漏洩していないこと。

---

## Scenario 3: セキュリティと環境構成要件の監査 (Security & Compliance Audit)

**目的**: コードベースに認証情報がハードコードされていないか、および機密情報のログ漏洩がないかを静的・動的に検証する。

**テスト手順**:
1. **シークレット分離の確認**:
   - プロジェクト内のすべての `.py` ファイルに対して、`ghp_` やパスワードらしき文字列がハードコードされていないことを `grep` 等で確認する。
   - **[検証]**: 認証情報はすべて `os.environ` または `dotenv` 経由で取得されていること。
2. **雛形ファイルの確認**:
   - プロジェクトルートに `.env.example` が存在することを確認する。
   - **[検証]**: `.env.example` の中身が `GITHUB_TOKEN=` のようにキーのみ（またはダミー値）であり、本物のトークンが含まれていないこと。
3. **ログ漏洩の確認 (動的検証)**:
   - Scenario 1（正常系）と Scenario 2（無効なトークンでの異常系）を実行する。
   - **[厳格な検証]**: アプリケーションを実行しているターミナルの標準出力・標準エラー出力に、`.env` から読み込んだ実際のトークン文字列が一切 `print` またはログ出力されていないことを目視および検索で確認する。

---

## Scenario 4: データ加工ロジックの厳密なバリデーション (Data Transformation Accuracy)

**目的**: Polarsを用いたデータ変換（集計・ソート・絞り込み）が、要件定義通りに正確に行われているかを検証する。

**前提条件**:
- Pytestが実行可能な環境であること。
- サンプルとして、固定のJSONモックデータ（ダミーのコミット履歴100件）がテスト用ディレクトリに用意されていること。

**テスト手順**:
1. テストフレームワーク（Pytest）を実行し、Transformationモジュール（Cycle 2で作成したPolarsの処理関数）のユニットテストを走らせる。
2. **[検証]**: 「日付ごとのコミット数」を集計するテストがパスすること。同日のコミットが正しく合算されていること。
3. **[検証]**: 「コミッター別のコミット数」を集計する関数に対し、6名以上のコミッターが存在するモックデータを渡した際、**正確にコミット数が多い順に「上位5名」のみ**が抽出されていること（同数の場合のタイブレーク処理でクラッシュしないことも含む）。
4. **[検証]**: 日付データ（ISO 8601形式などの文字列）が、Polars上で正しく `Date` または `Datetime` 型にキャストされてから集計されていること。
