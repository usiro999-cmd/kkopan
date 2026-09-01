"use client";

import Link from "next/link";
import { FormEvent, useMemo, useState } from "react";
import styles from "./galactic.module.css";

type Channel = {
  id: string;
  name: string;
  sector: string;
  distance: string;
  status: "online" | "standby";
  color: string;
};

type Message = {
  id: number;
  sender: "earth" | "empire";
  original: string;
  translated: string;
  time: string;
};

const channels: Channel[] = [
  { id: "vega", name: "ヴェガ統合評議会", sector: "アルファ宙域 · V-09", distance: "25.0 ly", status: "online", color: "#67f7d2" },
  { id: "orion", name: "オリオン外交局", sector: "リゲル回廊 · O-31", distance: "864 ly", status: "online", color: "#70b8ff" },
  { id: "andromeda", name: "アンドロメダ観測使節", sector: "M31 外縁域", distance: "2.5M ly", status: "standby", color: "#bd82ff" },
];

const initialMessages: Record<string, Message[]> = {
  vega: [
    {
      id: 1,
      sender: "empire",
      original: "⟟⋏⏁⟒⍀⌇⏁⟒⌰⌰⏃⍀ ⍜⏚⌇⟒⍀⎐⟒⍀, ⍙⟒ ⍀⟒☊⟒⟟⎐⟒ ⊬⍜⎍.",
      translated: "恒星間観測者へ。あなた方の信号を受信しました。",
      time: "18:03:12",
    },
    {
      id: 2,
      sender: "earth",
      original: "This is Earth Liaison KAWARAMACHI. We request peaceful first contact.",
      translated: "こちらは地球連絡局KAWARAMACHI。平和的な第一種接触を要請します。",
      time: "18:05:48",
    },
    {
      id: 3,
      sender: "empire",
      original: "⏁⊑⟒ ⎐⟒☌⏃ ☊⍜⎍⋏☊⟟⌰ ⏃☊☊⟒⌿⏁⌇ ⊬⍜⎍⍀ ☊⊑⏃⋏⋏⟒⌰.",
      translated: "ヴェガ統合評議会は、地球の通信チャンネルを承認します。",
      time: "18:08:21",
    },
  ],
  orion: [
    {
      id: 4,
      sender: "empire",
      original: "⌿⍀⍜⏁⍜☊⍜⌰ ⍜-31 ⏃☊⏁⟟⎐⟒.",
      translated: "外交プロトコル O-31 を起動しました。",
      time: "17:42:09",
    },
  ],
  andromeda: [],
};

const quickMessages = [
  "平和的な科学交流を提案します。",
  "地球文明の観測データを共有します。",
  "文化・言語交換プロトコルを開始してください。",
];

function Glyph({ children }: { children: React.ReactNode }) {
  return <span className={styles.glyph}>{children}</span>;
}

