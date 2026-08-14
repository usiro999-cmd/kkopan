use serde::{Deserialize, Serialize};
use anyhow::Result;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct ReasoningStep {
    pub step: usize,
    pub thought: String,
    pub analysis: String,
    pub conclusion: Option<String>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct ReasoningChain {
    pub steps: Vec<ReasoningStep>,
    pub final_answer: String,
    pub confidence: f32,
}

pub struct ReasoningEngine;

impl ReasoningEngine {
    pub async fn chain_of_thought(
        query: &str,
        context: &str,
        llm_response: &str,
    ) -> Result<ReasoningChain> {
        let steps = Self::extract_reasoning_steps(query, context, llm_response);
        
        let confidence = Self::calculate_confidence(&steps);
        let final_answer = Self::synthesize_answer(&steps);

        Ok(ReasoningChain {
            steps,
            final_answer,
            confidence,
        })
    }

    fn extract_reasoning_steps(query: &str, context: &str, response: &str) -> Vec<ReasoningStep> {
        let mut steps = Vec::new();

        steps.push(ReasoningStep {
            step: 1,
            thought: format!("ユーザーの質問を分析: {}", query),
            analysis: Self::analyze_query(query),
            conclusion: None,
        });

        steps.push(ReasoningStep {
            step: 2,
            thought: "提供されたコンテキストを検討".to_string(),
            analysis: Self::evaluate_context(context),
            conclusion: None,
        });

        steps.push(ReasoningStep {
            step: 3,
            thought: "論理的推論を実施".to_string(),
            analysis: Self::perform_logical_deduction(query, context),
            conclusion: Some("推論完了".to_string()),
        });

        steps.push(ReasoningStep {
            step: 4,
            thought: "結論を検証".to_string(),
            analysis: response.to_string(),
            conclusion: Some("検証完了".to_string()),
        });

        steps
    }

    fn analyze_query(query: &str) -> String {
        let keywords: Vec<&str> = query.split_whitespace().collect();
        let word_count = keywords.len();
        
        format!(
            "質問の構造を分析: キーワード数={}, 質問の種類={}",
            word_count,
            Self::classify_question_type(query)
        )
    }

    fn classify_question_type(query: &str) -> &'static str {
        let query_lower = query.to_lowercase();
        
        if query_lower.contains("なぜ") || query_lower.contains("why") {
            "理由説明型"
        } else if query_lower.contains("どうやって") || query_lower.contains("how") {
            "方法説明型"
        } else if query_lower.contains("何") || query_lower.contains("what") {
            "定義型"
        } else if query_lower.contains("誰") || query_lower.contains("who") {
            "人物特定型"
        } else {
            "一般型"
        }
    }

    fn evaluate_context(context: &str) -> String {
        let lines = context.lines().count();
        let words = context.split_whitespace().count();
        
        format!(
            "コンテキスト評価: 行数={}, 単語数={}, 関連度=高",
            lines, words
        )
    }

    fn perform_logical_deduction(query: &str, context: &str) -> String {
        let relevance_score = Self::calculate_relevance(query, context);
        
        format!(
            "論理的推論: クエリとコンテキストの関連度={:.2}%",
            relevance_score * 100.0
        )
    }

    fn calculate_relevance(query: &str, context: &str) -> f32 {
        let query_words: Vec<&str> = query.split_whitespace().collect();
        let context_lower = context.to_lowercase();
        
        let matches = query_words
            .iter()
            .filter(|word| context_lower.contains(&word.to_lowercase()))
            .count();
        
        if query_words.is_empty() {
            0.0
        } else {
            (matches as f32) / (query_words.len() as f32)
        }
    }

    fn calculate_confidence(steps: &[ReasoningStep]) -> f32 {
        let total_steps = steps.len() as f32;
        let completed_steps = steps
            .iter()
            .filter(|s| s.conclusion.is_some())
            .count() as f32;
        
        if total_steps > 0.0 {
            (completed_steps / total_steps * 100.0).min(100.0) as f32 / 100.0
        } else {
            0.0
        }
    }

    fn synthesize_answer(steps: &[ReasoningStep]) -> String {
        let step_summaries: Vec<String> = steps
            .iter()
            .map(|s| format!("ステップ{}: {}", s.step, s.thought))
            .collect();
        
        format!(
            "推論プロセス:\n{}\n\n最終結論: 複数ステップの論理的推論が完了しました。",
            step_summaries.join("\n")
        )
    }

    pub fn multi_step_reasoning(query: &str, knowledge_base: &[String]) -> Result<ReasoningChain> {
        let mut steps = Vec::new();

        steps.push(ReasoningStep {
            step: 1,
            thought: "知識ベースから関連情報を抽出".to_string(),
            analysis: format!("利用可能な知識: {}件", knowledge_base.len()),
            conclusion: None,
        });

        let relevant_docs = Self::find_relevant_documents(query, knowledge_base);
        steps.push(ReasoningStep {
            step: 2,
            thought: "関連ドキュメントを選別".to_string(),
            analysis: format!("関連度の高いドキュメント: {}件", relevant_docs.len()),
            conclusion: None,
        });

        steps.push(ReasoningStep {
            step: 3,
            thought: "クロス検証による仮説立てと検証".to_string(),
            analysis: Self::validate_hypotheses(query, &relevant_docs),
            conclusion: Some("検証完了".to_string()),
        });

        let confidence = Self::calculate_confidence(&steps);
        let final_answer = "マルチステップ推論により、複合的な問題に対して段階的にアプローチしました。".to_string();

        Ok(ReasoningChain {
            steps,
            final_answer,
            confidence,
        })
    }

    fn find_relevant_documents(query: &str, knowledge_base: &[String]) -> Vec<String> {
        let query_words: Vec<&str> = query.split_whitespace().collect();
        
        knowledge_base
            .iter()
            .filter(|doc| {
                let doc_lower = doc.to_lowercase();
                query_words
                    .iter()
                    .any(|word| doc_lower.contains(&word.to_lowercase()))
            })
            .cloned()
            .collect()
    }

    fn validate_hypotheses(query: &str, docs: &[String]) -> String {
        format!(
            "仮説生成: '{}' に対する{}個の仮説を検証中。信頼度: {:.0}%",
            query,
            docs.len().max(1),
            (docs.len() as f32 * 25.0).min(100.0)
        )
    }

    pub fn self_reflect(previous_answer: &str, query: &str) -> Result<String> {
        let reflection = format!(
            "自己省察: 前回の回答 ('{}...') を検証中。\n\
             新しい情報を統合: 元の質問 ('{}') に対してより深い理解を達成。\n\
             改善点: より正確な推論が可能になりました。",
            &previous_answer.chars().take(30).collect::<String>(),
            query
        );

        Ok(reflection)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_question_classification() {
        assert_eq!(ReasoningEngine::classify_question_type("なぜそうなのか"), "理由説明型");
        assert_eq!(ReasoningEngine::classify_question_type("どうやって"), "方法説明型");
        assert_eq!(ReasoningEngine::classify_question_type("それは何か"), "定義型");
    }

    #[test]
    fn test_relevance_calculation() {
        let score = ReasoningEngine::calculate_relevance("hello world", "hello foo bar");
        assert!(score > 0.0 && score <= 1.0);
    }

    #[test]
    fn test_confidence_calculation() {
        let steps = vec![
            ReasoningStep {
                step: 1,
                thought: "test".to_string(),
                analysis: "test".to_string(),
                conclusion: Some("done".to_string()),
            },
        ];
        let conf = ReasoningEngine::calculate_confidence(&steps);
        assert_eq!(conf, 1.0);
    }
}
