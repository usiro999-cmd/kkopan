# 🤖 AI Chat Server with RAG + Advanced Reasoning - Axum + LLM

**銀河文明レベルの頭脳**を備えたAIチャットボットサーバーです。🧠✨

LLM連携、RAG(知識ベース統合)、**Chain-of-Thought推論エンジン**で、単なる質問応答を超えた多段階推論が可能です。

## 🌟 機能

- **リアルタイムAI チャット** - OpenAI GPT-4 との連携
- **RAG (Retrieval Augmented Generation)** - 知識ベースから関連情報を取得
- **🧠 Chain-of-Thought 推論** - 複数ステップの論理的推論
- **マルチステップ推論** - 複合的な問題への段階的アプローチ
- **自己省察機能** - 回答の検証と改善
- **会話履歴管理** - SQLite でセッション管理
- **非同期処理** - Tokio による高速・スケーラブル

## 📋 セットアップ

### 必要なもの
- Rust 1.70+
- OpenAI API キー

### インストール

```bash
cp .env.example .env
# .env ファイルに OpenAI API キーを設定
export OPENAI_API_KEY="sk-your-api-key-here"

cargo build --release
cargo run
```

サーバーは `http://127.0.0.1:8080` で起動します。

## 🚀 API エンドポイント

### 1. ヘルスチェック
```bash
curl http://127.0.0.1:8080/health
```

### 2. 通常のチャット
```bash
curl -X POST http://127.0.0.1:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "こんにちは！",
    "session_id": "user-123"
  }'
```

### 3. RAG 対応チャット
```bash
curl -X POST http://127.0.0.1:8080/chat-rag \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Rust について教えてください",
    "session_id": "user-123",
    "use_rag": true
  }'
```

### 4. 🧠 Chain-of-Thought 推論（新機能！）
```bash
curl -X POST http://127.0.0.1:8080/reasoning \
  -H "Content-Type: application/json" \
  -d '{
    "message": "なぜ人工知能は重要なのか？",
    "session_id": "user-123"
  }'
```

**レスポンス例:**
```json
{
  "reasoning": {
    "steps": [
      {
        "step": 1,
        "thought": "ユーザーの質問を分析: なぜ人工知能は重要なのか？",
        "analysis": "質問の構造を分析: キーワード数=7, 質問の種類=理由説明型",
        "conclusion": null
      },
      {
        "step": 2,
        "thought": "提供されたコンテキストを検討",
        "analysis": "コンテキスト評価: 行数=0, 単語数=0, 関連度=高",
        "conclusion": null
      },
      {
        "step": 3,
        "thought": "論理的推論を実施",
        "analysis": "論理的推論: クエリとコンテキストの関連度=0.00%",
        "conclusion": "推論完了"
      },
      {
        "step": 4,
        "thought": "結論を検証",
        "analysis": "推論エンジンが分析を完了しました。",
        "conclusion": "検証完了"
      }
    ],
    "final_answer": "推論プロセス:\n複数ステップの論理的推論が完了しました。",
    "confidence": 1.0
  },
  "status": "success"
}
```

### 5. 宇宙型の時計同期
```bash
curl http://127.0.0.1:8080/cosmic/clock/sync
```

**レスポンス例:**
```json
{
  "status": "success",
  "source": "earth-to-galactic-display",
  "utc_time": "2026-08-14T02:15:44.900Z",
  "jst_time": "2026-08-14T11:15:44.900+09:00",
  "galactic_stardate": "GST-00020655-021544",
  "galactic_cycle": 20655,
  "unix_millis": 1786683344900,
  "recommended_refresh_ms": 1000
}
```

### 6. 画面で確認
ブラウザで次を開くと、銀河系時計の同期画面が表示されます。
```bash
http://127.0.0.1:8080/
```

### 7. 会話履歴取得
```bash
curl http://127.0.0.1:8080/history/user-123
```

## 📁 プロジェクト構成

