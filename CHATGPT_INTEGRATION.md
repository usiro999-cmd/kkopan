# 🚀 ChatGPT連携 実行ガイド

## ステップ1: OpenAI API キーの取得

1. https://platform.openai.com/api/keys にアクセス
2. 「Create new secret key」をクリック
3. キーをコピー（⚠️ 二度と表示されません）

```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## ステップ2: .env ファイルの設定

```bash
cd /home/kosakayasuhiro/myapp/hello_rust/my_axum_app

# .env ファイルを作成
cat > .env << EOF
OPENAI_API_KEY=sk-your-actual-key-here
EOF
```

**またはこのコマンドで直接設定：**

```bash
echo "OPENAI_API_KEY=sk-your-actual-key-here" > .env
```

## ステップ3: サーバーの起動

```bash
cargo run
```

出力：
```
🚀 Server running on http://127.0.0.1:8080
```

## ステップ4: テスト実行

### オプション A: テストスクリプト（Python）

```bash
# 自動テスト実行
python3 test_client.py

# 対話モード
python3 test_client.py interactive
```

### オプション B: curl でテスト

#### 1. ヘルスチェック
```bash
curl http://127.0.0.1:8080/health
```

#### 2. 通常チャット（LLMのみ）
```bash
curl -X POST http://127.0.0.1:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "こんにちは。あなたは誰ですか？",
    "session_id": "user-001"
  }'
```

**レスポンス例：**
```json
{
  "session_id": "user-001",
  "user_message": "こんにちは。あなたは誰ですか？",
  "ai_response": "こんにちは！私はOpenAIによって開発されたAIアシスタント、ChatGPTです。..."
}
```

#### 3. RAG チャット（知識ベース統合）
```bash
curl -X POST http://127.0.0.1:8080/chat-rag \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Rust についての良い学習リソースは何ですか？",
    "session_id": "user-002",
    "use_rag": true
  }'
```

#### 4. 推論チャット（Chain-of-Thought）
```bash
curl -X POST http://127.0.0.1:8080/reasoning \
  -H "Content-Type: application/json" \
  -d '{
    "message": "なぜプログラミングは重要なスキルなのか？",
    "session_id": "user-003"
  }'
```

#### 5. 履歴確認
```bash
curl http://127.0.0.1:8080/history/user-001
```

## 🎯 実装例

### Node.js クライアント

```javascript
const axios = require('axios');

async function chatWithChatGPT() {
  try {
    const response = await axios.post('http://127.0.0.1:8080/chat', {
      message: 'AI について教えてください',
      session_id: 'nodejs-session'
    });
    
    console.log('AI:', response.data.ai_response);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

chatWithChatGPT();
```

### Python クライアント

```python
import requests

response = requests.post(
    'http://127.0.0.1:8080/chat',
    json={
        'message': 'Python について教えてください',
        'session_id': 'python-session'
    }
)

print('AI:', response.json()['ai_response'])
```

### cURL ワンライナー

```bash
# シンプルなチャット
curl -X POST http://127.0.0.1:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"こんにちは"}' | jq '.ai_response'

# パイプで会話を複数連鎖
curl -s -X POST http://127.0.0.1:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"今日の天気は？"}' | jq -r '.ai_response' | head -3
```

## 🔍 トラブルシューティング

### エラー: `OPENAI_API_KEY not found`

```
❌ Error: couldn't create client: couldn't get default credential
```

**解決方法：**
```bash
# .env ファイルが存在するか確認
cat .env

# API キーが正しいか確認（sk- で始まる）
echo $OPENAI_API_KEY
```

### エラー: `Invalid authentication`

```
❌ 401 Unauthorized: Invalid API Key
```

**解決方法：**
- API キーが正しくコピーされているか確認
- 新しいキーを生成してみる
- https://platform.openai.com/account/billing/overview で認証情報を確認

### エラー: `Rate limit exceeded`

```
❌ 429 Too Many Requests
```

**解決方法：**
- リクエストの頻度を下げる
- キューイング機能を追加
- OpenAI Organizationの rate limit を確認

### エラー: `Connection refused`

```
❌ Connection refused: 127.0.0.1:8080
```

**解決方法：**
```bash
# サーバーが起動しているか確認
ps aux | grep my_axum_app

# ポート 8080 が使用中か確認
lsof -i :8080

# サーバーを再起動
cargo run
```

## 💰 API 使用料の確認

https://platform.openai.com/account/billing/overview にアクセスして、使用量と料金を確認できます。

**料金目安（2024年）：**
- GPT-4: $0.03/1K tokens (input)
- GPT-3.5: $0.0005/1K tokens (input)

## 📊 パフォーマンスモニタリング

```bash
# サーバーのログを監視
tail -f server.log

# リアルタイムで応答時間を計測
time curl -X POST http://127.0.0.1:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"テスト"}'
```

## 🔐 セキュリティチェックリスト

- ✅ API キーを .gitignore に追加
- ✅ 本番環境では環境変数を使用
- ✅ API キーをログに出力しない
- ✅ HTTPS を使用する（本番環境）
- ✅ レート制限を実装する

## 📚 次のステップ

1. **メモリ機能の追加** - 長期会話の履歴管理
2. **複数 LLM プロバイダ対応** - Claude, Cohere など
3. **ストリーミング応答** - リアルタイム出力
4. **Web フロントエンド** - UI の構築

---

**🚀 ChatGPT との連携が完全に完成しました！**
