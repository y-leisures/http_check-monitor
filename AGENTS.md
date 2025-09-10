# Repository Guidelines

## プロジェクト構成 & モジュール
- `check_website/`: Lambda 本体。`app.py` にハンドラと監視/通知/SQLite(S3) 操作を実装。
- `layers/`: Lambda Layer 用依存。`requirements.txt` を SAM がパッケージ化。
- `template.yaml`: AWS SAM テンプレート（関数/ロール/SNS/環境変数など）。
- `tests/`: 単体テスト（pytest）。`tests/unit/test_*.py` を推奨。
- 主要設定: `pyproject.toml`(ruff/mypy/依存), `Makefile`, `samconfig.toml`, `.pre-commit-config.yaml`。

## ビルド・テスト・開発コマンド
- 依存解決/実行: `uv run <cmd>`（Python 3.12 前提）
  - Lint: `uv run ruff check .` / Format: `uv run ruff format .`
  - 型チェック: `uv run mypy check_website`
  - テスト: `uv run pytest -q`
- SAM 操作（Makefile 経由）
  - ビルド: `make sam_build`
  - パッケージ: `make sam_package`
  - デプロイ: `make sam_deploy`（或いは `make sam_auto_deploy`/`make sam_dry_run`）
  - 削除: `make sam_delete`

## コーディング規約・命名
- スタイル: ruff 基準（行長 120、`py312` ターゲット）。自動整形は ruff-format。
- 型: mypy 有効。新規コードは関数/戻り値へ型注釈を付与。
- 命名: モジュール/関数/変数は`snake_case`、クラスは`CapWords`、定数は`UPPER_SNAKE_CASE`。

## テスト方針
- フレームワーク: pytest。ユニット志向で外部 I/O はモック化。
- 配置/命名: `tests/unit/test_*.py`。ケース毎に最小限の前提を用意。
- 実行例: `uv run pytest -q`。失敗再現のためログ/スタックトレースを PR に添付可。

## コミット & PR
- メッセージ規約: Conventional Commits を推奨（例: `feat: ...`, `fix: ...`, `refactor: ...`, `docs: ...`）。
- PR 要件: 目的/背景、変更点、テスト結果、関連 Issue、影響範囲を記載。CI(ruff/mypy/pytest) を green に。

## セキュリティ & 設定
- 機密値はコミット禁止。Slack Webhook は `template.yaml` の `WebhookUrl`/`SLACK_WEBHOOK_URL` 経由で注入。
- 監視対象 URL は `MONITOR_URL`、S3 は `S3_BUCKET`/`OBJECT_KEY_ON_S3`。ローカル実行例:
  ```bash
  export MONITOR_URL=https://example.com \
         SLACK_WEBHOOK_URL=*** \
         S3_BUCKET=my-bucket OBJECT_KEY_ON_S3=http_monitor/monitor.db
  ```
