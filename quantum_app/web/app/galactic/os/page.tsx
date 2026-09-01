"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import styles from "./os.module.css";

type LayerId = "stellar" | "network" | "civilization" | "science" | "defense";

const layers: { id: LayerId; number: string; glyph: string; name: string; english: string; color: string }[] = [
  { id: "stellar", number: "01", glyph: "☼", name: "恒星管理層", english: "STELLAR MANAGEMENT", color: "#ffd36c" },
  { id: "network", number: "02", glyph: "⌘", name: "銀河ネットワーク", english: "GALACTIC NETWORK", color: "#65dcff" },
  { id: "civilization", number: "03", glyph: "◈", name: "文明管理AI", english: "CIVILIZATION AI", color: "#72f3bd" },
  { id: "science", number: "04", glyph: "⌬", name: "科学研究エンジン", english: "SCIENCE ENGINE", color: "#af8fff" },
  { id: "defense", number: "05", glyph: "△", name: "防衛・安全機構", english: "DEFENSE & SAFETY", color: "#ff917c" },
];

const layerContent: Record<LayerId, {
  heading: string;
  description: string;
  stats: { label: string; value: string; unit?: string }[];
  systems: { name: string; detail: string; status: string }[];
}> = {
  stellar: {
    heading: "銀河の恒星エネルギーを統合監視",
    description: "4,012億個の恒星と架空のダイソン構造物をデジタルツイン上で監視します。",
    stats: [{ label: "監視恒星", value: "401.2", unit: "B" }, { label: "エネルギー出力", value: "8.41", unit: "×10³⁶W" }, { label: "異常予兆", value: "24" }],
    systems: [
      { name: "恒星スペクトル監視", detail: "光度・磁場・フレア活動を分散AIで解析", status: "正常" },
      { name: "ダイソン設備制御", detail: "集光衛星群の軌道と発電効率を最適化", status: "99.4%" },
      { name: "超新星早期警戒", detail: "重力波・ニュートリノ変動から爆発を予測", status: "監視中" },
    ],
  },
  network: {
    heading: "光速遅延を前提にした分散ネットワーク",
    description: "星系ごとに自律判断するエッジAIと、仮想ワームホール中継網を統合します。",
    stats: [{ label: "接続星系", value: "8.4", unit: "B" }, { label: "データ複製", value: "99.999", unit: "%" }, { label: "稼働リレー", value: "42.8", unit: "M" }],
    systems: [
      { name: "遅延耐性AI", detail: "到達時間の異なる情報を因果整合性付きで同期", status: "同期済み" },
      { name: "ワームホール通信網", detail: "創作上の中継経路を安全にシミュレーション", status: "安定" },
      { name: "惑星間クラウド", detail: "多重化されたデータを文明圏ごとに分散保存", status: "12.8 YB" },
    ],
  },
  civilization: {
    heading: "すべての生命圏を支援する文明管理AI",
    description: "人口・資源・経済のデジタルツインを使い、公平性を重視した政策案を提示します。",
    stats: [{ label: "支援市民", value: "18.2", unit: "Q" }, { label: "資源効率", value: "96.8", unit: "%" }, { label: "経済圏", value: "2,408" }],
    systems: [
      { name: "市民支援AI", detail: "医療・教育・移動・行政サービスを地域AIが支援", status: "稼働中" },
      { name: "資源配分最適化", detail: "生命維持資源を安全制約下で公平に配分", status: "均衡" },
      { name: "銀河経済モデル", detail: "星間貿易と供給網の長期シナリオを予測", status: "+2.4%" },
    ],
  },
  science: {
    heading: "銀河全体を仮想宇宙として再現",
    description: "観測データと理論モデルを比較し、新しい仮説を探索する研究環境です。",
    stats: [{ label: "シミュレーション", value: "6.8", unit: "M" }, { label: "研究AI", value: "42,081" }, { label: "候補理論", value: "1,284" }],
    systems: [
      { name: "銀河デジタルツイン", detail: "星形成・重力・物質循環を多階層で計算", status: "実行中" },
      { name: "新物理探索", detail: "観測と標準模型の差から検証可能な仮説を生成", status: "128候補" },
      { name: "宇宙論検証", detail: "暗黒物質・膨張史の複数モデルを比較", status: "解析中" },
    ],
  },
  defense: {
    heading: "生命圏を守る予測・回避・接触管理",
    description: "軍事制御ではなく、防災・天体衝突回避・外交安全に限定した意思決定支援です。",
    stats: [{ label: "追跡天体", value: "94.1", unit: "B" }, { label: "保護生命圏", value: "2,408" }, { label: "警戒イベント", value: "3" }],
    systems: [
      { name: "小惑星衝突回避", detail: "軌道予測と非破壊的偏向ミッションを計画", status: "安全" },
      { name: "ブラックホール監視", detail: "降着活動・潮汐変動・ジェット方向を観測", status: "監視中" },
      { name: "異文明接触管理", detail: "同盟憲章に基づき非敵対的接触を支援", status: "平和指数 94.7%" },
    ],
  },
};

