# Webアプリ作成用最低限のテンプレートです。
Docker Compose で動かせる `FastAPI + Next.js` テンプレートです。

## 構成

- `backend/`: FastAPI + SQLAlchemy + SQLite + Alembic + uv + ruff + mypy
- `frontend/`: Next.js + TypeScript + Tailwind CSS + Orval

## Backend コマンド

`backend/` で実行します。

- `make install`: 依存関係をインストール
- `make fmt`: フォーマット + ruff 自動修正
- `make lint`: ruff + mypy
- `make gen`: `api.yml` を更新
- `make dev`: `localhost:8000` で起動
- `make migrate-create name=init`: Alembic マイグレーション作成
- `make migrate-up`: Alembic マイグレーション適用

## Frontend コマンド

`frontend/` で実行します。

- `yarn fmt`: コード整形
- `yarn lint`: lint + 型チェック
- `yarn build`: ビルド
- `yarn gen`: `../backend/api.yml` から `src/gen/` を生成
- `yarn dev`: `localhost:3000` で起動

## Docker Compose

### 開発

```bash
docker compose up --build
```

### 本番相当

```bash
docker compose -f docker-compose.prod.yml up --build
```
