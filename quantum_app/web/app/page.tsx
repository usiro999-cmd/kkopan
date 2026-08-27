"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const targets = ["D2", "5-HT2A", "NMDA", "M1"] as const;
type Target = (typeof targets)[number];
type Profile = Record<Target, number>;

type Candidate = {
  id: string;
  rank: number;
  score: number;
  quantum_fidelity: number;
  descriptors: {
    molecular_weight: number;
    log_p: number;
    h_bond_donors: number;
    polar_surface_area: number;
  };
  explanation: Record<string, number>;
};

type Screening = {
  id: number;
  alpha: { candidates: Candidate[] };
  beta: { candidates: Candidate[] };
  comparison: { spearman_rho: number; same_leader: boolean };
  disclaimer: string;
};

type QuantumTarget = {
  name: string;
  description?: string;
};

type QuantumJob = {
  id: number;
  azure_job_id: string;
  target: string;
  circuit: string;
  shots: number;
  status: string;
  counts?: Record<string, number>;
};

const initialAlpha: Profile = { D2: 0.65, "5-HT2A": 0.75, NMDA: 0.6, M1: 0.55 };
const initialBeta: Profile = { D2: 0.45, "5-HT2A": 0.6, NMDA: 0.8, M1: 0.7 };

function ProfileEditor({
  label,
  profile,
  safety,
  onProfile,
  onSafety,
}: {
  label: string;
  profile: Profile;
  safety: number;
  onProfile: (profile: Profile) => void;
  onSafety: (value: number) => void;
}) {
  return (
    <article className="card profile">
      <span className="tag">{label}</span>
      <h2>Target Profile {label}</h2>
      {targets.map((target) => (
        <label key={target}>
          <span>{target}</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={profile[target]}
            onChange={(event) =>
              onProfile({ ...profile, [target]: Number(event.target.value) })
            }
          />
          <output>{profile[target].toFixed(2)}</output>
        </label>
      ))}
      <label>
        <span>Safety weight</span>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={safety}
          onChange={(event) => onSafety(Number(event.target.value))}
        />
        <output>{safety.toFixed(2)}</output>
      </label>
    </article>
  );
}

function Ranking({ label, candidates }: { label: string; candidates: Candidate[] }) {
  return (
    <article className="card">
      <span className="tag">{label}</span>
      <h2>{label} Ranking</h2>
      {candidates.map((candidate) => (
        <details className="candidate" key={candidate.id}>
          <summary>
            <strong>#{candidate.rank} {candidate.id}</strong>
            <div className="track"><i style={{ width: `${candidate.score * 100}%` }} /></div>
            <span>{(candidate.score * 100).toFixed(1)}%</span>
          </summary>
          <div className="descriptor-grid">
            <span>Fidelity <b>{candidate.quantum_fidelity.toFixed(3)}</b></span>
            <span>MolWt <b>{candidate.descriptors.molecular_weight}</b></span>
            <span>LogP <b>{candidate.descriptors.log_p}</b></span>
            <span>TPSA <b>{candidate.descriptors.polar_surface_area}</b></span>
          </div>
        </details>
      ))}
    </article>
  );
}

function Curriculum() {
  return (
    <section className="curriculum">
      <p className="eyebrow">GRADUATE CURRICULUM</p>
      <h2>量子化学情報学・実験計画・モデル批判</h2>
      <div className="theory-grid">
        <article className="card">
          <span className="tag">QISKIT</span>
          <h3>量子特徴写像</h3>
          <code>|ψ(x)⟩ = Ucx ∏ᵢ Ry(πxᵢ)|0⟩</code>
          <code>F(x,z) = |⟨ψ(x)|ψ(z)⟩|²</code>
          <p>Fidelityは状態空間の類似度であり、生物学的エビデンスではありません。</p>
        </article>
        <article className="card">
          <span className="tag">RDKIT</span>
          <h3>分子記述子</h3>
          <p>MolWt、LogP、水素結合供与体、TPSAを計算し、記述子の尺度と交絡を検討します。</p>
          <code>xmol = [MolWt, LogP, HBD, TPSA]</code>
        </article>
        <article className="card">
          <span className="tag">STATISTICS</span>
          <h3>順位安定性</h3>
          <code>ρ = 1 − 6Σdᵢ² / n(n²−1)</code>
          <p>目的関数を変えたツイン実験から、ランキングの感度を批判的に評価します。</p>
        </article>
      </div>
    </section>
  );
}

