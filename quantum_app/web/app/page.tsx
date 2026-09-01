"use client";

import { useState } from "react";

type IconName =
  | "activity"
  | "alert"
  | "arrow"
  | "chevron"
  | "cloud"
  | "drone"
  | "farm"
  | "grid"
  | "layers"
  | "ocean"
  | "quantum"
  | "satellite"
  | "settings"
  | "users";

function Icon({ name, size = 20 }: { name: IconName; size?: number }) {
  const paths: Record<IconName, React.ReactNode> = {
    activity: <><path d="M3 12h4l2-7 4 14 2-7h6" /></>,
    alert: <><path d="M12 9v4" /><path d="M12 17h.01" /><path d="m10.3 3.5-8 14A2 2 0 0 0 4 20h16a2 2 0 0 0 1.7-2.5l-8-14a2 2 0 0 0-3.4 0Z" /></>,
    arrow: <><path d="M5 12h14" /><path d="m14 7 5 5-5 5" /></>,
    chevron: <><path d="m9 18 6-6-6-6" /></>,
    cloud: <><path d="M17.5 19H6a4 4 0 0 1-.4-8 6 6 0 0 1 11.6-1.6A4.8 4.8 0 0 1 17.5 19Z" /></>,
    drone: <><path d="M8 12h8" /><path d="M12 9v7" /><path d="M9 16h6l-1 3h-4Z" /><path d="M5 8h3l1 4H5a2 2 0 1 1 0-4Z" /><path d="M19 8h-3l-1 4h4a2 2 0 1 0 0-4Z" /><path d="M5 6V4m14 2V4" /></>,
    farm: <><path d="M3 20h18" /><path d="M5 20V9l7-5 7 5v11" /><path d="M9 20v-6h6v6" /><path d="M8 10h.01m8 0h.01" /></>,
    grid: <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></>,
    layers: <><path d="m12 2 9 5-9 5-9-5 9-5Z" /><path d="m3 12 9 5 9-5" /><path d="m3 17 9 5 9-5" /></>,
    ocean: <><path d="M3 15c2 0 2-1 4-1s2 1 4 1 2-1 4-1 2 1 4 1 2-1 2-1" /><path d="M3 20c2 0 2-1 4-1s2 1 4 1 2-1 4-1 2 1 4 1 2-1 2-1" /><path d="m7 11 5-8 5 8" /><path d="M12 3v8" /></>,
    quantum: <><ellipse cx="12" cy="12" rx="10" ry="4.5" /><ellipse cx="12" cy="12" rx="10" ry="4.5" transform="rotate(60 12 12)" /><ellipse cx="12" cy="12" rx="10" ry="4.5" transform="rotate(120 12 12)" /><circle cx="12" cy="12" r="1.2" fill="currentColor" /></>,
    satellite: <><path d="m13 7 4 4-6 6-4-4 6-6Z" /><path d="m16 4 4 4-3 3-4-4 3-3Zm-9 9 4 4-3 3-4-4 3-3Z" /><path d="m14 14 5 5M5 5l5 5" /></>,
    settings: <><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3A1.7 1.7 0 0 0 10 3V2.8h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z" /></>,
    users: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.9m-2-12a4 4 0 0 1 0 7.8" /></>,
  };

  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {paths[name]}
    </svg>
  );
}

const navItems: { label: string; icon: IconName }[] = [
  { label: "概要", icon: "grid" },
  { label: "衛星画像", icon: "satellite" },
  { label: "農地診断", icon: "farm" },
  { label: "災害検知", icon: "alert" },
  { label: "海洋監視", icon: "ocean" },
  { label: "ドローン", icon: "drone" },
  { label: "量子最適化", icon: "quantum" },
];

const features: { title: string; description: string; icon: IconName; tone: string; meta: string }[] = [
  { title: "衛星画像取得", description: "最新の地球観測データを取得・解析", icon: "satellite", tone: "blue", meta: "12 衛星 接続中" },
  { title: "AI農地診断", description: "生育状況・土壌・収穫予測をAIで可視化", icon: "farm", tone: "green", meta: "精度 94.8%" },
  { title: "災害検知", description: "洪水・土砂・火災をリアルタイム検知", icon: "alert", tone: "orange", meta: "24時間 監視中" },
  { title: "海洋監視", description: "海水温・漁場・赤潮リスクを一元管理", icon: "ocean", tone: "cyan", meta: "8 海域 解析中" },
  { title: "ドローン連携", description: "自動航行・撮影・散布を統合制御", icon: "drone", tone: "purple", meta: "5 機 オンライン" },
  { title: "量子最適化", description: "複雑な運用計画を量子技術で高速化", icon: "quantum", tone: "violet", meta: "QPU Ready" },
];

