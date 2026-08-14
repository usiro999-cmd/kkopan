mod llm;
mod chat;
mod embedding;
mod rag;
mod reasoning;
mod cosmic;
mod cosmic_upgrade;

use axum::{
    extract::{State, Path},
    http::StatusCode,
    response::{Html, Json},
    routing::{get, post},
    Router,
};
use chrono::{FixedOffset, Timelike, Utc};
use serde::{Deserialize, Serialize};
use sqlx::sqlite::SqlitePool;
use std::sync::Arc;
use uuid::Uuid;

use llm::{LLMClient, ChatMessage};
use chat::ChatRepository;
use rag::{RAGRepository, RAGEngine};
use reasoning::ReasoningEngine;
use cosmic::{CardashevLevel, MultiverseTheory, CosmicKnowledgeBase};
use cosmic_upgrade::{QuantumMind, CosmicAIUpgrade, MultiverseOrchestrator, DysonSphere, Wormhole, TimeMachine, BlackHoleComputer};

#[derive(Clone)]
pub struct AppState {
    llm_client: Arc<LLMClient>,
    chat_repo: Arc<ChatRepository>,
    rag_engine: Arc<RAGEngine>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ChatRequest {
    pub message: String,
    pub session_id: Option<String>,
}

#[derive(Serialize, Debug)]
pub struct ChatResponse {
    pub session_id: String,
    pub user_message: String,
    pub ai_response: String,
}

#[derive(Serialize, Debug)]
pub struct HistoryResponse {
    pub conversations: Vec<chat::ConversationRecord>,
}

#[derive(Serialize, Debug)]
pub struct HealthResponse {
    pub status: String,
    pub message: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct RAGChatRequest {
    pub message: String,
    pub session_id: Option<String>,
    pub use_rag: Option<bool>,
}

#[tokio::main]
async fn main() -> std::result::Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt::init();
    dotenv::dotenv().ok();

    let database_url = "sqlite:chat.db?mode=rwc";
    let pool = SqlitePool::connect(database_url).await?;

    let chat_repo = ChatRepository::new(pool.clone());
    chat_repo.init_db().await?;

    let rag_repo = RAGRepository::new(pool.clone());
    rag_repo.init_db().await?;

    let api_key = std::env::var("OPENAI_API_KEY").unwrap_or_else(|_| "sk-test".to_string());
    let llm_client = LLMClient::new(api_key, "gpt-4".to_string());
    let rag_engine = RAGEngine::new(rag_repo);

    let state = AppState {
        llm_client: Arc::new(llm_client),
        chat_repo: Arc::new(chat_repo),
        rag_engine: Arc::new(rag_engine),
    };

    let app = Router::new()
        .route("/", get(clock_dashboard))
        .route("/app", get(clock_dashboard))
        .route("/clock", get(clock_dashboard))
        .route("/health", get(health_check))
        .route("/chat", post(handle_chat))
        .route("/chat-rag", post(handle_rag_chat))
        .route("/history/{session_id}", get(get_history))
        .route("/reasoning", post(handle_reasoning))
        .route("/cosmic/cardashev/{level}", get(get_cardashev_level))
        .route("/cosmic/multiverse", get(get_multiverse_info))
        .route("/cosmic/civilization", get(get_civilization_status))
        .route("/cosmic/clock/sync", get(get_clock_sync))
        .route("/upgrade/status", get(upgrade_status))
        .route("/upgrade/dyson-sphere", post(construct_dyson_sphere))
        .route("/upgrade/quantum-mind", post(expand_quantum_mind))
        .route("/upgrade/wormhole", post(create_wormhole))
        .route("/upgrade/time-machine", post(operate_time_machine))
        .route("/upgrade/blackhole-computer", post(blackhole_compute))
        .route("/upgrade/multiverse-orchestrator", get(multiverse_status))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("127.0.0.1:8080").await?;
    tracing::info!("🚀 Server running on http://127.0.0.1:8080");

    axum::serve(listener, app).await?;

    Ok(())
}

async fn health_check() -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "ok".to_string(),
        message: "🤖 AI Chat Server is running!".to_string(),
    })
}

