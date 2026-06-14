# 世界の株価 個別

世界の株式銘柄をリアルタイムで監視できるダッシュボードアプリです。銘柄を自由に追加・削除・並べ替えでき、ミニチャートや詳細チャート、テクニカル指標、ファンダメンタルズ情報を確認できます。
<img width="1912" height="1072" alt="image" src="https://github.com/user-attachments/assets/5f2454d8-2e38-4e6f-babd-a2ffab4f4434" />
<img width="1173" height="867" alt="image" src="https://github.com/user-attachments/assets/7c8c3b7f-2c0c-4f82-9b69-24489f2fe572" />
<img width="1142" height="175" alt="image" src="https://github.com/user-attachments/assets/e8a2cbd2-9879-49b1-adf3-5c7c249894b2" />




## 機能

- **リアルタイム更新**: SSE (Server-Sent Events) による近リアルタイムな株価・チャート配信
- **銘柄検索・追加**: 銘柄コード・名称で検索して一覧に追加
- **ドラッグ＆ドロップ並べ替え**: カード表示の順番を自由に変更
- **ダークモード**: ライト/ダーク切り替え
- **ミニチャート**: 各銘柄カードに当日のインデイチャートを表示
- **詳細チャート**: ローソク足・期間選択・テクニカル指標 (MA, RSI, MACD など)
- **ファンダメンタルズ**: PER・PBR・配当利回りなどの基本財務指標
- **EDINET 書類**: 上場企業の有価証券報告書リンク
- **永続化**: 選択銘柄・表示順を localStorage に保存（再訪時も復元）

## 技術スタック

| レイヤー | 技術 |
|--------|------|
| Backend | Python 3.10 / FastAPI / SQLAlchemy / SQLite / Alembic |
| データ取得 | yfinance / pandas / ta (テクニカル指標) / APScheduler |
| 外部 API | EDINET API |
| Frontend | Next.js 15 / React 19 / TypeScript / Tailwind CSS |
| チャート | lightweight-charts v4 |
| DnD | @dnd-kit |
| API 生成 | Orval (OpenAPI → TypeScript クライアント自動生成) |
| 開発環境 | uv / ruff / mypy / Prettier / ESLint |
| インフラ | Docker / Docker Compose |

## ディレクトリ構成

```
.
├── backend/          # FastAPI バックエンド
│   ├── app/
│   │   ├── api/      # ルーター (search, quote, stream, history, indicators, filings …)
│   │   ├── application/   # ユースケース・インターフェース
│   │   ├── domain/        # ドメインモデル
│   │   ├── infrastructure/# yfinance・SSE ブロードキャスター等の実装
│   │   └── core/          # 設定
│   ├── alembic/      # DBマイグレーション
│   └── codes.csv     # 銘柄マスタ
└── frontend/         # Next.js フロントエンド
    └── src/
        ├── app/           # ページ
        ├── components/    # TickerTile / SearchModal / FullChart / FundamentalsPanel …
        ├── hooks/         # useSSE / useLayout / useDarkMode
        ├── gen/           # Orval 自動生成コード
        └── lib/           # API クライアント設定
```

## セットアップ

### 環境変数

`backend/.env` に以下を設定してください。

```env
EDINET_API_KEY=<あなたのEDINET APIキー>
```

EDINET API キーは [EDINET API](https://disclosure2.edinet-fsa.go.jp/webd/api/APIInfoController.do) から取得できます。

### Docker Compose（推奨）

```bash
# 開発環境
docker compose up --build

# 本番相当
docker compose -f docker-compose.prod.yml up --build
```

起動後、`http://localhost:3000` でアクセスできます。

### ローカル起動（Docker なし）

**Backend** (`backend/` で実行)

```bash
make install   # 依存関係のインストール (uv sync)
make dev       # localhost:8000 で起動
```

**Frontend** (`frontend/` で実行)

```bash
yarn install
yarn dev       # localhost:3000 で起動
```

## 開発コマンド

### Backend

```bash
make install          # 依存関係をインストール
make fmt              # フォーマット + ruff 自動修正
make lint             # ruff + mypy
make gen              # api.yml (OpenAPI スキーマ) を更新
make dev              # localhost:8000 で起動
make migrate-create name=<名前>  # Alembic マイグレーション作成
make migrate-up       # Alembic マイグレーション適用
```

### Frontend

```bash
yarn fmt     # Prettier でコード整形
yarn lint    # ESLint + 型チェック
yarn build   # プロダクションビルド
yarn gen     # ../backend/api.yml から src/gen/ を生成
yarn dev     # localhost:3000 で起動
```

## API エンドポイント

| メソッド | パス | 説明 |
|--------|------|------|
| GET | `/search` | 銘柄検索 |
| GET | `/quote/{ticker}` | 現在の株価スナップショット |
| GET | `/history/{ticker}` | 過去の株価履歴 |
| GET | `/indicators/{ticker}` | テクニカル指標 |
| GET | `/filings/{ticker}` | EDINET 書類一覧 |
| GET | `/stream` | SSE ストリーム (リアルタイム更新) |
| GET | `/health` | ヘルスチェック |