const audiences = [
  { label: "農家", value: "124", icon: "farm" as IconName },
  { label: "漁業者", value: "38", icon: "ocean" as IconName },
  { label: "自治体", value: "16", icon: "cloud" as IconName },
  { label: "企業", value: "27", icon: "users" as IconName },
];

const technologyStack: { category: string; name: string; detail: string; icon: IconName; tone: string }[] = [
  { category: "衛星データ", name: "Sentinel-2", detail: "無料・光学観測", icon: "satellite", tone: "blue" },
  { category: "ドローン", name: "DJI", detail: "撮影・自動航行", icon: "drone", tone: "purple" },
  { category: "AI", name: "Python + PyTorch", detail: "画像解析・予測", icon: "activity", tone: "green" },
  { category: "地図", name: "QGIS", detail: "地理空間解析", icon: "layers", tone: "cyan" },
  { category: "クラウド", name: "Microsoft Azure", detail: "データ・AI基盤", icon: "cloud", tone: "blue" },
];

const quantumUseCases = [
  "ドローンの飛行ルート最適化",
  "複数機の協調運用",
  "監視エリアの優先順位計算",
  "災害予測シミュレーション",
];

export default function Home() {
  const [activeNav, setActiveNav] = useState("概要");
  const [period, setPeriod] = useState("本日");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Icon name="satellite" size={23} /></div>
          <div><strong>SpaceAI</strong><span>KAWARAMACHI</span></div>
        </div>
        <nav aria-label="メインナビゲーション">
          <p className="nav-label">PLATFORM</p>
          {navItems.map((item) => (
            <button
              className={activeNav === item.label ? "nav-item active" : "nav-item"}
              key={item.label}
              onClick={() => setActiveNav(item.label)}
            >
              <Icon name={item.icon} size={19} />
              <span>{item.label}</span>
              {item.label === "災害検知" && <i>2</i>}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <button className="nav-item"><Icon name="settings" size={19} /><span>設定</span></button>
          <div className="system-state"><span /><div><strong>システム正常</strong><small>全サービス稼働中</small></div></div>
        </div>
      </aside>

      <main className="dashboard">
        <header className="topbar">
          <div>
            <p className="breadcrumb">SpaceAI / <span>{activeNav}</span></p>
            <h1>おはようございます、河原町さん</h1>
            <p className="subtitle">宇宙から、地域の未来を見守ります。</p>
          </div>
          <div className="top-actions">
            <div className="live-pill"><span /> LIVE</div>
            <button className="notification" aria-label="通知"><Icon name="alert" size={19} /><b>2</b></button>
            <button className="profile"><span>河</span><div><strong>河原町オフィス</strong><small>管理者</small></div><Icon name="chevron" size={14} /></button>
          </div>
        </header>

        <section className="hero-grid">
          <article className="earth-panel">
            <div className="orbit orbit-one" />
            <div className="orbit orbit-two" />
            <div className="earth">
              <div className="land land-one" />
              <div className="land land-two" />
              <div className="land land-three" />
              <div className="scan-line" />
              <span className="map-point point-one" />
              <span className="map-point point-two" />
              <span className="map-point point-three" />
            </div>
            <div className="satellite-float"><Icon name="satellite" size={34} /></div>
            <div className="panel-copy">
              <span className="eyebrow"><i /> EARTH INTELLIGENCE PLATFORM</span>
              <h2>地球を読み解く。<br /><em>未来を最適化する。</em></h2>
              <p>衛星・AI・ドローン・量子技術をひとつに。<br />地域の課題に、宇宙から答えを。</p>
              <button className="primary-button">ミッションを開始 <Icon name="arrow" size={17} /></button>
            </div>
            <div className="coordinate">35.0116° N&nbsp;&nbsp; 135.7681° E<br /><span>KYOTO · JAPAN</span></div>
          </article>

          <article className="monitor-card">
            <div className="card-heading">
              <div><span className="eyebrow">REALTIME MONITOR</span><h3>リアルタイム監視</h3></div>
              <button aria-label="詳細"><Icon name="chevron" size={18} /></button>
            </div>
            <div className="monitor-map">
              <div className="map-river" />
              <div className="field f1" /><div className="field f2" /><div className="field f3" /><div className="field f4" />
              <span className="pulse p1" /><span className="pulse p2" /><span className="pulse p3" />
              <div className="map-label"><i /> 河原町エリア</div>
            </div>
            <div className="monitor-stats">
              <div><span className="stat-icon green"><Icon name="farm" size={18} /></span><p>農地コンディション<strong>良好 <b>92%</b></strong></p></div>
              <div><span className="stat-icon blue"><Icon name="cloud" size={18} /></span><p>気象リスク<strong>低 <b>12%</b></strong></p></div>
              <div><span className="stat-icon cyan"><Icon name="activity" size={18} /></span><p>最終更新<strong>2分前</strong></p></div>
            </div>
          </article>
        </section>

        <section className="section-block">
          <div className="section-heading">
            <div><span className="eyebrow">CORE CAPABILITIES</span><h2>統合インテリジェンス</h2></div>
            <button className="text-button">すべての機能を見る <Icon name="arrow" size={16} /></button>
          </div>
          <div className="feature-grid">
            {features.map((feature) => (
              <button className="feature-card" key={feature.title}>
                <span className={`feature-icon ${feature.tone}`}><Icon name={feature.icon} size={25} /></span>
                <span className="feature-copy"><strong>{feature.title}</strong><small>{feature.description}</small><em><i /> {feature.meta}</em></span>
                <span className="feature-arrow"><Icon name="chevron" size={17} /></span>
              </button>
            ))}
          </div>
        </section>

        <section className="bottom-grid">
          <article className="usage-card">
            <div className="section-heading compact">
              <div><span className="eyebrow">ACTIVE USERS</span><h2>利用状況</h2></div>
              <select value={period} onChange={(event) => setPeriod(event.target.value)} aria-label="集計期間">
                <option>本日</option><option>今週</option><option>今月</option>
              </select>
            </div>
            <div className="audience-grid">
              {audiences.map((audience) => (
                <div key={audience.label}><span><Icon name={audience.icon} size={18} /></span><p>{audience.label}<strong>{audience.value}<small>ユーザー</small></strong></p></div>
              ))}
            </div>
          </article>
          <article className="quantum-banner">
            <div className="quantum-visual"><Icon name="quantum" size={74} /></div>
            <div><span className="eyebrow">CELESTIAL LINK · NEW</span><h2>銀河文明との通信を開始。</h2><p>量子翻訳と星間外交を体験するフィクション・シミュレーター。</p></div>
            <a href="/galactic">通信を開く <Icon name="arrow" size={16} /></a>
          </article>
        </section>

        <section className="architecture-section">
          <div className="section-heading">
            <div><span className="eyebrow">RECOMMENDED ARCHITECTURE</span><h2>推奨技術スタック</h2></div>
            <span className="starter-badge"><i /> STARTER READY</span>
          </div>
          <div className="stack-flow">
            {technologyStack.map((technology, index) => (
              <div className="stack-step" key={technology.category}>
                <span className={`feature-icon ${technology.tone}`}><Icon name={technology.icon} size={23} /></span>
                <div><small>{technology.category}</small><strong>{technology.name}</strong><em>{technology.detail}</em></div>
                {index < technologyStack.length - 1 && <span className="stack-connector"><Icon name="chevron" size={15} /></span>}
              </div>
            ))}
          </div>
        </section>

        <section className="quantum-roadmap">
          <div className="roadmap-intro">
            <span className="eyebrow">AI → QUANTUM AI</span>
            <h2>段階的に量子技術を導入</h2>
            <p>まず通常のAIでデータ収集・診断基盤を構築。運用データが蓄積した段階で、計算負荷の高い最適化領域に量子技術を適用します。</p>
          </div>
          <div className="roadmap-phases">
            <article className="roadmap-phase active">
              <span className="phase-number">01</span>
              <div><small>PHASE 1 · NOW</small><h3>通常AIで基盤構築</h3><p>Sentinel-2、DJI、PyTorch、QGISをAzure上で統合</p></div>
              <b>実装優先</b>
            </article>
            <div className="phase-line"><span /></div>
            <article className="roadmap-phase future">
              <span className="phase-number">02</span>
              <div><small>PHASE 2 · NEXT</small><h3>量子最適化を追加</h3>
                <ul>{quantumUseCases.map((useCase) => <li key={useCase}>{useCase}</li>)}</ul>
              </div>
              <b>QPU READY</b>
            </article>
          </div>
        </section>
      </main>
    </div>
  );
}
