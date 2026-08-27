# Multiverse Quantum AI Research Academy

大学院向けの教育用量子AI創薬シミュレーターです。すべての候補、標的スコア、
学習ラベルは合成データであり、医療・臨床・実際の創薬判断には使用できません。
核融合研究アシスタントも、教育用の0次元D-Tプラズマモデルです。

## Stack

- Next.js + TypeScript
- FastAPI + SQLAlchemy
- PostgreSQL
- Azure OpenAI
- RDKit
- Qiskit
- Azure Quantum

## Start

```bash
cd quantum_app
cp .env.example .env
# .env の POSTGRES_PASSWORD を変更
docker compose up --build
```

- Web: <http://localhost:3000>
- Fusion Research Copilot: <http://localhost:3000/fusion>
- API docs: <http://localhost:8000/docs>

ポートが使用中の場合は `.env` の `WEB_PORT` / `API_PORT` を変更できます。
VPSへ公開する場合は、`PUBLIC_API_URL`と`CORS_ORIGINS`を実際のHTTPS URL、
またはサーバーの公開IPとポートへ変更してからビルドしてください。

Azure OpenAIチューターを使う場合は、`.env` にエンドポイント、APIキー、
デプロイ名を設定してください。未設定の場合、チューターAPIは `503` を返します。

## Fusion Research Copilot

`/fusion`では温度、密度、閉じ込め時間、磁場、装置寸法、加熱入力を比較し、
Lawson三重積、体積平均β、D-T核融合出力、α加熱、輸送損失の教育的推定を表示します。
AIアシスタントは計算コンテキストを使って、欠落している物理、安定性、輸送、
実験計画を説明します。結果は炉設計、安全解析、制御、施設運転には使用できません。

## Azure Quantum

推奨認証はWorkspace Resource IDとAzure Identityです。

```env
AZURE_QUANTUM_RESOURCE_ID=/subscriptions/.../resourceGroups/.../providers/Microsoft.Quantum/Workspaces/...
AZURE_QUANTUM_DEFAULT_TARGET=ionq.simulator
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...
```

代わりに `AZURE_QUANTUM_CONNECTION_STRING` も利用できますが、秘密として安全に
管理してください。画面からターゲット一覧を取得し、Bell回路を送信できます。

## Test

```bash
docker compose run --rm api python -m pytest
docker compose run --rm web npm run typecheck
```
