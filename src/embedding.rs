use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Document {
    pub id: String,
    pub content: String,
    pub embedding: Option<Vec<f32>>,
    pub metadata: Option<serde_json::Value>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct RetrievalResult {
    pub document: Document,
    pub score: f32,
}

pub struct EmbeddingGenerator;

impl EmbeddingGenerator {
    pub fn simple_embedding(text: &str) -> Vec<f32> {
        let words: Vec<&str> = text.split_whitespace().collect();
        let mut embedding = vec![0.0; 384];
        
        for (_i, word) in words.iter().enumerate() {
            let hash = word.chars().fold(0u32, |acc, c| {
                acc.wrapping_mul(31).wrapping_add(c as u32)
            });
            let idx = (hash as usize) % embedding.len();
            embedding[idx] += (word.len() as f32) * 0.1;
        }
        
        let norm: f32 = embedding.iter().map(|x| x * x).sum::<f32>().sqrt();
        if norm > 0.0 {
            embedding.iter_mut().for_each(|x| *x /= norm);
        }
        
        embedding
    }

    pub fn cosine_similarity(a: &[f32], b: &[f32]) -> f32 {
        if a.len() != b.len() {
            return 0.0;
        }
        
        let dot_product: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
        let norm_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
        let norm_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();
        
        if norm_a > 0.0 && norm_b > 0.0 {
            dot_product / (norm_a * norm_b)
        } else {
            0.0
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_embedding_generation() {
        let embedding = EmbeddingGenerator::simple_embedding("hello world");
        assert_eq!(embedding.len(), 384);
    }

    #[test]
    fn test_cosine_similarity() {
        let a = vec![1.0, 0.0, 0.0];
        let b = vec![1.0, 0.0, 0.0];
        assert!((EmbeddingGenerator::cosine_similarity(&a, &b) - 1.0).abs() < 0.001);
    }
}
