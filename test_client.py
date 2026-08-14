#!/usr/bin/env python3
"""
🤖 AI Chat Server Test Client
実際のOpenAI APIとの連携をテストします
"""

import requests
import json
import sys
from typing import Optional

BASE_URL = "http://127.0.0.1:8080"

def test_health():
    """ヘルスチェック"""
    print("🏥 ヘルスチェック...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print(f"✅ Server is running!\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")
        return True
    else:
        print(f"❌ Server not responding: {response.status_code}\n")
        return False

def test_chat(message: str, session_id: Optional[str] = None):
    """通常のチャット"""
    print(f"💬 Sending message: {message}")
    if not session_id:
        session_id = "test-session-001"
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": message,
            "session_id": session_id
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Chat Response:")
        print(f"  Session: {result['session_id']}")
        print(f"  User: {result['user_message']}")
        print(f"  AI: {result['ai_response']}\n")
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}\n")
        return None

def test_rag_chat(message: str, session_id: Optional[str] = None):
    """RAG対応チャット"""
    print(f"🔍 RAG Chat: {message}")
    if not session_id:
        session_id = "test-session-002"
    
    response = requests.post(
        f"{BASE_URL}/chat-rag",
        json={
            "message": message,
            "session_id": session_id,
            "use_rag": True
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ RAG Chat Response:")
        print(f"  Session: {result['session_id']}")
        print(f"  User: {result['user_message']}")
        print(f"  AI: {result['ai_response']}\n")
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}\n")
        return None

def test_reasoning(message: str, session_id: Optional[str] = None):
    """推論エンジン"""
    print(f"🧠 Reasoning: {message}")
    if not session_id:
        session_id = "test-session-003"
    
    response = requests.post(
        f"{BASE_URL}/reasoning",
        json={
            "message": message,
            "session_id": session_id
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("status") == "success":
            reasoning = result["reasoning"]
            print(f"✅ Reasoning Complete:")
            print(f"  Steps: {len(reasoning['steps'])}")
            print(f"  Confidence: {reasoning['confidence']:.0%}")
            print(f"  Final Answer: {reasoning['final_answer']}\n")
            
            print("  📊 Reasoning Steps:")
            for step in reasoning['steps']:
                print(f"    Step {step['step']}: {step['thought']}")
                print(f"      Analysis: {step['analysis']}")
                if step['conclusion']:
                    print(f"      Conclusion: {step['conclusion']}")
            print()
            return result
        else:
            print(f"❌ Error: {result.get('error')}\n")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}\n")
    return None

def test_history(session_id: str):
    """会話履歴取得"""
    print(f"📜 History for {session_id}:")
    response = requests.get(f"{BASE_URL}/history/{session_id}")
    
    if response.status_code == 200:
        result = response.json()
        conversations = result["conversations"]
        print(f"✅ Found {len(conversations)} conversations:\n")
        
        for conv in conversations:
            print(f"  User: {conv['user_message']}")
            print(f"  AI: {conv['ai_response']}")
            print(f"  Time: {conv['created_at']}\n")
        return result
    else:
        print(f"❌ Error: {response.status_code}\n")
    return None

def interactive_mode():
    """対話モード"""
    print("\n🤖 Interactive Chat Mode")
    print("Commands: /quit, /history, /rag, /reasoning, /clear")
    print("-" * 50)
    
    session_id = "interactive-session"
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "/quit":
                print("👋 Goodbye!")
                break
            elif user_input.lower() == "/history":
                test_history(session_id)
            elif user_input.lower() == "/rag":
                msg = input("RAG Message: ").strip()
                if msg:
                    test_rag_chat(msg, session_id)
            elif user_input.lower() == "/reasoning":
                msg = input("Reasoning Message: ").strip()
                if msg:
                    test_reasoning(msg, session_id)
            elif user_input.lower() == "/clear":
                session_id = f"session-{hash(str(__import__('time').time()))}"
                print(f"✨ New session: {session_id}")
            else:
                test_chat(user_input, session_id)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    print("=" * 60)
    print("🚀 AI Chat Server Test Client")
    print("=" * 60)
    
    # ヘルスチェック
    if not test_health():
        print("❌ Server not running!")
        print("   Start with: cargo run")
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        # 対話モード
        interactive_mode()
    else:
        # テストモード
        print("📋 Running tests...\n")
        
        # テスト1: 通常チャット
        test_chat("こんにちは！元気ですか？")
        
        # テスト2: RAG チャット
        test_rag_chat("Rust プログラミングについて教えてください")
        
        # テスト3: 推論
        test_reasoning("なぜ人工知能は重要なのか？")
        
        # テスト4: 履歴取得
        test_history("test-session-001")
        
        print("✅ All tests completed!")
        print("\n💡 Tip: Run with 'interactive' for interactive mode")
        print("   python3 test_client.py interactive")

if __name__ == "__main__":
    main()