function QuantumCloud() {
  const [configured, setConfigured] = useState(false);
  const [targets, setTargets] = useState<QuantumTarget[]>([]);
  const [target, setTarget] = useState("");
  const [shots, setShots] = useState(100);
  const [job, setJob] = useState<QuantumJob | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadConnection() {
    setError("");
    setLoading(true);
    try {
      const statusResponse = await fetch(`${API_URL}/api/v1/quantum/status`);
      const status = await statusResponse.json();
      if (!statusResponse.ok) throw new Error(status.detail ?? "Status request failed");
      setConfigured(status.configured);
      if (!status.configured) return;
      const targetsResponse = await fetch(`${API_URL}/api/v1/quantum/targets`);
      const targetData = await targetsResponse.json();
      if (!targetsResponse.ok) throw new Error(targetData.detail ?? "Target discovery failed");
      setTargets(targetData);
      const selected = status.default_target && targetData.some(
        (item: QuantumTarget) => item.name === status.default_target,
      ) ? status.default_target : targetData[0]?.name ?? "";
      setTarget(selected);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Azure Quantum connection failed");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadConnection();
  }, []);

  async function submitJob() {
    setError("");
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/quantum/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target, circuit: "bell", shots }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Job submission failed");
      setJob(data);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Job submission failed");
    } finally {
      setLoading(false);
    }
  }

  async function refreshJob() {
    if (!job) return;
    setError("");
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/quantum/jobs/${job.id}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Job retrieval failed");
      setJob(data);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Job retrieval failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card quantum-cloud">
      <div className="cloud-heading">
        <div>
          <span className="tag">AZURE QUANTUM · QDK</span>
          <h2>実量子コンピューターAPI</h2>
          <p>QiskitでBell回路を生成し、選択したAzure Quantumターゲットへ送信します。</p>
        </div>
        <strong className={configured ? "connected" : "disconnected"}>
          {loading ? "確認中" : configured ? "設定済み" : "未設定"}
        </strong>
      </div>
      {configured ? (
        <div className="cloud-controls">
          <label>
            <span>Quantum target</span>
            <select value={target} onChange={(event) => setTarget(event.target.value)}>
              {targets.map((item) => <option key={item.name}>{item.name}</option>)}
            </select>
          </label>
          <label>
            <span>Shots</span>
            <input
              type="number"
              min="1"
              max="10000"
              value={shots}
              onChange={(event) => setShots(Number(event.target.value))}
            />
          </label>
          <button onClick={submitJob} disabled={loading || !target}>
            Bell回路を送信
          </button>
        </div>
      ) : (
        <p className="setup-note">
          `.env` にAZURE_QUANTUM_RESOURCE_IDとAzure Identity認証情報を設定し、
          APIコンテナを再起動してください。
        </p>
      )}
      {job && (
        <div className="job-card">
          <div><span>Job</span><b>{job.azure_job_id}</b></div>
          <div><span>Target</span><b>{job.target}</b></div>
          <div><span>Status</span><b>{job.status}</b></div>
          <button onClick={refreshJob} disabled={loading}>状態を更新</button>
          {job.counts && (
            <div className="counts">
              {Object.entries(job.counts).map(([state, count]) => (
                <span key={state}>|{state}⟩ <b>{count}</b></span>
              ))}
            </div>
          )}
        </div>
      )}
      {error && <p className="error">{error}</p>}
    </section>
  );
}

function Tutor({ screeningId }: { screeningId?: number }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function ask(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/tutor`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, screening_id: screeningId }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Tutor request failed");
      setAnswer(data.answer);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Tutor request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card tutor">
      <span className="tag">AZURE OPENAI</span>
      <h2>研究チューター</h2>
      <form onSubmit={ask}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="例: Fidelityと結合親和性を区別して説明してください"
          minLength={3}
          maxLength={2000}
          required
        />
        <button disabled={loading}>{loading ? "解析中…" : "質問する"}</button>
      </form>
      {answer && <p className="answer">{answer}</p>}
      {error && <p className="error">{error}</p>}
    </section>
  );
}

export default function Home() {
  const [alpha, setAlpha] = useState(initialAlpha);
  const [beta, setBeta] = useState(initialBeta);
  const [alphaSafety, setAlphaSafety] = useState(0.35);
  const [betaSafety, setBetaSafety] = useState(0.6);
  const [result, setResult] = useState<Screening | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function runScreening() {
    setError("");
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/screenings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: "Graduate twin experiment",
          alpha: { profile: alpha, safety_weight: alphaSafety },
          beta: { profile: beta, safety_weight: betaSafety },
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Screening failed");
      setResult(data);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Screening failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header>
        <p className="eyebrow">NEXT.JS · FASTAPI · POSTGRESQL · QISKIT · RDKIT</p>
        <h1>Multiverse Quantum AI Academy</h1>
        <p>大学院レベルの量子AI創薬ツイン実験環境</p>
      </header>
      <aside className="warning">
        教育専用です。候補IDと評価ラベルは合成であり、診断、治療、臨床、実際の創薬判断には使用できません。
      </aside>
      <Link className="fusion-link" href="/fusion">
        <span>NEW RESEARCH WORKSPACE</span>
        <strong>Fusion Research Copilot</strong>
        <i>核融合プラズマ解析とAI研究支援を開く →</i>
      </Link>
      <section className="twin-grid">
        <ProfileEditor label="Alpha" profile={alpha} safety={alphaSafety} onProfile={setAlpha} onSafety={setAlphaSafety} />
        <ProfileEditor label="Beta" profile={beta} safety={betaSafety} onProfile={setBeta} onSafety={setBetaSafety} />
      </section>
      <button className="run" onClick={runScreening} disabled={loading}>
        {loading ? "RDKit + Qiskit解析中…" : "ツイン・スクリーニング実行"}
      </button>
      {error && <p className="error">{error}</p>}
      {result && (
        <>
          <section className="metrics card">
            <div><strong>{result.comparison.spearman_rho.toFixed(2)}</strong><span>Spearman ρ</span></div>
            <div><strong>{result.comparison.same_leader ? "一致" : "不一致"}</strong><span>首位候補</span></div>
            <div><strong>#{result.id}</strong><span>PostgreSQL Run</span></div>
          </section>
          <section className="twin-grid">
            <Ranking label="Alpha" candidates={result.alpha.candidates} />
            <Ranking label="Beta" candidates={result.beta.candidates} />
          </section>
          <p className="disclaimer">{result.disclaimer}</p>
        </>
      )}
      <Curriculum />
      <QuantumCloud />
      <Tutor screeningId={result?.id} />
    </main>
  );
}
