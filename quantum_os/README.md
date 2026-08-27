# Multiverse Quantum OS

Ubuntu 24.04ベースのDocker量子開発環境です。Qiskit、Aer、QDK、
Azure Quantum SDK、RDKit、JupyterLabを非rootユーザーで実行します。

## 起動

```bash
cd quantum_os
cp .env.example .env
# JUPYTER_TOKENを長いランダム値へ変更
docker compose -f compose.yml up --build -d
```

ブラウザで `http://localhost:8888/lab?token=<JUPYTER_TOKEN>` を開きます。

## CLI

```bash
docker compose -f compose.yml run --rm quantum-os quantum-info
docker compose -f compose.yml run --rm quantum-os \
  python /opt/quantum-os/examples/bell.py
docker compose -f compose.yml run --rm quantum-os bash
```

Azure Quantumを使う場合は `.env` にWorkspaceとAzure Identityの設定を追加します。
秘密情報をイメージへ埋め込まず、Gitにも登録しないでください。

## Blueqat MCP

VS Codeでこのリポジトリを開くと、[`.vscode/mcp.json`](../.vscode/mcp.json)の
`blueqat`サーバーを起動できます。初回起動時に`uv`がPython 3.12と固定済み依存関係を
準備します。

MCPはBlueqat 2.0.4のNumPyバックエンドを使い、次のツールを提供します。

- `simulate_circuit`: 測定結果とOpenQASM 2を返す
- `circuit_statevector`: 非ゼロ振幅を返す
- `export_qasm`: 検証済み回路をOpenQASM 2へ変換する

任意のPythonコードは実行せず、許可ゲート、最大20量子ビット、最大500ゲート、
最大10,000 shotsに制限しています。

## Webアップデート

`http://localhost:9090` を開き、ユーザー名 `admin` と
`UPDATE_ADMIN_PASSWORD` でログインします。更新サービスは次をすべて検証します。

- GitHubリポジトリとリリースタグ
- Ed25519署名
- 許可されたGHCRイメージ名
- SHA-256イメージダイジェスト
- 更新後コンテナのヘルスチェック

失敗時は以前のコンテナへ自動的に戻します。

管理画面は標準で `127.0.0.1` のみに公開されます。別端末から利用する場合は
認証付きHTTPSリバースプロキシを用意してから `UPDATER_BIND` を変更してください。
平文HTTPのまま外部へ公開しないでください。

### 初回の署名鍵設定

```bash
docker run --rm -i multiverse-quantum-os-updater:1 python - <<'PY'
import base64
from nacl.signing import SigningKey
key = SigningKey.generate()
print("GitHub secret QUANTUM_OS_UPDATE_SIGNING_KEY:")
print(base64.b64encode(bytes(key)).decode())
print("quantum_os/.env UPDATE_PUBLIC_KEY:")
print(base64.b64encode(bytes(key.verify_key)).decode())
PY
```

秘密鍵はGitHub Actions Secretだけに保存し、公開鍵のみを`.env`へ設定します。
GitHubで `quantum-os-v1.0.0` のようなタグをpushすると、Workflowがイメージと
署名済み更新情報をReleaseへ公開します。

### WWWからAI拡張を導入

Web管理画面の「AIパックを確認」「署名済みAIを導入」を使用します。AIは
量子OS本体ではなく専用の読み取り専用ボリュームからJupyterカーネルとして
読み込まれます。

初期AIパックには次が含まれます。

- scikit-learnによる説明可能Ridgeモデル
- 合成学習データと検証指標
- 特徴量寄与の表示
- 大学院向け実験サンプル

実在薬の薬効・安全性・臨床結果を予測するものではありません。

AIパックを公開するには `quantum-ai-v1.0.0` のようなタグをpushします。
OS更新と同じEd25519署名鍵でマニフェストが署名され、GHCRイメージは
SHA-256ダイジェストへ固定されます。

Docker SocketのグループIDは次で確認し、`.env`の`DOCKER_GID`へ設定します。

```bash
stat -c '%g' /var/run/docker.sock
```