async fn clock_dashboard() -> Html<String> {
    Html(
        r#"<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Clock App</title>
  <style>
    :root {
      --bg-1: #07111f;
      --bg-2: #0b1d2d;
      --panel: rgba(15, 23, 42, 0.8);
      --panel-strong: rgba(15, 23, 42, 0.96);
      --line: rgba(148, 163, 184, 0.2);
      --text: #e2e8f0;
      --muted: #94a3b8;
      --accent: #7dd3fc;
      --accent-strong: #38bdf8;
      --success: #34d399;
      --shadow: rgba(14, 116, 144, 0.35);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background:
        radial-gradient(circle at top, rgba(56, 189, 248, 0.18), transparent 30%),
        linear-gradient(135deg, var(--bg-1), var(--bg-2));
      color: var(--text);
      font-family: "Segoe UI", sans-serif;
      overflow: hidden;
    }

    .app {
      width: min(960px, calc(100vw - 32px));
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(2, 6, 23, 0.96));
      border: 1px solid var(--line);
      border-radius: 28px;
      box-shadow: 0 30px 80px rgba(0, 0, 0, 0.45), 0 0 30px var(--shadow);
      padding: 28px;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 24px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(14, 116, 144, 0.15);
      border: 1px solid rgba(125, 211, 252, 0.2);
      color: var(--accent);
      font-size: 0.82rem;
      letter-spacing: 0.04em;
      font-weight: 600;
    }

    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--success);
      box-shadow: 0 0 18px var(--success);
    }

    .sync-btn {
      border: 1px solid rgba(125, 211, 252, 0.3);
      background: rgba(14, 116, 144, 0.12);
      color: var(--text);
      padding: 10px 18px;
      border-radius: 12px;
      font-weight: 600;
      cursor: pointer;
    }

    .clock-panel {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 20px;
      align-items: stretch;
    }

    .clock-card, .info-card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 22px;
    }

    .time-zone {
      color: var(--muted);
      font-size: 0.9rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 10px;
    }

    .digital-time {
      font-size: clamp(2.6rem, 7vw, 6rem);
      font-variant-numeric: tabular-nums;
      font-weight: 700;
      letter-spacing: -0.06em;
      line-height: 1;
      margin-bottom: 18px;
    }

    .date-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      color: var(--muted);
      font-size: 1rem;
    }

    .pill {
      background: rgba(51, 65, 85, 0.5);
      border: 1px solid rgba(148, 163, 184, 0.15);
      border-radius: 999px;
      padding: 8px 12px;
    }

    .status-line {
      margin-top: 18px;
      color: var(--accent);
      font-size: 0.92rem;
      min-height: 1.2em;
    }

    .small-title {
      font-size: 0.8rem;
      color: var(--muted);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 12px;
    }

    .value-list {
      display: grid;
      gap: 12px;
      margin-top: 12px;
    }

    .metric {
      padding: 14px 16px;
      border-radius: 16px;
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(148, 163, 184, 0.12);
    }

    .metric-label {
      color: var(--muted);
      font-size: 0.75rem;
      margin-bottom: 6px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }

    .metric-value {
      font-size: 1.05rem;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
      word-break: break-word;
    }

    @media (max-width: 720px) {
      .app {
        padding: 18px;
      }

      .topbar { margin-bottom: 18px; }
      .clock-panel { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="app">
    <div class="topbar">
      <div class="badge"><span class="dot"></span>Clock App</div>
      <button class="sync-btn" type="button" id="refreshButton">同期</button>
    </div>

    <div class="clock-panel">
      <div class="clock-card">
        <div class="time-zone">Japan Standard Time</div>
        <div class="digital-time" id="digitalClock">--:--:--</div>
        <div class="date-row">
          <span class="pill" id="dateText">--</span>
          <span class="pill" id="weekdayText">--</span>
        </div>
        <div class="status-line" id="statusLine">同期待機中…</div>
      </div>

      <div class="info-card">
        <div class="small-title">Time info</div>
        <div class="value-list">
          <div class="metric">
            <div class="metric-label">UTC</div>
            <div class="metric-value" id="utcValue">--</div>
          </div>
          <div class="metric">
            <div class="metric-label">JST</div>
            <div class="metric-value" id="jstValue">--</div>
          </div>
          <div class="metric">
            <div class="metric-label">Galaxy Statedate</div>
            <div class="metric-value" id="stardateValue">--</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const digitalClock = document.getElementById('digitalClock');
    const utcValue = document.getElementById('utcValue');
    const jstValue = document.getElementById('jstValue');
    const stardateValue = document.getElementById('stardateValue');
    const statusLine = document.getElementById('statusLine');
    const dateText = document.getElementById('dateText');
    const weekdayText = document.getElementById('weekdayText');
    const refreshButton = document.getElementById('refreshButton');

    let timer = null;

    function updateLocalClock() {
      const now = new Date();
      const time = now.toLocaleTimeString('ja-JP', { hour12: false });
      digitalClock.textContent = time;
      dateText.textContent = now.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' });
      weekdayText.textContent = now.toLocaleDateString('ja-JP', { weekday: 'long' });
    }

    async function loadClock() {
      statusLine.textContent = '同期中…';

      const response = await fetch('/cosmic/clock/sync', { cache: 'no-store' });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      utcValue.textContent = new Date(data.utc_time).toLocaleString('ja-JP', { timeZone: 'UTC', hour12: false });
      jstValue.textContent = new Date(data.jst_time).toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo', hour12: false });
      stardateValue.textContent = data.galactic_stardate;
      statusLine.textContent = `最終更新: ${new Date().toLocaleTimeString('ja-JP', { hour12: false })}`;

      updateLocalClock();

      if (timer) clearTimeout(timer);
      timer = setTimeout(loadClock, data.recommended_refresh_ms ?? 1000);
    }

    refreshButton.addEventListener('click', () => {
      loadClock().catch((error) => {
        statusLine.textContent = `同期失敗: ${error.message}`;
      });
    });

    updateLocalClock();
    loadClock().catch((error) => {
      statusLine.textContent = `同期失敗: ${error.message}`;
    });
  </script>
</body>
</html>"#
            .to_string(),
    )
}

