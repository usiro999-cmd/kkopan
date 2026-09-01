"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import styles from "./compute.module.css";

type NodeId = "ai" | "azure" | "quantum";
type JobStatus = "待機中" | "実行中" | "完了";

const nodes: { id: NodeId; name: string; type: string; capacity: string; color: string }[] = [
  { id: "ai", name: "AI Neural Cluster", type: "PyTorch · GPU", capacity: "48.2 PFLOPS", color: "#67f5c7" },
  { id: "azure", name: "Azure Orbital Cloud", type: "Distributed CPU", capacity: "12,480 Cores", color: "#5fb8ff" },
  { id: "quantum", name: "Quantum Optimizer", type: "Qiskit · QPU", capacity: "127 Qubits", color: "#ae8cff" },
];

const jobTypes = [
  { id: "earth", name: "地球観測AI解析", description: "衛星画像から農地・海洋・災害リスクを推論" },
  { id: "route", name: "ドローン群ルート最適化", description: "複数機の経路とバッテリー消費を同時最適化" },
  { id: "climate", name: "災害予測シミュレーション", description: "気象・地形データから地域リスクを並列計算" },
];

export default function GalacticComputeGrid() {
  const [selectedJob, setSelectedJob] = useState("route");
  const [allocations, setAllocations] = useState<Record<NodeId, number>>({ ai: 45, azure: 35, quantum: 20 });
  const [status, setStatus] = useState<JobStatus>("待機中");
  const [progress, setProgress] = useState(0);
  const [completedRuns, setCompletedRuns] = useState(12);

  const allocationTotal = Object.values(allocations).reduce((sum, value) => sum + value, 0);
  const selected = jobTypes.find((job) => job.id === selectedJob) ?? jobTypes[0];
  const estimatedPower = useMemo(
    () => (allocations.ai * 1.8 + allocations.azure * 1.1 + allocations.quantum * 0.35).toFixed(1),
    [allocations],
  );

  useEffect(() => {
    if (status !== "実行中") return;
    const timer = window.setInterval(() => {
      setProgress((current) => {
        const next = Math.min(current + 4, 100);
        if (next === 100) {
          window.clearInterval(timer);
          setStatus("完了");
          setCompletedRuns((count) => count + 1);
        }
        return next;
      });
    }, 160);
    return () => window.clearInterval(timer);
  }, [status]);

  function setAllocation(node: NodeId, value: number) {
    setAllocations((current) => ({ ...current, [node]: value }));
  }

  function startJob() {
    if (status === "実行中" || allocationTotal !== 100) return;
    setProgress(0);
    setStatus("実行中");
  }

  return (
    <main className={styles.shell}>
      <div className={styles.gridBackground} />
      <header className={styles.header}>
        <Link href="/galactic" className={styles.brand}>
          <span>⌬</span>
          <div><strong>GALACTIC COMPUTE GRID</strong><small>SPACEAI DISTRIBUTED INTELLIGENCE</small></div>
        </Link>
        <nav>
          <Link href="/galactic">外交通信</Link>
          <Link href="/galactic/alliance">同盟通信</Link>
          <span className={styles.active}>計算グリッド</span>
          <Link href="/galactic/os">OS</Link>
          <Link href="/">SpaceAI</Link>
        </nav>
        <div className={styles.live}><i /> GRID ONLINE</div>
      </header>

      <section className={styles.dashboard}>
        <div className={styles.title}>
          <div>
            <span>UNIFIED COMPUTE ORCHESTRATION</span>
            <h1>ソフトウェアで、<em>計算の力</em>を束ねる。</h1>
            <p>AI・Azureクラウド・量子最適化を、ひとつの演算グリッドとして統合します。</p>
          </div>
          <div className={styles.powerIndex}>
            <span>COMPUTE POWER INDEX</span>
            <strong>8.42<small> / 10</small></strong>
            <i><b /></i>
          </div>
        </div>

        <div className={styles.metrics}>
          <article><span>AGGREGATE PERFORMANCE</span><strong>61.8 <small>PFLOPS</small></strong><em>↑ 12.4% today</em></article>
          <article><span>ACTIVE NODES</span><strong>3 <small>/ 3</small></strong><em className={styles.green}>All systems nominal</em></article>
          <article><span>POWER DRAW</span><strong>{estimatedPower} <small>kW</small></strong><em>Software-estimated</em></article>
          <article><span>COMPLETED RUNS</span><strong>{completedRuns}</strong><em>Current session</em></article>
        </div>

        <div className={styles.mainGrid}>
          <section className={styles.networkPanel}>
            <header><div><span>COMPUTE TOPOLOGY</span><h2>分散ノード</h2></div><strong><i /> SYNCHRONIZED</strong></header>
            <div className={styles.topology}>
              <svg viewBox="0 0 800 330" aria-hidden="true">
                <path d="M400 165 C300 70 220 85 135 95" />
                <path d="M400 165 C520 60 630 70 690 100" />
                <path d="M400 165 C400 230 400 250 400 285" />
              </svg>
              <div className={styles.core}><span>⌬</span><strong>ORCHESTRATOR</strong><small>SpaceAI Core</small><i /></div>
              {nodes.map((node, index) => (
                <div className={`${styles.node} ${styles[`node${index + 1}`]}`} key={node.id} style={{ "--node-color": node.color } as React.CSSProperties}>
                  <div className={styles.nodeIcon}>{node.id === "ai" ? "AI" : node.id === "azure" ? "AZ" : "Q"}</div>
                  <span><strong>{node.name}</strong><small>{node.type}</small><em>{node.capacity}</em></span>
                  <i />
                </div>
              ))}
              <div className={styles.packetOne} /><div className={styles.packetTwo} /><div className={styles.packetThree} />
            </div>
          </section>

          <aside className={styles.allocationPanel}>
            <header><span>RESOURCE ALLOCATION</span><h2>演算リソース配分</h2></header>
            <div className={styles.allocationTotal}>
              <span>TOTAL ALLOCATION</span>
              <strong className={allocationTotal === 100 ? styles.valid : styles.invalid}>{allocationTotal}%</strong>
            </div>
            {nodes.map((node) => (
              <label className={styles.allocation} key={node.id}>
                <span><i style={{ background: node.color }} /><strong>{node.name}</strong><output>{allocations[node.id]}%</output></span>
                <input type="range" min="0" max="100" step="5" value={allocations[node.id]} onChange={(event) => setAllocation(node.id, Number(event.target.value))} />
              </label>
            ))}
            {allocationTotal !== 100 && <p className={styles.allocationError}>合計を100%に調整してください。</p>}
            <div className={styles.safety}>
              <span>◇</span><div><strong>安全なシミュレーション</strong><p>実クラウド資源や課金APIには接続していません。</p></div>
            </div>
          </aside>
        </div>

        <section className={styles.jobConsole}>
          <div className={styles.jobSelector}>
            <header><span>MISSION WORKLOAD</span><h2>計算ミッションを選択</h2></header>
            <div>
              {jobTypes.map((job) => (
                <button className={selectedJob === job.id ? styles.jobActive : styles.job} key={job.id} onClick={() => setSelectedJob(job.id)} disabled={status === "実行中"}>
                  <i>{job.id === "earth" ? "◉" : job.id === "route" ? "⌁" : "△"}</i>
                  <span><strong>{job.name}</strong><small>{job.description}</small></span>
                  <b>{selectedJob === job.id ? "SELECTED" : "READY"}</b>
                </button>
              ))}
            </div>
          </div>

          <div className={styles.execution}>
            <header><span>EXECUTION CONTROL</span><h2>ジョブ実行</h2></header>
            <div className={styles.executionSummary}>
              <span><small>MISSION</small><strong>{selected.name}</strong></span>
              <span><small>STATUS</small><strong className={status === "完了" ? styles.green : undefined}>{status}</strong></span>
              <span><small>EST. TIME</small><strong>00:04</strong></span>
            </div>
            <div className={styles.progress}>
              <i><b style={{ width: `${progress}%` }} /></i>
              <span>{progress}%</span>
            </div>
            <button className={styles.executeButton} onClick={startJob} disabled={status === "実行中" || allocationTotal !== 100}>
              <span>{status === "実行中" ? "演算グリッド実行中" : status === "完了" ? "もう一度実行" : "演算を開始"}</span>
              <b>➤</b>
            </button>
          </div>
        </section>

        <footer>
          <span>EARTH COMPUTE TREATY · RESOURCE SAFE MODE</span>
          <p>「銀河のパワー」は、実在するソフトウェアと計算資源を統合する比喩的な表現です。</p>
        </footer>
      </section>
    </main>
  );
}
