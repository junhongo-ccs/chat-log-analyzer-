# Chat Log Analyzer (チャットログ分析ツール)

仮想ヘルプAIの会話ログを分析し、ユーザーの困りごとや頻出する質問を可視化するツールです。

## 機能
- **キーワードランキング**: 頻出する単語を特定
- **カテゴリ自動分類**: Gemini APIを使用してメッセージを分類
- **フィルタリング**: 期間やカテゴリによる絞り込み
- **データエクスポート**: 分析結果のCSV出力

## セットアップと起動

1. **GitHubからクローン:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/chat-log-analyzer.git
   cd chat-log-analyzer
   ```

2. **ライブラリのインストール:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **環境変数の設定:**
   `.env.example` を `.env` にコピーし、`GEMINI_API_KEY` を記入してください。

4. **アプリケーションの起動:**
   ```bash
   streamlit run app.py
   ```

## デプロイ手順 (Streamlit Community Cloud)

1. **GitHubにプッシュ:**
   - このリポジトリを自身のGitHubアカウントにプッシュします。

2. **Streamlit Cloudと連携:**
   - [Streamlit Community Cloud](https://share.streamlit.io/) にログインし、`New app` をクリックします。
   - リポジトリ、ブランチ、メインファイル（`app.py`）を選択します。

3. **APIキー（Secrets）の設定:**
   - デプロイ設定の `Advanced settings` > `Secrets` に、以下のようにAPIキーを入力します。
     ```toml
     GEMINI_API_KEY = "あなたのAPIキー"
     ```

4. **デプロイ完了:**
   - 数分でデプロイが完了し、公開URLが発行されます。

## ファイル構成
- `app.py`: メインのUI (Streamlit)
- `analyzer.py`: 分析ロジック
- `data/`: サンプルデータ
- `utils/`: 共通ユーティリティ (ストップワード等)
