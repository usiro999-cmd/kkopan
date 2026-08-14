use sqlx::SqlitePool;
use anyhow::{Context, Result};
use chrono::Utc;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct ConversationRecord {
    pub id: i64,
    pub session_id: String,
    pub user_message: String,
    pub ai_response: String,
    pub created_at: String,
}

pub struct ChatRepository {
    pool: SqlitePool,
}

impl ChatRepository {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }

    pub async fn init_db(&self) -> Result<()> {
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"
        )
        .execute(&self.pool)
        .await
        .context("会話テーブル作成に失敗しました")?;

        Ok(())
    }

    pub async fn save_conversation(
        &self,
        session_id: &str,
        user_message: &str,
        ai_response: &str,
    ) -> Result<ConversationRecord> {
        let now = Utc::now().to_rfc3339();
        
        let result = sqlx::query(
            "INSERT INTO conversations (session_id, user_message, ai_response, created_at) 
             VALUES (?, ?, ?, ?)"
        )
        .bind(session_id)
        .bind(user_message)
        .bind(ai_response)
        .bind(&now)
        .execute(&self.pool)
        .await
        .context("会話保存に失敗しました")?;

        Ok(ConversationRecord {
            id: result.last_insert_rowid(),
            session_id: session_id.to_string(),
            user_message: user_message.to_string(),
            ai_response: ai_response.to_string(),
            created_at: now,
        })
    }

    pub async fn get_conversation_history(&self, session_id: &str, limit: i64) -> Result<Vec<ConversationRecord>> {
        let records = sqlx::query_as::<_, (i64, String, String, String, String)>(
            "SELECT id, session_id, user_message, ai_response, created_at 
             FROM conversations 
             WHERE session_id = ? 
             ORDER BY created_at DESC 
             LIMIT ?"
        )
        .bind(session_id)
        .bind(limit)
        .fetch_all(&self.pool)
        .await
        .context("会話履歴取得に失敗しました")?;

        Ok(records.into_iter().map(|(id, session_id, user_message, ai_response, created_at)| {
            ConversationRecord {
                id,
                session_id,
                user_message,
                ai_response,
                created_at,
            }
        }).collect())
    }
}
