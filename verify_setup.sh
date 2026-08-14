#!/bin/bash
# 🚀 ChatGPT Integration Verification Script

set -e

PROJECT_DIR="/home/kosakayasuhiro/myapp/hello_rust/my_axum_app"
cd "$PROJECT_DIR"

echo "======================================"
echo "🤖 ChatGPT Integration Verification"
echo "======================================"
echo ""

# 1. .env ファイルの確認
echo "📋 Checking .env file..."
if [ -f ".env" ]; then
    if grep -q "OPENAI_API_KEY=" .env; then
        KEY=$(grep "OPENAI_API_KEY=" .env | cut -d'=' -f2)
        if [[ $KEY == sk-* ]]; then
            echo "✅ .env file exists with valid API key format"
            echo "   Key: ${KEY:0:20}...${KEY: -10}"
        else
            echo "⚠️  API key format seems incorrect (should start with 'sk-')"
        fi
    else
        echo "❌ OPENAI_API_KEY not found in .env"
    fi
else
    echo "❌ .env file not found"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "   Please edit .env and add your API key!"
fi
echo ""

# 2. プロジェクトのビルド確認
echo "🔨 Checking build status..."
if cargo check 2>&1 | grep -q "Finished"; then
    echo "✅ Project builds successfully"
else
    echo "❌ Build failed"
    exit 1
fi
echo ""

# 3. 依存関係の確認
echo "📦 Checking dependencies..."
DEPS=("reqwest" "serde" "sqlx" "tokio" "axum")
for dep in "${DEPS[@]}"; do
    if grep -q "$dep" Cargo.toml; then
        echo "✅ $dep is included"
    else
        echo "❌ $dep not found"
    fi
done
echo ""

# 4. ソースファイルの確認
echo "📁 Checking source files..."
FILES=("src/main.rs" "src/llm.rs" "src/chat.rs" "src/embedding.rs" "src/rag.rs" "src/reasoning.rs")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        LINES=$(wc -l < "$file")
        echo "✅ $file ($LINES lines)"
    else
        echo "❌ $file not found"
    fi
done
echo ""

# 5. API エンドポイントの確認
echo "🔗 Checking API endpoints..."
ENDPOINTS=("/health" "/chat" "/chat-rag" "/reasoning" "/history")
for endpoint in "${ENDPOINTS[@]}"; do
    if grep -q "\"$endpoint\"" src/main.rs; then
        echo "✅ $endpoint endpoint is defined"
    else
        echo "❌ $endpoint endpoint not found"
    fi
done
echo ""

# 6. 実行ガイドの表示
echo "======================================"
echo "🚀 Next Steps:"
echo "======================================"
echo ""
echo "1️⃣  Set your OpenAI API key:"
echo "   export OPENAI_API_KEY='sk-your-actual-key'"
echo ""
echo "2️⃣  Start the server:"
echo "   cargo run"
echo ""
echo "3️⃣  In another terminal, test with:"
echo "   python3 test_client.py"
echo ""
echo "4️⃣  Or use interactive mode:"
echo "   python3 test_client.py interactive"
echo ""
echo "5️⃣  Or test with curl:"
echo "   curl -X POST http://127.0.0.1:8080/chat \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"message\":\"こんにちは\"}'"
echo ""
echo "======================================"
echo "✨ Setup verification complete!"
echo "======================================"