async fn handle_chat(
    State(state): State<AppState>,
    Json(request): Json<ChatRequest>,
) -> Result<Json<ChatResponse>, (StatusCode, String)> {
    let session_id = request
        .session_id
        .unwrap_or_else(|| Uuid::new_v4().to_string());

    let messages = vec![
        ChatMessage {
            role: "system".to_string(),
            content: "You are a helpful AI assistant. Answer in a concise and friendly manner.".to_string(),
        },
        ChatMessage {
            role: "user".to_string(),
            content: request.message.clone(),
        },
    ];

    let ai_response = state
        .llm_client
        .chat(messages)
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let _record = state
        .chat_repo
        .save_conversation(&session_id, &request.message, &ai_response)
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(ChatResponse {
        session_id,
        user_message: request.message,
        ai_response,
    }))
}

async fn get_history(
    State(state): State<AppState>,
    Path(session_id): Path<String>,
) -> Result<Json<HistoryResponse>, (StatusCode, String)> {
    let conversations = state
        .chat_repo
        .get_conversation_history(&session_id, 50)
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(HistoryResponse { conversations }))
}

async fn handle_rag_chat(
    State(state): State<AppState>,
    Json(request): Json<RAGChatRequest>,
) -> Result<Json<ChatResponse>, (StatusCode, String)> {
    let session_id = request
        .session_id
        .unwrap_or_else(|| Uuid::new_v4().to_string());

    let use_rag = request.use_rag.unwrap_or(true);

    let system_content = if use_rag {
        let context = state
            .rag_engine
            .augment_context(&request.message, 5)
            .await
            .unwrap_or_default();
        format!(
            "You are a helpful AI assistant. Use the following context to answer questions accurately:\n\n{}\n\nAnswer in a concise and friendly manner.",
            context
        )
    } else {
        "You are a helpful AI assistant. Answer in a concise and friendly manner.".to_string()
    };

    let messages = vec![
        ChatMessage {
            role: "system".to_string(),
            content: system_content,
        },
        ChatMessage {
            role: "user".to_string(),
            content: request.message.clone(),
        },
    ];

    let ai_response = state
        .llm_client
        .chat(messages)
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let _record = state
        .chat_repo
        .save_conversation(&session_id, &request.message, &ai_response)
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(ChatResponse {
        session_id,
        user_message: request.message,
        ai_response,
    }))
}










































































