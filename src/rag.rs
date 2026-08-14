use sqlx::SqlitePool;
use anyhow::{Context, Result};
use chrono::Utc;
use serde::{Deserialize, Serialize};
use crate::embedding::{Document, EmbeddingGenerator, RetrievalResult};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct KnowledgeBase {
    pub id: String,
    pub title: String,
    pub description: String,
    pub created_at: String,
}

pub struct RAGRepository {
    pool: SqlitePool,
}

impl RAGRepository {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }

    pub async fn init_db(&self) -> Result<()> {
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB,
                metadata TEXT,
                created_at TEXT NOT NULL
            )"
        )
        .execute(&self.pool)
        .await
        .context("ドキュメントテーブル作成に失敗しました")?;

        sqlx::query(
            "CREATE TABLE IF NOT EXISTS knowledge_bases (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL
            )"
        )
        .execute(&self.pool)
        .await
        .context("知識ベーステーブル作成に失敗しました")?;

        Ok(())
    }

    pub async fn add_document(&self, doc: Document) -> Result<()> {
        let now = Utc::now().to_rfc3339();
        let embedding_blob = doc
            .embedding
            .as_ref()
            .map(|e| serde_json::to_string(e).unwrap_or_default());

        sqlx::query(
            "INSERT OR REPLACE INTO documents (id, title, content, embedding, metadata, created_at)
             VALUES (?, ?, ?, ?, ?, ?)"
        )
        .bind(&doc.id)
        .bind("Document")
        .bind(&doc.content)
        .bind(embedding_blob)
        .bind(doc.metadata.as_ref().map(|m| m.to_string()))
        .bind(&now)
        .execute(&self.pool)
        .await
        .context("ドキュメント追加に失敗しました")?;

        Ok(())
    }

    pub async fn retrieve_similar(&self, query: &str, limit: usize) -> Result<Vec<RetrievalResult>> {
        let query_embedding = EmbeddingGenerator::simple_embedding(query);

        let docs = sqlx::query_as::<_, (String, String)>(
            "SELECT id, embedding FROM documents LIMIT 100"
        )
        .fetch_all(&self.pool)
        .await
        .context("ドキュメント取得に失敗しました")?;

        let mut results: Vec<RetrievalResult> = docs
            .into_iter()
            .filter_map(|(id, embedding_str)| {
                let embedding: Vec<f32> = serde_json::from_str(&embedding_str).ok()?;
                let score = EmbeddingGenerator::cosine_similarity(&query_embedding, &embedding);
                Some((id, score))
            })
            .map(|(id, score)| {
                (
                    RetrievalResult {
                        document: Document {
                            id: id.clone(),
                            content: "Retrieved".to_string(),
                            embedding: None,
                            metadata: None,
                        },
                        score,
                    },
                    id,
                )
            })
            .map(|(result, _)| result)
            .collect();

        results.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap_or(std::cmp::Ordering::Equal));
        Ok(results.into_iter().take(limit).collect())
    }

    pub async fn get_document(&self, id: &str) -> Result<Option<String>> {
        let result = sqlx::query_as::<_, (String,)>(
            "SELECT content FROM documents WHERE id = ?"
        )
        .bind(id)
        .fetch_optional(&self.pool)
        .await
        .context("ドキュメント取得に失敗しました")?;

        Ok(result.map(|(content,)| content))
    }
}

pub struct RAGEngine {
    pub repo: RAGRepository,
}

impl RAGEngine {
    pub fn new(repo: RAGRepository) -> Self {
        Self { repo }
    }

    pub async fn augment_context(&self, query: &str, top_k: usize) -> Result<String> {
        let results = self.repo.retrieve_similar(query, top_k).await?;
        
        let context = results
            .into_iter()
            .map(|r| format!("- Score: {:.2} | ID: {}", r.score, r.document.id))
            .collect::<Vec<_>>()
            .join("\n");

        if context.is_empty() {
            Ok("No relevant documents found.".to_string())
        } else {
            Ok(format!("Relevant context:\n{}", context))
        }
    }
}
