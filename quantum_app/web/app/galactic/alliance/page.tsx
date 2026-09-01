"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import styles from "./alliance.module.css";

type Member = {
  id: string;
  glyph: string;
  name: string;
  origin: string;
  role: string;
  status: "online" | "relay";
  color: string;
};

type AllianceMessage = {
  id: number;
  member: string;
  glyph: string;
  body: string;
  translation?: string;
  time: string;
  color: string;
};

const members: Member[] = [
  { id: "earth", glyph: "地", name: "地球連邦代表部", origin: "SOL · ORION ARM", role: "新規加盟文明", status: "online", color: "#67d9ff" },
  { id: "vega", glyph: "⌬", name: "ヴェガ統合評議会", origin: "VEGA · V-09", role: "同盟議長", status: "online", color: "#68f4c8" },
  { id: "orion", glyph: "◇", name: "オリオン星系共同体", origin: "RIGEL · O-31", role: "安全保障理事", status: "online", color: "#a98cff" },
  { id: "sirius", glyph: "△", name: "シリウス科学機構", origin: "SIRIUS · S-04", role: "科学技術理事", status: "relay", color: "#ffc875" },
  { id: "andromeda", glyph: "∞", name: "アンドロメダ使節団", origin: "M31 · A-01", role: "銀河間オブザーバー", status: "relay", color: "#f58ccf" },
];

const initialMessages: AllianceMessage[] = [
  { id: 1, member: "ヴェガ統合評議会", glyph: "⌬", body: "第7,204回銀河系同盟総会を開会します。地球連邦代表部の参加を歓迎します。", translation: "原文：⏃⌰⌰⟟⏃⋏☊⟒ ☊⍜⎍⋏☊⟟⌰ ⌇⟒⌇⌇⟟⍜⋏ 7204 ⟟⌇ ⋏⍜⍙ ⍜⌿⟒⋏.", time: "19:02", color: "#68f4c8" },
  { id: 2, member: "シリウス科学機構", glyph: "△", body: "共同観測網から、ペルセウス腕で重力波異常を検出しました。全加盟文明へ解析データを共有します。", translation: "翻訳信頼度 98.4% · 科学プロトコル S-11", time: "19:05", color: "#ffc875" },
  { id: 3, member: "地球連邦代表部", glyph: "地", body: "地球の観測資源を共同解析へ提供します。平和的な科学協力を支持します。", time: "19:08", color: "#67d9ff" },
];

const agenda = [
  { id: "resolution", title: "共同観測決議 G-2048", detail: "ペルセウス腕の重力波異常を同盟共同観測網で解析", yes: 72, abstain: 18, no: 10 },
  { id: "earth", title: "地球文明 正式加盟審査", detail: "技術・文化・非敵対原則に基づく加盟資格の審議", yes: 61, abstain: 31, no: 8 },
];