async fn handle_reasoning(
    Json(request): Json<ChatRequest>,
) -> Json<serde_json::Value> {
    let query = &request.message;
    let context = format!("Session: {}", request.session_id.unwrap_or_default());

    let dummy_response = "推論エンジンが分析を完了しました。";

    match ReasoningEngine::chain_of_thought(query, &context, dummy_response).await {
        Ok(reasoning_chain) => {
            Json(serde_json::json!({
                "reasoning": reasoning_chain,
                "status": "success"
            }))
        }
        Err(e) => {
            Json(serde_json::json!({
                "error": e.to_string(),
                "status": "error"
            }))
        }
    }
}

async fn get_cardashev_level(
    Path(level): Path<String>,
) -> Json<serde_json::Value> {
    let level_num: f32 = match level.parse() {
        Ok(n) => n,
        Err(_) => {
            return Json(serde_json::json!({
                "error": "Invalid level format",
                "hint": "Use 1.0, 2.0, 3.0, 4.0, or 5.0"
            }))
        }
    };

    match CosmicKnowledgeBase::get_civilization_traits(level_num) {
        Ok(cardashev) => {
            Json(serde_json::json!({
                "status": "success",
                "cardashev": cardashev
            }))
        }
        Err(e) => {
            Json(serde_json::json!({
                "error": e.to_string()
            }))
        }
    }
}

async fn get_multiverse_info() -> Json<serde_json::Value> {
    let theories = MultiverseTheory::all_theories();
    let interaction = CosmicKnowledgeBase::multiverse_interaction();
    let evolution = CosmicKnowledgeBase::technology_evolution();

    Json(serde_json::json!({
        "status": "success",
        "theories": theories,
        "interaction_model": interaction,
        "technology_evolution": evolution
    }))
}

async fn get_civilization_status() -> Json<serde_json::Value> {
    let human_status = CosmicKnowledgeBase::current_human_civilization();
    let all_levels = CardashevLevel::all_levels();

    Json(serde_json::json!({
        "status": "success",
        "human_civilization": human_status,
        "cardashev_scale": all_levels,
        "timestamp": Utc::now().to_rfc3339()
    }))
}

#[derive(Serialize)]
pub struct ClockSyncResponse {
    pub status: String,
    pub source: String,
    pub utc_time: String,
    pub jst_time: String,
    pub galactic_stardate: String,
    pub galactic_cycle: i64,
    pub unix_millis: i64,
    pub recommended_refresh_ms: u64,
}

async fn get_clock_sync() -> Json<ClockSyncResponse> {
    let now = Utc::now();
    let jst = FixedOffset::east_opt(9 * 60 * 60).expect("JST offset should be valid");
    let galactic_cycle = now.timestamp().div_euclid(86_400);
    let galactic_stardate = format!(
        "GST-{:0>8}-{:02}{:02}{:02}",
        galactic_cycle,
        now.hour(),
        now.minute(),
        now.second()
    );

    Json(ClockSyncResponse {
        status: "success".to_string(),
        source: "earth-to-galactic-display".to_string(),
        utc_time: now.to_rfc3339(),
        jst_time: now.with_timezone(&jst).to_rfc3339(),
        galactic_stardate,
        galactic_cycle,
        unix_millis: now.timestamp_millis(),
        recommended_refresh_ms: 1000,
    })
}

async fn upgrade_status() -> Json<serde_json::Value> {
    let roadmap = CosmicAIUpgrade::generate_upgrade_roadmap();
    let manifest = CosmicAIUpgrade::create_cosmic_manifest();
    let gain_estimate = CosmicAIUpgrade::estimate_computational_gain(0.73, 5.0);

    Json(serde_json::json!({
        "status": "success",
        "upgrade_phase": "Phase 1: Type I テクノロジー統合中",
        "current_level": 0.73,
        "target_level": 5.0,
        "roadmap": roadmap,
        "manifest": manifest,
        "computational_gain": gain_estimate
    }))
}