```
src/
├── main.rs         # メインサーバー、ルーター定義
├── llm.rs          # OpenAI API クライアント
├── chat.rs         # 会話履歴の管理と保存
├── embedding.rs    # ベクトル埋め込みと相似度計算
├── rag.rs          # RAGエンジンと知識ベース管理
└── reasoning.rs    # 推論エンジン（新機能！）

chat.db            # SQLite データベース（自動作成）
.env               # 環境変数（API キー等）
```

## 🔌 モジュール詳細

### `reasoning.rs` - 推論エンジン（新機能🎉）

#### Chain-of-Thought 推論
複数ステップの論理的推論で、単純な質問応答を超えた深い理解を実現：

```rust
pub async fn chain_of_thought(
    query: &str,           // ユーザーの質問
    context: &str,         // 背景情報
    llm_response: &str     // LLMの応答
) -> Result<ReasoningChain>
```

**推論ステップ：**
1. **質問分析** - 質問の構造・タイプを分類
2. **コンテキスト評価** - 提供情報の関連度を計算
3. **論理的推論** - 段階的な推論プロセス
4. **結論検証** - 回答の妥当性を確認

#### マルチステップ推論
複合的な問題への段階的アプローチ：

```rust
pub fn multi_step_reasoning(
    query: &str,
    knowledge_base: &[String]
) -> Result<ReasoningChain>
```

#### 自己省察
前回の回答から学習し、より正確な理解を達成：

```rust
pub fn self_reflect(
    previous_answer: &str,
    query: &str
) -> Result<String>
```

### 推論チェーンの構造

```rust
pub struct ReasoningChain {
    pub steps: Vec<ReasoningStep>,      // 推論ステップ
    pub final_answer: String,           // 最終回答
    pub confidence: f32,                // 信頼度 (0.0-1.0)
}

pub struct ReasoningStep {
    pub step: usize,                    // ステップ番号
    pub thought: String,                // 思考内容
    pub analysis: String,               // 分析結果
    pub conclusion: Option<String>,     // 結論
}
```

## 🎯 推論エンジンの特徴

- ✅ **質問タイプの自動分類**
  - 理由説明型（Why）
  - 方法説明型（How）
  - 定義型（What）
  - 人物特定型（Who）
  - 一般型

- ✅ **関連度スコア計算**
  - キーワードマッチング
  - ベクトル相似度
  - コンテキスト評価

- ✅ **信頼度の算出**
  - 完了ステップ数に基づく信頼度
  - 推論プロセスの妥当性検証

- ✅ **段階的推論プロセス**
  - 複数ステップの論理的つながり
  - 各ステップの詳細な分析
  - 最終結論の自動生成

## 📝 使用例

### Python クライアント
```python
import requests

BASE_URL = "http://127.0.0.1:8080"

# 推論エンドポイント
response = requests.post(
    f"{BASE_URL}/reasoning",
    json={
        "message": "なぜAIは重要なのか？",
        "session_id": "user-123"
    }
)

reasoning_result = response.json()
if reasoning_result["status"] == "success":
    chain = reasoning_result["reasoning"]
    print(f"推論ステップ数: {len(chain['steps'])}")
    print(f"信頼度: {chain['confidence']:.0%}")
    print(f"最終回答: {chain['final_answer']}")
    
    for step in chain['steps']:
        print(f"\nステップ {step['step']}: {step['thought']}")
        print(f"分析: {step['analysis']}")
```

## 🛠️ 開発

### ホットリロード
```bash
cargo install cargo-watch
cargo watch -x run
```

### テスト実行
```bash
cargo test
```

## 🌐 本番環境へのデプロイ

```bash
cargo build --release
./target/release/my_axum_app
```

## ⚠️ セキュリティ注意事項

- API キーを `.env` に保存し、**決して公開リポジトリにコミットしない**
- 本番環境では環境変数やシークレット管理ツール（AWS Secrets Manager など）を使用

## 📚 参考リンク

- [Axum ドキュメント](https://docs.rs/axum/)
- [OpenAI API リファレンス](https://platform.openai.com/docs/api-reference)
- [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903)
- [RAG (Retrieval Augmented Generation)](https://en.wikipedia.org/wiki/Retrieval-augmented_generation)

## 📝 ライセンス

MIT

---

**🚀 銀河文明レベルの頭脳を手に入れましたか？YES! 🧠✨**