export default function GalacticCommunication() {
  const [activeChannel, setActiveChannel] = useState("vega");
  const [messages, setMessages] = useState(initialMessages);
  const [draft, setDraft] = useState("");
  const [isTransmitting, setIsTransmitting] = useState(false);
  const [translation, setTranslation] = useState(true);

  const channel = channels.find((item) => item.id === activeChannel) ?? channels[0];
  const activeMessages = messages[activeChannel] ?? [];
  const signalStrength = activeChannel === "vega" ? 98.7 : activeChannel === "orion" ? 84.2 : 41.6;
  const latency = activeChannel === "vega" ? "25.0 年" : activeChannel === "orion" ? "864 年" : "2.5M 年";

  const stardate = useMemo(() => {
    const date = new Date();
    return `${date.getUTCFullYear()}.${String(date.getUTCMonth() + 1).padStart(2, "0")}.${String(date.getUTCDate()).padStart(2, "0")}`;
  }, []);

  function transmit(event: FormEvent) {
    event.preventDefault();
    const text = draft.trim();
    if (!text || isTransmitting || channel.status !== "online") return;

    setIsTransmitting(true);
    window.setTimeout(() => {
      const now = new Date().toLocaleTimeString("ja-JP", { hour12: false });
      const outgoing: Message = {
        id: Date.now(),
        sender: "earth",
        original: text,
        translated: `地球標準語から銀河共通プロトコルへ変換済み：${text}`,
        time: now,
      };
      setMessages((current) => ({
        ...current,
        [activeChannel]: [...(current[activeChannel] ?? []), outgoing],
      }));
      setDraft("");
      setIsTransmitting(false);
    }, 900);
  }

  return (
    <main className={styles.shell}>
      <div className={styles.starfield} />
      <header className={styles.header}>
        <Link href="/" className={styles.brand}>
          <span className={styles.brandMark}><Glyph>⌬</Glyph></span>
          <span><strong>CELESTIAL LINK</strong><small>SPACEAI KAWARAMACHI · XENO COMMUNICATION</small></span>
        </Link>
        <div className={styles.headerStatus}>
          <Link href="/galactic/os" className={styles.computeLink}>GALACTIC OS</Link>
          <Link href="/galactic/alliance" className={styles.computeLink}>ALLIANCE</Link>
          <Link href="/galactic/compute" className={styles.computeLink}>COMPUTE GRID</Link>
          <span className={styles.simulation}>FICTIONAL SIMULATION</span>
          <span className={styles.online}><i /> QUANTUM RELAY ONLINE</span>
          <span className={styles.stardate}>STARDATE {stardate}</span>
        </div>
      </header>

      <section className={styles.workspace}>
        <aside className={styles.sidebar}>
          <div className={styles.sidebarHeading}>
            <span>CONTACT NETWORK</span>
            <strong>外交チャンネル</strong>
          </div>
          <div className={styles.channelList}>
            {channels.map((item) => (
              <button
                key={item.id}
                className={activeChannel === item.id ? styles.channelActive : styles.channel}
                onClick={() => setActiveChannel(item.id)}
              >
                <span className={styles.channelOrb} style={{ "--orb": item.color } as React.CSSProperties}><i /></span>
                <span className={styles.channelCopy}>
                  <strong>{item.name}</strong>
                  <small>{item.sector}</small>
                  <em>{item.distance}</em>
                </span>
                <span className={item.status === "online" ? styles.statusOnline : styles.statusStandby}>
                  {item.status === "online" ? "接続中" : "待機"}
                </span>
              </button>
            ))}
          </div>

          <div className={styles.civilization}>
            <span className={styles.label}>CIVILIZATION PROFILE</span>
            <div className={styles.levelRing}>
              <div><small>KARDASHEV</small><strong>III</strong><em>銀河文明</em></div>
            </div>
            <dl>
              <div><dt>エネルギー規模</dt><dd>10³⁶ W</dd></div>
              <div><dt>恒星系ネットワーク</dt><dd>8.4B</dd></div>
              <div><dt>外交信頼度</dt><dd className={styles.safe}>安定</dd></div>
            </dl>
          </div>
          <Link href="/" className={styles.back}>← SpaceAIへ戻る</Link>
        </aside>

        <section className={styles.communication}>
          <div className={styles.contactHeader}>
            <div>
              <span className={styles.label}>SECURE DIPLOMATIC CHANNEL</span>
              <h1>{channel.name}</h1>
              <p><i /> 暗号化された量子もつれ通信 · 認証済み</p>
            </div>
            <div className={styles.contactMetrics}>
              <span><small>SIGNAL</small><strong>{signalStrength}%</strong></span>
              <span><small>PHOTON DELAY</small><strong>{latency}</strong></span>
              <button aria-label="チャンネル設定">⋮</button>
            </div>
          </div>

          <div className={styles.messages}>
            <div className={styles.protocolNotice}>
              <Glyph>◇</Glyph>
              <div><strong>接触プロトコル CL-3 有効</strong><span>すべての通信は外交記録として保存されます</span></div>
            </div>

            {activeMessages.length === 0 && (
              <div className={styles.empty}>
                <Glyph>⌁</Glyph>
                <h2>応答待機中</h2>
                <p>このチャンネルは深宇宙リレーの同期を待っています。</p>
              </div>
            )}

            {activeMessages.map((message) => (
              <article className={message.sender === "earth" ? styles.messageEarth : styles.messageEmpire} key={message.id}>
                <div className={styles.avatar}>{message.sender === "earth" ? "地" : <Glyph>⌬</Glyph>}</div>
                <div className={styles.bubble}>
                  <header><strong>{message.sender === "earth" ? "地球連絡局" : channel.name}</strong><time>{message.time}</time></header>
                  <p className={message.sender === "empire" ? styles.alienText : undefined}>{message.original}</p>
                  {translation && <div className={styles.translation}><span>QUANTUM TRANSLATION</span>{message.translated}</div>}
                </div>
              </article>
            ))}
            {isTransmitting && (
              <div className={styles.transmitting}><i /><i /><i /><span>量子符号化中</span></div>
            )}
          </div>

          <div className={styles.composer}>
            <div className={styles.quickReplies}>
              {quickMessages.map((message) => <button key={message} onClick={() => setDraft(message)}>{message}</button>)}
            </div>
            <form onSubmit={transmit}>
              <button type="button" className={translation ? styles.translateOn : styles.translateOff} onClick={() => setTranslation((value) => !value)}>
                <Glyph>文</Glyph><span>量子翻訳</span>
              </button>
              <textarea
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder={channel.status === "online" ? "銀河共通プロトコルでメッセージを作成…" : "このチャンネルは現在待機中です"}
                maxLength={500}
                disabled={channel.status !== "online"}
              />
              <span className={styles.counter}>{draft.length}/500</span>
              <button className={styles.send} disabled={!draft.trim() || isTransmitting || channel.status !== "online"}>
                <span>{isTransmitting ? "送信中" : "送信"}</span><Glyph>➤</Glyph>
              </button>
            </form>
            <p className={styles.disclaimer}>これは創作上の文明との通信を再現したエンターテインメント用シミュレーションです。実在の地球外通信ではありません。</p>
          </div>
        </section>

        <aside className={styles.intelligence}>
          <div className={styles.mapCard}>
            <header><span className={styles.label}>GALACTIC POSITION</span><strong>銀河座標</strong></header>
            <div className={styles.galaxyMap}>
              <div className={styles.galaxyCore} />
              <div className={`${styles.galaxyArm} ${styles.armOne}`} />
              <div className={`${styles.galaxyArm} ${styles.armTwo}`} />
              <div className={`${styles.galaxyArm} ${styles.armThree}`} />
              <span className={`${styles.mapNode} ${styles.earthNode}`}><i />SOL</span>
              <span className={`${styles.mapNode} ${styles.empireNode}`}><i />{activeChannel.toUpperCase()}</span>
              <svg viewBox="0 0 300 210" aria-hidden="true"><path d="M78 142 Q155 45 230 82" /></svg>
            </div>
            <div className={styles.coordinates}>
              <span><small>ORIGIN</small><strong>SOL · 0.0.0</strong></span>
              <span><small>DESTINATION</small><strong>{channel.sector}</strong></span>
            </div>
          </div>

          <div className={styles.telemetry}>
            <header><span className={styles.label}>RELAY TELEMETRY</span><strong>通信状態</strong></header>
            <div className={styles.telemetryRow}><span>量子コヒーレンス</span><strong>99.94%</strong><i><b style={{ width: "99.94%" }} /></i></div>
            <div className={styles.telemetryRow}><span>翻訳信頼度</span><strong>96.18%</strong><i><b style={{ width: "96.18%" }} /></i></div>
            <div className={styles.telemetryRow}><span>外交安全指数</span><strong>88.70%</strong><i><b style={{ width: "88.7%" }} /></i></div>
          </div>

          <div className={styles.directive}>
            <span className={styles.label}>EARTH DIRECTIVE 01</span>
            <Glyph>△</Glyph>
            <strong>非敵対的接触を維持</strong>
            <p>技術移転の要求、軍事座標、個人情報の送信は禁止されています。</p>
          </div>
        </aside>
      </section>
    </main>
  );
}