export default function GalacticAlliance() {
  const [activeMember, setActiveMember] = useState("all");
  const [messages, setMessages] = useState(initialMessages);
  const [draft, setDraft] = useState("");
  const [translation, setTranslation] = useState(true);
  const [selectedAgenda, setSelectedAgenda] = useState(0);
  const [vote, setVote] = useState<"yes" | "abstain" | "no" | null>(null);
  const [emergency, setEmergency] = useState(false);

  const visibleMessages = activeMember === "all"
    ? messages
    : messages.filter((message) => message.member === members.find((member) => member.id === activeMember)?.name);
  const activeAgenda = agenda[selectedAgenda];

  function sendMessage(event: FormEvent) {
    event.preventDefault();
    const text = draft.trim();
    if (!text) return;
    setMessages((current) => [
      ...current,
      {
        id: Date.now(),
        member: "地球連邦代表部",
        glyph: "地",
        body: text,
        translation: translation ? "銀河共通語 GCL-7 へ同時翻訳済み" : undefined,
        time: new Date().toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" }),
        color: "#67d9ff",
      },
    ]);
    setDraft("");
  }

  return (
    <main className={styles.shell}>
      <div className={styles.stars} />
      <header className={styles.header}>
        <Link href="/galactic" className={styles.brand}>
          <span>✦</span>
          <div><strong>GALACTIC ALLIANCE</strong><small>UNITED CIVILIZATIONS COMMUNICATION NETWORK</small></div>
        </Link>
        <nav>
          <Link href="/galactic">外交通信</Link>
          <span>同盟通信</span>
          <Link href="/galactic/compute">計算グリッド</Link>
          <Link href="/galactic/os">OS</Link>
        </nav>
        <div className={styles.network}><i /> 5 CIVILIZATIONS LINKED</div>
      </header>

      <section className={styles.layout}>
        <aside className={styles.members}>
          <div className={styles.sectionTitle}><span>ALLIANCE MEMBERS</span><h2>加盟文明</h2></div>
          <button className={activeMember === "all" ? styles.memberActive : styles.member} onClick={() => setActiveMember("all")}>
            <i className={styles.allianceSeal}>✦</i>
            <span><strong>同盟総会チャンネル</strong><small>ALL DELEGATIONS</small></span>
            <b>5</b>
          </button>
          <div className={styles.memberList}>
            {members.map((member) => (
              <button className={activeMember === member.id ? styles.memberActive : styles.member} key={member.id} onClick={() => setActiveMember(member.id)}>
                <i className={styles.memberGlyph} style={{ "--member": member.color } as React.CSSProperties}>{member.glyph}</i>
                <span><strong>{member.name}</strong><small>{member.origin}</small><em>{member.role}</em></span>
                <b className={member.status === "online" ? styles.online : styles.relay}>{member.status === "online" ? "●" : "◌"}</b>
              </button>
            ))}
          </div>
          <div className={styles.charter}>
            <span>ALLIANCE CHARTER</span>
            <strong>銀河系同盟憲章</strong>
            <p>相互尊重、非侵略、知識共有、生命圏保護の4原則。</p>
            <div><i /><i /><i /><i /></div>
          </div>
          <Link href="/" className={styles.back}>← SpaceAI KAWARAMACHI</Link>
        </aside>

        <section className={styles.chamber}>
          <div className={styles.chamberHeader}>
            <div><span>GENERAL ASSEMBLY · SESSION 7204</span><h1>{activeMember === "all" ? "銀河系同盟 総会通信" : members.find((member) => member.id === activeMember)?.name}</h1><p><i /> 多文明量子中継 · GCL-7自動翻訳 · 記録中</p></div>
            <button className={emergency ? styles.emergencyActive : styles.emergency} onClick={() => setEmergency((value) => !value)}>
              <span>△</span>{emergency ? "緊急回線 接続中" : "緊急通信"}
            </button>
          </div>

          {emergency && (
            <div className={styles.emergencyBanner}><span>△</span><div><strong>ALLIANCE PRIORITY CHANNEL ACTIVE</strong><p>全加盟文明へ優先通信帯域を確保しました。これは安全なUIシミュレーションです。</p></div><i /></div>
          )}

          <div className={styles.messageStream}>
            <div className={styles.sessionMarker}><i /><span>銀河標準時 7204.188 · 総会記録開始</span><i /></div>
            {visibleMessages.length === 0 && <div className={styles.empty}><span>◇</span><strong>個別通信記録はありません</strong><p>同盟総会チャンネルから代表団へメッセージを送信できます。</p></div>}
            {visibleMessages.map((message) => (
              <article className={message.member === "地球連邦代表部" ? styles.earthMessage : styles.message} key={message.id}>
                <div className={styles.avatar} style={{ "--member": message.color } as React.CSSProperties}>{message.glyph}</div>
                <div className={styles.messageBody}>
                  <header><strong>{message.member}</strong><time>{message.time} GST</time></header>
                  <p>{message.body}</p>
                  {message.translation && translation && <span className={styles.translation}>◇ GCL-7 TRANSLATION · {message.translation}</span>}
                  <div className={styles.reactions}><button>同意 <b>12</b></button><button>記録 <b>4</b></button><button>共有</button></div>
                </div>
              </article>
            ))}
          </div>

          <form className={styles.composer} onSubmit={sendMessage}>
            <div className={styles.composeTools}>
              <button type="button" className={translation ? styles.translationOn : styles.translationOff} onClick={() => setTranslation((value) => !value)}>◇ 自動翻訳 {translation ? "ON" : "OFF"}</button>
              <span>EARTH DELEGATION · VERIFIED</span>
            </div>
            <div>
              <textarea value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="同盟総会へメッセージを送信…" maxLength={600} />
              <span>{draft.length}/600</span>
              <button disabled={!draft.trim()}>同盟回線へ送信 <b>➤</b></button>
            </div>
            <p>創作上の銀河文明を扱うコミュニケーション・シミュレーションです。</p>
          </form>
        </section>

        <aside className={styles.council}>
          <section className={styles.allianceStatus}>
            <div className={styles.sectionTitle}><span>ALLIANCE STATUS</span><h2>同盟ネットワーク</h2></div>
            <div className={styles.orbit}>
              <div className={styles.core}>✦<small>GA</small></div>
              {members.map((member, index) => <i key={member.id} className={styles[`orbit${index + 1}`]} style={{ "--member": member.color } as React.CSSProperties}>{member.glyph}</i>)}
            </div>
            <dl><div><dt>加盟文明</dt><dd>2,408</dd></div><div><dt>接続星系</dt><dd>8.4B</dd></div><div><dt>平和指数</dt><dd className={styles.safe}>94.7%</dd></div></dl>
          </section>

          <section className={styles.agenda}>
            <div className={styles.sectionTitle}><span>COUNCIL AGENDA</span><h2>共同決議</h2></div>
            <div className={styles.agendaTabs}>{agenda.map((item, index) => <button className={selectedAgenda === index ? styles.agendaActive : undefined} key={item.id} onClick={() => { setSelectedAgenda(index); setVote(null); }}>{String(index + 1).padStart(2, "0")}</button>)}</div>
            <strong>{activeAgenda.title}</strong>
            <p>{activeAgenda.detail}</p>
            <div className={styles.voteBar}><i style={{ width: `${activeAgenda.yes}%` }} /><b style={{ width: `${activeAgenda.abstain}%` }} /></div>
            <div className={styles.voteLegend}><span><i />賛成 {activeAgenda.yes}%</span><span><i />棄権 {activeAgenda.abstain}%</span><span><i />反対 {activeAgenda.no}%</span></div>
            <div className={styles.voteButtons}>
              <button className={vote === "yes" ? styles.voted : undefined} onClick={() => setVote("yes")}>賛成</button>
              <button className={vote === "abstain" ? styles.voted : undefined} onClick={() => setVote("abstain")}>棄権</button>
              <button className={vote === "no" ? styles.votedNo : undefined} onClick={() => setVote("no")}>反対</button>
            </div>
            {vote && <span className={styles.voteRecorded}>地球代表票を記録しました</span>}
          </section>

          <section className={styles.telemetry}>
            <div className={styles.sectionTitle}><span>NETWORK TELEMETRY</span><h2>通信品質</h2></div>
            <div><span>翻訳同期率</span><strong>99.18%</strong><i><b style={{ width: "99.18%" }} /></i></div>
            <div><span>中継コヒーレンス</span><strong>97.42%</strong><i><b style={{ width: "97.42%" }} /></i></div>
            <div><span>暗号化整合性</span><strong>100%</strong><i><b style={{ width: "100%" }} /></i></div>
          </section>
        </aside>
      </section>
    </main>
  );
}