const events = [
  { time: "21:08", level: "warning", title: "ペルセウス腕で重力波異常", detail: "科学研究エンジンへ解析ジョブを転送" },
  { time: "20:51", level: "safe", title: "ダイソン群 V-442 同期完了", detail: "発電効率が0.8%改善" },
  { time: "20:32", level: "info", title: "アンドロメダ中継点を再同期", detail: "データ整合性 99.999%" },
];

export default function GalacticOS() {
  const [activeLayer, setActiveLayer] = useState<LayerId>("stellar");
  const [simulation, setSimulation] = useState(false);
  const [progress, setProgress] = useState(0);
  const content = layerContent[activeLayer];

  useEffect(() => {
    if (!simulation) return;
    const timer = window.setInterval(() => {
      setProgress((value) => {
        if (value >= 100) {
          window.clearInterval(timer);
          setSimulation(false);
          return 100;
        }
        return value + 2;
      });
    }, 90);
    return () => window.clearInterval(timer);
  }, [simulation]);

  function runSimulation() {
    setProgress(0);
    setSimulation(true);
  }

  return (
    <main className={styles.shell}>
      <div className={styles.space} />
      <header className={styles.topbar}>
        <Link href="/galactic" className={styles.brand}>
          <span className={styles.logo}>G</span>
          <div><strong>GalacticOS</strong><small>GALACTIC OPERATING SYSTEM · v3.0</small></div>
        </Link>
        <nav>
          <Link href="/galactic">通信</Link>
          <Link href="/galactic/alliance">同盟</Link>
          <Link href="/galactic/compute">演算</Link>
          <span>OS</span>
        </nav>
        <div className={styles.systemHealth}><i /> ALL SYSTEMS NOMINAL <b>99.9998%</b></div>
      </header>

      <section className={styles.layout}>
        <aside className={styles.layers}>
          <div className={styles.navTitle}><span>SYSTEM ARCHITECTURE</span><strong>銀河運用レイヤー</strong></div>
          {layers.map((layer) => (
            <button
              key={layer.id}
              className={activeLayer === layer.id ? styles.layerActive : styles.layer}
              onClick={() => setActiveLayer(layer.id)}
              style={{ "--layer": layer.color } as React.CSSProperties}
            >
              <span className={styles.layerNumber}>{layer.number}</span>
              <i>{layer.glyph}</i>
              <span><strong>{layer.name}</strong><small>{layer.english}</small></span>
              <b>›</b>
            </button>
          ))}
          <div className={styles.kernel}>
            <span>CORE KERNEL</span>
            <div className={styles.kernelOrb}><i /><b>G/OS</b></div>
            <strong>量子分散カーネル</strong>
            <small>8.4B星系で合意済み</small>
          </div>
          <Link href="/" className={styles.back}>← SpaceAIへ戻る</Link>
        </aside>

        <section className={styles.content}>
          <div className={styles.hero}>
            <div>
              <span>GALACTIC COMMAND CENTER · LAYER {layers.find((item) => item.id === activeLayer)?.number}</span>
              <h1>{content.heading}</h1>
              <p>{content.description}</p>
            </div>
            <button onClick={runSimulation} disabled={simulation}>
              <i>{simulation ? "◌" : "▶"}</i>
              <span><strong>{simulation ? "シミュレーション実行中" : "銀河シミュレーション実行"}</strong><small>SAFE DIGITAL TWIN MODE</small></span>
            </button>
          </div>

          <div className={styles.stats}>
            {content.stats.map((stat) => <article key={stat.label}><span>{stat.label}</span><strong>{stat.value}<small>{stat.unit}</small></strong><i><b /></i></article>)}
          </div>

          <div className={styles.galaxyPanel}>
            <div className={styles.galaxy}>
              <div className={styles.core} />
              <div className={`${styles.arm} ${styles.arm1}`} /><div className={`${styles.arm} ${styles.arm2}`} /><div className={`${styles.arm} ${styles.arm3}`} />
              <div className={styles.scan} />
              {Array.from({ length: 18 }, (_, index) => <i key={index} className={styles[`star${index + 1}`]} />)}
              <span className={styles.sol}><i /> SOL</span>
              <span className={styles.vega}><i /> VEGA</span>
              <span className={styles.center}><i /> SAGITTARIUS A*</span>
            </div>
            <div className={styles.mapOverlay}>
              <span>LIVE GALACTIC DIGITAL TWIN</span>
              <strong>401,247,082,194</strong>
              <small>TRACKED STELLAR OBJECTS</small>
            </div>
            {simulation && <div className={styles.simulationOverlay}><span>SIMULATION CYCLE 04</span><strong>{progress}%</strong><i><b style={{ width: `${progress}%` }} /></i></div>}
            {!simulation && progress === 100 && <div className={styles.complete}>✓ シミュレーション完了 · 異常なし</div>}
          </div>

          <div className={styles.systemGrid}>
            {content.systems.map((system, index) => (
              <article key={system.name}>
                <div className={styles.systemIcon}>{layers.find((item) => item.id === activeLayer)?.glyph}<i>{index + 1}</i></div>
                <div><span>SUBSYSTEM {String(index + 1).padStart(2, "0")}</span><h2>{system.name}</h2><p>{system.detail}</p></div>
                <strong><i /> {system.status}</strong>
              </article>
            ))}
          </div>
        </section>

        <aside className={styles.monitor}>
          <section className={styles.clock}>
            <span>GALACTIC STANDARD TIME</span><strong>7204.244.21</strong><small>ORIGIN · SOL RELAY</small>
          </section>
          <section className={styles.resources}>
            <header><span>CORE RESOURCES</span><h2>システム資源</h2></header>
            <div><span>演算容量</span><strong>84.2%</strong><i><b style={{ width: "84.2%" }} /></i></div>
            <div><span>量子メモリ</span><strong>71.8%</strong><i><b style={{ width: "71.8%" }} /></i></div>
            <div><span>ネットワーク</span><strong>96.4%</strong><i><b style={{ width: "96.4%" }} /></i></div>
            <div><span>エネルギー</span><strong>63.1%</strong><i><b style={{ width: "63.1%" }} /></i></div>
          </section>
          <section className={styles.events}>
            <header><span>LIVE EVENT STREAM</span><h2>銀河イベント</h2></header>
            {events.map((event) => <article key={event.time}><time>{event.time}</time><i className={styles[event.level]} /><div><strong>{event.title}</strong><p>{event.detail}</p></div></article>)}
          </section>
          <section className={styles.guardrail}>
            <span>◇</span><div><strong>HUMAN OVERSIGHT ACTIVE</strong><p>すべての重要判断には文明代表の承認が必要です。</p></div>
          </section>
        </aside>
      </section>
      <footer className={styles.footer}>FICTIONAL CIVILIZATION SIMULATION · GalacticOSは実在の恒星設備、ワームホール、防衛システムを制御しません。</footer>
    </main>
  );
}
