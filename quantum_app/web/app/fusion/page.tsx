"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import styles from "./fusion.module.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Scenario = {
  name: string;
  temperature_kev: number;
  density_1e20_m3: number;
  confinement_time_s: number;
  magnetic_field_t: number;
  major_radius_m: number;
  minor_radius_m: number;
  elongation: number;
  external_heating_mw: number;
};

type Analysis = {
  name: string;
  volume_m3: number;
  plasma_pressure_kpa: number;
  beta_percent: number;
  triple_product_kev_s_m3: number;
  lawson_reference_ratio: number;
  stored_energy_mj: number;
  dt_reactivity_m3_s: number;
  fusion_power_mw: number;
  alpha_heating_mw: number;
  transport_loss_mw: number;
  plasma_gain_q: number | null;
  net_heating_margin_mw: number;
  diagnostics: string[];
  assumptions: string[];
  disclaimer: string;
};

type NumberField = Exclude<keyof Scenario, "name">;

const baseline: Scenario = {
  name: "Baseline tokamak",
  temperature_kev: 15,
  density_1e20_m3: 1,
  confinement_time_s: 3,
  magnetic_field_t: 5.3,
  major_radius_m: 6.2,
  minor_radius_m: 2,
  elongation: 1.7,
  external_heating_mw: 50,
};

const presets: Record<string, Scenario> = {
  "ITER-like": baseline,
  Compact: {
    name: "Compact high-field",
    temperature_kev: 18,
    density_1e20_m3: 1.5,
    confinement_time_s: 1.2,
    magnetic_field_t: 12,
    major_radius_m: 3.3,
    minor_radius_m: 1.1,
    elongation: 1.8,
    external_heating_mw: 40,
  },
  Stellarator: {
    name: "Steady-state stellarator study",
    temperature_kev: 10,
    density_1e20_m3: 1.2,
    confinement_time_s: 1.5,
    magnetic_field_t: 3,
    major_radius_m: 5.5,
    minor_radius_m: 0.55,
    elongation: 1.2,
    external_heating_mw: 20,
  },
};

const controls: Array<{
  key: NumberField;
  label: string;
  unit: string;
  min: number;
  max: number;
  step: number;
}> = [
  { key: "temperature_kev", label: "Ion temperature", unit: "keV", min: 1, max: 50, step: 0.5 },
  { key: "density_1e20_m3", label: "Ion density", unit: "10²⁰ m⁻³", min: 0.1, max: 5, step: 0.1 },
  { key: "confinement_time_s", label: "Energy confinement", unit: "s", min: 0.1, max: 20, step: 0.1 },
  { key: "magnetic_field_t", label: "Magnetic field", unit: "T", min: 1, max: 20, step: 0.1 },
  { key: "major_radius_m", label: "Major radius", unit: "m", min: 1, max: 15, step: 0.1 },
  { key: "minor_radius_m", label: "Minor radius", unit: "m", min: 0.2, max: 5, step: 0.1 },
  { key: "elongation", label: "Elongation κ", unit: "", min: 1, max: 2.8, step: 0.05 },
  { key: "external_heating_mw", label: "External heating", unit: "MW", min: 0, max: 200, step: 1 },
];

function format(value: number, digits = 2) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value);
}

