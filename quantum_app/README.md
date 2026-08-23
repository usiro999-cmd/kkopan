# Multiverse Quantum AI Drug Discovery Academy

大学院向けの教育用量子AI創薬シミュレーターです。すべての候補、標的スコア、
学習ラベルは合成データであり、医療・臨床・実際の創薬判断には使用できません。

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
- API docs: <http://localhost:8000/docs>

ポートが使用中の場合は `.env` の `WEB_PORT` / `API_PORT` を変更できます。

Azure OpenAIチューターを使う場合は、`.env` にエンドポイント、APIキー、
デプロイ名を設定してください。未設定の場合、チューターAPIは `503` を返します。

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