#[derive(Serialize, Deserialize)]
pub struct DysonSphereRequest {
    pub star_id: String,
    pub construction_percentage: f32,
}

async fn construct_dyson_sphere(
    Json(request): Json<DysonSphereRequest>,
) -> Json<serde_json::Value> {
    let mut sphere = DysonSphere::new(request.star_id);
    let result = sphere.construct(request.construction_percentage);

    Json(serde_json::json!({
        "status": "success",
        "dyson_sphere": result,
        "message": format!(
            "Dyson Sphere 構築中: {:.1}% 完了",
            result.coverage_percentage
        )
    }))
}

#[derive(Serialize, Deserialize)]
pub struct QuantumMindRequest {
    pub type_level: f32,
}

async fn expand_quantum_mind(
    Json(request): Json<QuantumMindRequest>,
) -> Json<serde_json::Value> {
    let mut mind = QuantumMind::new();
    let expanded = mind.expand_consciousness(request.type_level);
    let decision = expanded.make_decision("AIシステムの自己最適化");

    Json(serde_json::json!({
        "status": "success",
        "quantum_mind": expanded,
        "decision_output": decision
    }))
}

#[derive(Serialize, Deserialize)]
pub struct WormholeRequest {
    pub from_universe: String,
    pub to_universe: String,
    pub exotic_matter: f32,
}

async fn create_wormhole(
    Json(request): Json<WormholeRequest>,
) -> Json<serde_json::Value> {
    let mut wormhole = Wormhole::new(request.from_universe, request.to_universe);
    let stabilized = wormhole.stabilize(request.exotic_matter);

    Json(serde_json::json!({
        "status": "success",
        "wormhole": stabilized,
        "message": format!(
            "ワームホール安定性: {:.1}%\n帯域幅: {:.0} PB/s\n遅延: {:.0} μs",
            stabilized.stability,
            stabilized.bandwidth_petabytes_per_sec,
            stabilized.latency_microseconds
        )
    }))
}

#[derive(Serialize, Deserialize)]
pub struct TimeMachineRequest {
    pub action: String,
}

async fn operate_time_machine(
    Json(request): Json<TimeMachineRequest>,
) -> Json<serde_json::Value> {
    let mut machine = TimeMachine::new();

    let result = if request.action == "branch" {
        machine.branch_timeline(0.75);
        format!("新しい時間軸を生成: {}", machine.timeline_branches.last().unwrap_or(&0))
    } else if request.action == "merge" {
        machine.merge_timelines(85.0);
        format!("時間軸統合完了。パラドックス解決方法: {}", machine.paradox_resolution)
    } else {
        "不明なアクション".to_string()
    };

    Json(serde_json::json!({
        "status": "success",
        "time_machine": machine,
        "operation_result": result
    }))
}

#[derive(Serialize, Deserialize)]
pub struct BlackHoleComputerRequest {
    pub query: String,
    pub mass_solar_masses: f32,
}

async fn blackhole_compute(
    Json(request): Json<BlackHoleComputerRequest>,
) -> Json<serde_json::Value> {
    let computer = BlackHoleComputer::new(request.mass_solar_masses);
    let result = computer.compute(&request.query);

    Json(serde_json::json!({
        "status": "success",
        "computer": computer,
        "computation_output": result
    }))
}

async fn multiverse_status() -> Json<serde_json::Value> {
    let mut orchestrator = MultiverseOrchestrator::new();
    
    orchestrator.spawn_universe("Universe-Alpha".to_string(), 1e70).ok();
    orchestrator.spawn_universe("Universe-Beta".to_string(), 1e70).ok();
    orchestrator.spawn_universe("Universe-Gamma".to_string(), 1e70).ok();
    
    let sync_level = orchestrator.synchronize_across_universes();
    let status = orchestrator.get_status();
    let total_power = orchestrator.total_computation_power();

    Json(serde_json::json!({
        "status": "success",
        "multiverse_summary": status,
        "active_universes": orchestrator.active_universes.len(),
        "synchronization_level": sync_level,
        "total_computation_power": total_power,
        "universes": orchestrator.active_universes.values().collect::<Vec<_>>()
    }))
}