export default function FusionResearchAssistant() {
  const [scenario, setScenario] = useState(baseline);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [reference, setReference] = useState<Analysis | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState<"analysis" | "assistant" | null>(null);

  function update(key: NumberField, value: number) {
    setScenario((current) => ({ ...current, [key]: value }));
  }

  async function runAnalysis() {
    setError("");
    setBusy("analysis");
    try {
      const response = await fetch(`${API_URL}/api/v1/fusion/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(scenario),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Plasma analysis failed");
      if (analysis) setReference(analysis);
      setAnalysis(data);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Plasma analysis failed");
    } finally {
      setBusy(null);
    }
  }

  async function askAssistant(event: FormEvent) {
    event.preventDefault();
    setError("");
    setBusy("assistant");
    try {
      const response = await fetch(`${API_URL}/api/v1/fusion/assistant`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, scenario: analysis }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Assistant request failed");
      setAnswer(data.answer);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Assistant request failed");
    } finally {
      setBusy(null);
    }
  }

  const lawsonPercent = Math.min((analysis?.lawson_reference_ratio ?? 0) * 100, 100);

  return (
    <main className={styles.shell}>
      <nav className={styles.nav}>
        <Link href="/">MULTIVERSE LAB</Link>
        <span>FUSION / RESEARCH ASSISTANT</span>
      </nav>

      <header className={styles.hero}>
        <div>
          <p className={styles.kicker}>PLASMA PHYSICS · 0D DIGITAL TWIN · AZURE OPENAI</p>
          <h1>Fusion<br /><em>Research</em> Copilot</h1>
          <p className={styles.lede}>
            D–Tプラズマの性能空間を探索し、Lawson条件、β、エネルギー収支を
            大学院レベルで批判的に検討する研究支援環境。
          </p>
        </div>
        <div className={styles.orbit} aria-label="stylized plasma confinement diagram">
          <div className={styles.core} />
          <span className={styles.orbitLabel}>D + T → α + n</span>
        </div>
      </header>

      <aside className={styles.notice}>
        <b>EDUCATIONAL MODEL</b>
        <span>設計・安全解析・施設運転には使用できません。実験操作は所属機関の承認手順に従ってください。</span>
      </aside>

      <section className={styles.workspace}>
        <article className={styles.controlPanel}>
          <div className={styles.sectionHeading}>
            <div><span>01</span><h2>Plasma scenario</h2></div>
            <div className={styles.presets}>
              {Object.entries(presets).map(([name, values]) => (
                <button key={name} onClick={() => setScenario(values)}>{name}</button>
              ))}
            </div>
          </div>
          <label className={styles.nameField}>
            <span>Scenario name</span>
            <input value={scenario.name} maxLength={100} onChange={(event) =>
              setScenario({ ...scenario, name: event.target.value })
            } />
          </label>
          <div className={styles.controls}>
            {controls.map((control) => (
              <label key={control.key}>
                <span>{control.label}</span>
                <div>
                  <input
                    type="range"
                    min={control.min}
                    max={control.max}
                    step={control.step}
                    value={scenario[control.key]}
                    onChange={(event) => update(control.key, Number(event.target.value))}
                  />
                  <output>{scenario[control.key]} <small>{control.unit}</small></output>
                </div>
              </label>
            ))}
          </div>
          <button className={styles.analyze} onClick={runAnalysis} disabled={busy !== null}>
            {busy === "analysis" ? "SOLVING ENERGY BALANCE…" : "RUN PLASMA ANALYSIS →"}
          </button>
        </article>

        <article className={styles.resultPanel}>
          <div className={styles.sectionHeading}>
            <div><span>02</span><h2>Performance envelope</h2></div>
            <i className={analysis ? styles.live : ""}>{analysis ? "ANALYZED" : "AWAITING INPUT"}</i>
          </div>
          {analysis ? (
            <>
              <div className={styles.primaryMetrics}>
                <div>
                  <span>Fusion power</span>
                  <strong>{format(analysis.fusion_power_mw, 1)}</strong>
                  <small>MW thermal</small>
                </div>
                <div>
                  <span>Plasma gain Q</span>
                  <strong>{analysis.plasma_gain_q === null ? "—" : format(analysis.plasma_gain_q)}</strong>
                  <small>Pfusion / Pexternal</small>
                </div>
                <div>
                  <span>Volume β</span>
                  <strong>{format(analysis.beta_percent)}</strong>
                  <small>percent</small>
                </div>
              </div>
              <div className={styles.lawson}>
                <div>
                  <span>LAWSON TRIPLE PRODUCT</span>
                  <b>{analysis.triple_product_kev_s_m3.toExponential(2)} keV·s·m⁻³</b>
                </div>
                <strong>{format(analysis.lawson_reference_ratio)}× ref.</strong>
                <div className={styles.gauge}><i style={{ width: `${lawsonPercent}%` }} /></div>
              </div>
              <div className={styles.energyGrid}>
                <div><span>Stored energy</span><b>{format(analysis.stored_energy_mj)} MJ</b></div>
                <div><span>Alpha heating</span><b>{format(analysis.alpha_heating_mw)} MW</b></div>
                <div><span>Transport loss</span><b>{format(analysis.transport_loss_mw)} MW</b></div>
                <div><span>Heating margin</span><b className={analysis.net_heating_margin_mw < 0 ? styles.negative : ""}>{format(analysis.net_heating_margin_mw)} MW</b></div>
              </div>
              {reference && (
                <p className={styles.comparison}>
                  前回比: fusion power {analysis.fusion_power_mw >= reference.fusion_power_mw ? "▲" : "▼"}{" "}
                  {format(Math.abs(analysis.fusion_power_mw - reference.fusion_power_mw), 1)} MW
                </p>
              )}
              <ul className={styles.diagnostics}>
                {analysis.diagnostics.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </>
          ) : (
            <div className={styles.empty}>
              <span>nTτ<sub>E</sub></span>
              <p>シナリオを解析すると、閉じ込め性能とエネルギー収支を表示します。</p>
            </div>
          )}
        </article>
      </section>

      <section className={styles.assistant}>
        <div>
          <span className={styles.index}>03</span>
          <p className={styles.kicker}>RESEARCH DIALOGUE</p>
          <h2>Ask the fusion AI</h2>
          <p>
            結果の解釈、欠落している物理、実験仮説、診断計画を質問できます。
            Azure OpenAI未設定時はAPIが明示的に通知します。
          </p>
          <div className={styles.prompts}>
            {["β限界とMHD安定性の関係は？", "この0Dモデルで欠落している輸送物理は？", "Lawson条件の不確かさをどう評価する？"].map((prompt) => (
              <button key={prompt} onClick={() => setQuestion(prompt)}>{prompt}</button>
            ))}
          </div>
        </div>
        <form onSubmit={askAssistant}>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="研究上の問いを入力…"
            minLength={3}
            maxLength={2000}
            required
          />
          <button disabled={busy !== null}>
            {busy === "assistant" ? "THINKING…" : "ASK WITH SCENARIO CONTEXT"}
          </button>
          {answer && <div className={styles.answer}>{answer}</div>}
        </form>
      </section>

      {analysis && (
        <details className={styles.assumptions}>
          <summary>Model assumptions & limitations</summary>
          <ul>{analysis.assumptions.map((item) => <li key={item}>{item}</li>)}</ul>
          <p>{analysis.disclaimer}</p>
        </details>
      )}
      {error && <div className={styles.error}>{error}</div>}
    </main>
  );
}
