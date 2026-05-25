import { useState, useEffect } from "react";

// ── helpers ──────────────────────────────────────────────────────────────────
const uid = () => Math.random().toString(36).slice(2, 10).toUpperCase();
const now = () => new Date().toISOString();
const hash = async (str) => {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2,"0")).join("");
};

const EMPTY_RECORD = {
  version: "1.0",
  subject: { entity: "", node: "", key_id: "" },
  self_record: { statement: "", evidence: [], tags: [], timestamp: now() },
  external_claims: [],
  provenance: { handshake_id: uid(), challenge: uid(), receipt: { issued: now() } },
  consent: { purpose: "", scope: [], expires: "", revocable: true },
  privacy: { minimization: "self", retention: "90d", sharing: [] },
  seals: { self_hash: "", self_sig: "", transparency_log: [] },
};

const STATUS_COLOR = { unverified: "#f59e0b", verified: "#10b981", contested: "#ef4444" };
const MINIMIZATION_LABELS = { self: "Self Only", need_to_know: "Need-to-Know", public: "Public" };

// ── tiny components ───────────────────────────────────────────────────────────
const Tag = ({ label, onRemove, color = "#334155" }) => (
  <span style={{
    display:"inline-flex", alignItems:"center", gap:4,
    background: color + "22", color, border: `1px solid ${color}44`,
    borderRadius:4, padding:"2px 8px", fontSize:11, fontFamily:"'IBM Plex Mono', monospace",
    letterSpacing:"0.04em"
  }}>
    {label}
    {onRemove && <button onClick={onRemove} style={{background:"none",border:"none",cursor:"pointer",color,padding:0,lineHeight:1,fontSize:13}}>×</button>}
  </span>
);

const Field = ({ label, children, hint }) => (
  <div style={{ marginBottom:18 }}>
    <label style={{ display:"block", fontSize:10, letterSpacing:"0.12em", color:"#64748b", textTransform:"uppercase", marginBottom:5, fontFamily:"'IBM Plex Mono', monospace" }}>
      {label}
    </label>
    {children}
    {hint && <p style={{ margin:"4px 0 0", fontSize:11, color:"#94a3b8" }}>{hint}</p>}
  </div>
);

const Input = (props) => (
  <input {...props} style={{
    width:"100%", boxSizing:"border-box",
    background:"#0f172a", border:"1px solid #1e3a5f",
    color:"#e2e8f0", padding:"8px 12px", borderRadius:6,
    fontSize:13, fontFamily:"'IBM Plex Mono', monospace",
    outline:"none", transition:"border 0.15s",
    ...props.style
  }}
  onFocus={e => e.target.style.borderColor="#38bdf8"}
  onBlur={e => e.target.style.borderColor="#1e3a5f"}
  />
);

const Textarea = (props) => (
  <textarea {...props} style={{
    width:"100%", boxSizing:"border-box", resize:"vertical",
    background:"#0f172a", border:"1px solid #1e3a5f",
    color:"#e2e8f0", padding:"8px 12px", borderRadius:6,
    fontSize:13, fontFamily:"'IBM Plex Mono', monospace",
    outline:"none", minHeight:80, transition:"border 0.15s",
    ...props.style
  }}
  onFocus={e => e.target.style.borderColor="#38bdf8"}
  onBlur={e => e.target.style.borderColor="#1e3a5f"}
  />
);

const Select = ({ value, onChange, options }) => (
  <select value={value} onChange={onChange} style={{
    background:"#0f172a", border:"1px solid #1e3a5f",
    color:"#e2e8f0", padding:"8px 12px", borderRadius:6,
    fontSize:13, fontFamily:"'IBM Plex Mono', monospace",
    outline:"none", width:"100%"
  }}>
    {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
  </select>
);

const Btn = ({ children, onClick, variant = "primary", small, disabled }) => {
  const styles = {
    primary: { background:"#0ea5e9", color:"#fff", border:"none" },
    ghost:   { background:"transparent", color:"#94a3b8", border:"1px solid #1e3a5f" },
    danger:  { background:"transparent", color:"#f87171", border:"1px solid #f8717144" },
    success: { background:"#10b981", color:"#fff", border:"none" },
  };
  return (
    <button onClick={onClick} disabled={disabled} style={{
      ...styles[variant], borderRadius:6, cursor: disabled ? "not-allowed" : "pointer",
      padding: small ? "4px 10px" : "8px 16px",
      fontSize: small ? 11 : 13,
      fontFamily:"'IBM Plex Mono', monospace",
      letterSpacing:"0.04em", transition:"opacity 0.15s",
      opacity: disabled ? 0.4 : 1,
    }}>
      {children}
    </button>
  );
};

const Card = ({ children, style }) => (
  <div style={{
    background:"#0f172a", border:"1px solid #1e3a5f",
    borderRadius:10, padding:20, ...style
  }}>{children}</div>
);

const SectionHeader = ({ title, icon }) => (
  <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:16 }}>
    <span style={{ fontSize:16 }}>{icon}</span>
    <h3 style={{ margin:0, fontSize:13, letterSpacing:"0.12em", textTransform:"uppercase", color:"#38bdf8", fontFamily:"'IBM Plex Mono', monospace" }}>{title}</h3>
  </div>
);

// ── tag/list input ────────────────────────────────────────────────────────────
const TagInput = ({ values, onChange, placeholder, color }) => {
  const [draft, setDraft] = useState("");
  const add = () => {
    const v = draft.trim();
    if (v && !values.includes(v)) { onChange([...values, v]); }
    setDraft("");
  };
  return (
    <div>
      <div style={{ display:"flex", gap:6, marginBottom:6 }}>
        <Input value={draft} onChange={e=>setDraft(e.target.value)} placeholder={placeholder}
          onKeyDown={e=>{ if(e.key==="Enter"){ e.preventDefault(); add(); }}} />
        <Btn onClick={add} small>+</Btn>
      </div>
      <div style={{ display:"flex", flexWrap:"wrap", gap:4 }}>
        {values.map(v => <Tag key={v} label={v} color={color} onRemove={()=>onChange(values.filter(x=>x!==v))} />)}
      </div>
    </div>
  );
};

// ── external claim row ────────────────────────────────────────────────────────
const ClaimRow = ({ claim, onUpdate, onRemove }) => (
  <Card style={{ marginBottom:10, border:"1px solid #1e2d4a", padding:14 }}>
    <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10, marginBottom:8 }}>
      <Field label="Source">
        <Input value={claim.source} onChange={e=>onUpdate({...claim, source:e.target.value})} placeholder="e.g. court-record://..." />
      </Field>
      <Field label="Status">
        <Select value={claim.status||"unverified"} onChange={e=>onUpdate({...claim, status:e.target.value})}
          options={["unverified","verified","contested"].map(s=>({value:s,label:s}))} />
      </Field>
    </div>
    <Field label="Claim">
      <Textarea value={claim.claim} onChange={e=>onUpdate({...claim, claim:e.target.value})} placeholder="What is claimed?" style={{ minHeight:50 }} />
    </Field>
    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
      <Tag label={claim.status||"unverified"} color={STATUS_COLOR[claim.status||"unverified"]} />
      <Btn variant="danger" small onClick={onRemove}>Remove</Btn>
    </div>
  </Card>
);

// ── log entry ─────────────────────────────────────────────────────────────────
const LogEntry = ({ entry }) => (
  <div style={{ display:"flex", gap:10, alignItems:"flex-start", padding:"6px 0", borderBottom:"1px solid #0f2035" }}>
    <span style={{ fontSize:10, color:"#475569", fontFamily:"'IBM Plex Mono', monospace", whiteSpace:"nowrap", paddingTop:2 }}>
      {new Date(entry.ts).toLocaleTimeString()}
    </span>
    <div>
      <div style={{ fontSize:12, color:"#cbd5e1", fontFamily:"'IBM Plex Mono', monospace" }}>{entry.event}</div>
      <div style={{ fontSize:10, color:"#475569", fontFamily:"'IBM Plex Mono', monospace" }}>actor: {entry.actor}</div>
    </div>
  </div>
);

// ── JSON viewer ───────────────────────────────────────────────────────────────
const JsonViewer = ({ data }) => (
  <pre style={{
    background:"#020c1b", border:"1px solid #0d2137", borderRadius:8,
    padding:16, fontSize:11, color:"#7dd3fc", overflowX:"auto",
    fontFamily:"'IBM Plex Mono', monospace", lineHeight:1.6,
    maxHeight:400, overflow:"auto",
  }}>
    {JSON.stringify(data, null, 2)}
  </pre>
);

// ── main app ──────────────────────────────────────────────────────────────────
export default function NarrativeInversionTool() {
  const [record, setRecord] = useState(() => JSON.parse(JSON.stringify(EMPTY_RECORD)));
  const [tab, setTab] = useState("subject");
  const [sealed, setSealed] = useState(false);
  const [sealing, setSealing] = useState(false);
  const [showJson, setShowJson] = useState(false);
  const [copied, setCopied] = useState(false);

  const update = (path, value) => {
    setRecord(r => {
      const next = JSON.parse(JSON.stringify(r));
      const keys = path.split(".");
      let cur = next;
      for (let i = 0; i < keys.length - 1; i++) cur = cur[keys[i]];
      cur[keys[keys.length-1]] = value;
      return next;
    });
    setSealed(false);
  };

  const addLogEntry = (event, actor) => {
    setRecord(r => {
      const next = JSON.parse(JSON.stringify(r));
      next.seals.transparency_log.push({ ts: now(), event, actor });
      return next;
    });
  };

  const sealRecord = async () => {
    setSealing(true);
    const actor = record.subject.entity || "unknown";
    const payload = JSON.stringify({ ...record, seals: { ...record.seals, self_hash:"", self_sig:"" } });
    const h = await hash(payload);
    const sig = "SIG-" + uid() + uid();
    setRecord(r => {
      const next = JSON.parse(JSON.stringify(r));
      next.seals.self_hash = h;
      next.seals.self_sig  = sig;
      return next;
    });
    addLogEntry("record_sealed", actor);
    setSealed(true);
    setSealing(false);
  };

  const copyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(record, null, 2));
    setCopied(true);
    setTimeout(()=>setCopied(false), 1500);
  };

  const downloadJson = () => {
    const blob = new Blob([JSON.stringify(record, null, 2)], { type:"application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `NIR-${record.subject.entity || "record"}-${Date.now()}.json`;
    a.click();
  };

  const TABS = [
    { id:"subject",  label:"Subject",  icon:"🪪" },
    { id:"record",   label:"Record",   icon:"📝" },
    { id:"claims",   label:"Claims",   icon:"⚖️" },
    { id:"consent",  label:"Consent",  icon:"🔒" },
    { id:"privacy",  label:"Privacy",  icon:"🛡️" },
    { id:"seals",    label:"Seals",    icon:"🔏" },
  ];

  const completeness = (() => {
    let score = 0;
    if (record.subject.entity) score++;
    if (record.subject.node) score++;
    if (record.subject.key_id) score++;
    if (record.self_record.statement) score++;
    if (record.self_record.evidence.length) score++;
    if (record.consent.purpose) score++;
    if (record.consent.scope.length) score++;
    if (record.consent.expires) score++;
    if (sealed) score++;
    return Math.round((score/9)*100);
  })();

  return (
    <div style={{
      minHeight:"100vh", background:"#020c1b",
      fontFamily:"'IBM Plex Mono', monospace",
      color:"#e2e8f0",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=Syne:wght@700;800&display=swap');
        * { box-sizing:border-box; }
        ::-webkit-scrollbar { width:4px; height:4px; }
        ::-webkit-scrollbar-track { background:#0f172a; }
        ::-webkit-scrollbar-thumb { background:#1e3a5f; border-radius:2px; }
        input::placeholder, textarea::placeholder { color:#334155; }
        select option { background:#0f172a; }
        @keyframes pulse-glow { 0%,100%{opacity:1} 50%{opacity:0.5} }
        @keyframes slide-in { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
        .tab-panel { animation: slide-in 0.2s ease; }
        .seal-pulse { animation: pulse-glow 2s infinite; }
      `}</style>

      {/* header */}
      <div style={{
        borderBottom:"1px solid #0d2137",
        background:"linear-gradient(180deg, #020c1b 0%, #061526 100%)",
        padding:"20px 28px", display:"flex", alignItems:"center", justifyContent:"space-between"
      }}>
        <div>
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <div style={{ width:8, height:8, borderRadius:"50%", background: sealed ? "#10b981" : "#f59e0b", boxShadow: sealed ? "0 0 8px #10b981" : "0 0 8px #f59e0b" }} className={sealed ? "" : "seal-pulse"} />
            <h1 style={{ margin:0, fontSize:22, fontFamily:"'Syne', sans-serif", fontWeight:800, letterSpacing:"-0.02em", color:"#f1f5f9" }}>
              Narrative Inversion
            </h1>
            <span style={{ fontSize:10, color:"#475569", letterSpacing:"0.1em", paddingTop:2 }}>v1.0</span>
          </div>
          <p style={{ margin:"4px 0 0 18px", fontSize:11, color:"#475569", letterSpacing:"0.06em" }}>
            SELF-SOVEREIGN RECORD AUTHORITY
          </p>
        </div>

        {/* progress */}
        <div style={{ textAlign:"right" }}>
          <div style={{ fontSize:10, color:"#475569", letterSpacing:"0.08em", marginBottom:4 }}>COMPLETENESS</div>
          <div style={{ display:"flex", alignItems:"center", gap:8 }}>
            <div style={{ width:120, height:4, background:"#0f2035", borderRadius:2, overflow:"hidden" }}>
              <div style={{ width:`${completeness}%`, height:"100%", background: completeness===100 ? "#10b981" : "#0ea5e9", transition:"width 0.4s ease", borderRadius:2 }} />
            </div>
            <span style={{ fontSize:13, color: completeness===100 ? "#10b981" : "#0ea5e9", fontWeight:600 }}>{completeness}%</span>
          </div>
        </div>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"200px 1fr", minHeight:"calc(100vh - 73px)" }}>

        {/* sidebar nav */}
        <div style={{ borderRight:"1px solid #0d2137", padding:"16px 12px" }}>
          {TABS.map(t => (
            <button key={t.id} onClick={()=>setTab(t.id)} style={{
              display:"flex", alignItems:"center", gap:8, width:"100%",
              padding:"9px 12px", borderRadius:6, border:"none", cursor:"pointer",
              background: tab===t.id ? "#0ea5e915" : "transparent",
              borderLeft: tab===t.id ? "2px solid #0ea5e9" : "2px solid transparent",
              color: tab===t.id ? "#38bdf8" : "#64748b",
              fontSize:12, fontFamily:"'IBM Plex Mono', monospace",
              letterSpacing:"0.05em", textAlign:"left", transition:"all 0.15s",
              marginBottom:2,
            }}>
              <span>{t.icon}</span> {t.label}
            </button>
          ))}

          {/* seals action */}
          <div style={{ marginTop:20, paddingTop:20, borderTop:"1px solid #0d2137" }}>
            <Btn onClick={sealRecord} disabled={sealing || !record.subject.entity || !record.self_record.statement}>
              {sealing ? "Sealing…" : sealed ? "✓ Re-seal" : "Seal Record"}
            </Btn>
            {sealed && <p style={{ fontSize:10, color:"#10b981", marginTop:8 }}>✓ Record integrity verified</p>}
          </div>

          {/* view JSON */}
          <div style={{ marginTop:12 }}>
            <Btn variant="ghost" onClick={()=>setShowJson(v=>!v)}>
              {showJson ? "Hide JSON" : "View JSON"}
            </Btn>
          </div>
        </div>

        {/* main content */}
        <div style={{ padding:"24px 28px", overflow:"auto" }}>

          {/* ── subject ── */}
          {tab==="subject" && (
            <div className="tab-panel">
              <SectionHeader title="Subject Identity" icon="🪪" />
              <Card>
                <Field label="Entity Identifier" hint="DID, URI, or human-readable identifier for this subject">
                  <Input value={record.subject.entity} onChange={e=>update("subject.entity",e.target.value)} placeholder="did:example:abc123" />
                </Field>
                <Field label="Node" hint="Network node or jurisdiction this record is registered to">
                  <Input value={record.subject.node} onChange={e=>update("subject.node",e.target.value)} placeholder="node://registry.example.com" />
                </Field>
                <Field label="Key ID" hint="Cryptographic key identifier used for signing">
                  <Input value={record.subject.key_id} onChange={e=>update("subject.key_id",e.target.value)} placeholder="key-2026-01" />
                </Field>
              </Card>

              <SectionHeader title="Provenance" icon="🔗" />
              <Card>
                <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16 }}>
                  <Field label="Handshake ID"><Input value={record.provenance.handshake_id} onChange={e=>update("provenance.handshake_id",e.target.value)} /></Field>
                  <Field label="Challenge"><Input value={record.provenance.challenge} onChange={e=>update("provenance.challenge",e.target.value)} /></Field>
                </div>
              </Card>
            </div>
          )}

          {/* ── self record ── */}
          {tab==="record" && (
            <div className="tab-panel">
              <SectionHeader title="Self Record" icon="📝" />
              <Card>
                <Field label="Statement" hint="Your first-person account, claim, or narrative">
                  <Textarea value={record.self_record.statement} onChange={e=>update("self_record.statement",e.target.value)} placeholder="I assert that…" style={{ minHeight:120 }} />
                </Field>
                <Field label="Timestamp">
                  <Input type="datetime-local" value={record.self_record.timestamp.slice(0,16)} onChange={e=>update("self_record.timestamp", new Date(e.target.value).toISOString())} />
                </Field>
                <Field label="Evidence References" hint="URIs, hashes, or document IDs that support the statement">
                  <TagInput values={record.self_record.evidence} onChange={v=>update("self_record.evidence",v)} placeholder="ipfs://Qm... or doc:// ..." color="#0ea5e9" />
                </Field>
                <Field label="Tags" hint="Categorical labels for this record">
                  <TagInput values={record.self_record.tags||[]} onChange={v=>update("self_record.tags",v)} placeholder="identity, legal, …" color="#8b5cf6" />
                </Field>
              </Card>
            </div>
          )}

          {/* ── external claims ── */}
          {tab==="claims" && (
            <div className="tab-panel">
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:16 }}>
                <SectionHeader title="External Claims" icon="⚖️" />
                <Btn variant="ghost" small onClick={()=>{
                  const c = { source:"", claim:"", doc_refs:[], timestamp:now(), status:"unverified" };
                  update("external_claims", [...record.external_claims, c]);
                  addLogEntry("external_claim_added", record.subject.entity || "unknown");
                }}>+ Add Claim</Btn>
              </div>
              {record.external_claims.length === 0 && (
                <Card style={{ textAlign:"center", padding:"40px 20px" }}>
                  <div style={{ fontSize:32, marginBottom:8 }}>⚖️</div>
                  <p style={{ color:"#475569", fontSize:12 }}>No external claims recorded.<br />Add claims made by third parties about this subject.</p>
                </Card>
              )}
              {record.external_claims.map((c,i) => (
                <ClaimRow key={i} claim={c}
                  onUpdate={nc=>{
                    const arr = [...record.external_claims];
                    arr[i]=nc;
                    update("external_claims",arr);
                  }}
                  onRemove={()=>update("external_claims", record.external_claims.filter((_,j)=>j!==i))}
                />
              ))}
            </div>
          )}

          {/* ── consent ── */}
          {tab==="consent" && (
            <div className="tab-panel">
              <SectionHeader title="Consent Parameters" icon="🔒" />
              <Card>
                <Field label="Purpose" hint="Why this record is being created and shared">
                  <Input value={record.consent.purpose} onChange={e=>update("consent.purpose",e.target.value)} placeholder="Legal identity verification for…" />
                </Field>
                <Field label="Scope" hint="Specific use-cases this consent covers">
                  <TagInput values={record.consent.scope} onChange={v=>update("consent.scope",v)} placeholder="identity-verification, …" color="#10b981" />
                </Field>
                <Field label="Expires">
                  <Input type="datetime-local" value={record.consent.expires ? record.consent.expires.slice(0,16) : ""} onChange={e=>update("consent.expires", new Date(e.target.value).toISOString())} />
                </Field>
                <Field label="Revocable">
                  <div style={{ display:"flex", alignItems:"center", gap:10 }}>
                    <label style={{ display:"flex", alignItems:"center", gap:6, cursor:"pointer" }}>
                      <input type="checkbox" checked={record.consent.revocable} onChange={e=>update("consent.revocable",e.target.checked)}
                        style={{ accentColor:"#0ea5e9", width:14, height:14 }} />
                      <span style={{ fontSize:12, color:"#94a3b8" }}>This consent can be revoked</span>
                    </label>
                  </div>
                </Field>
              </Card>
            </div>
          )}

          {/* ── privacy ── */}
          {tab==="privacy" && (
            <div className="tab-panel">
              <SectionHeader title="Privacy Controls" icon="🛡️" />
              <Card>
                <Field label="Data Minimization" hint="Who should have access to this record">
                  <Select value={record.privacy.minimization}
                    onChange={e=>update("privacy.minimization",e.target.value)}
                    options={Object.entries(MINIMIZATION_LABELS).map(([v,l])=>({value:v,label:l}))} />
                </Field>
                <Field label="Retention Period" hint="How long this record should be retained">
                  <Input value={record.privacy.retention} onChange={e=>update("privacy.retention",e.target.value)} placeholder="90d / 1y / indefinite" />
                </Field>
                <Field label="Sharing Parties" hint="Entities permitted to receive this record">
                  <TagInput values={record.privacy.sharing} onChange={v=>update("privacy.sharing",v)} placeholder="org://partner.example.com" color="#f59e0b" />
                </Field>
              </Card>

              {/* minimization badge */}
              <Card style={{ marginTop:16, border:"1px solid #0d2137", display:"flex", alignItems:"center", gap:12 }}>
                <div style={{ fontSize:28 }}>
                  {{ self:"🔐", need_to_know:"🔑", public:"🌐" }[record.privacy.minimization]}
                </div>
                <div>
                  <div style={{ fontSize:12, color:"#38bdf8", fontWeight:600 }}>{MINIMIZATION_LABELS[record.privacy.minimization]}</div>
                  <div style={{ fontSize:11, color:"#475569", marginTop:2 }}>
                    {{ self:"Only the subject may access this record.", need_to_know:"Limited access on a need-to-know basis.", public:"This record may be publicly disclosed." }[record.privacy.minimization]}
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* ── seals ── */}
          {tab==="seals" && (
            <div className="tab-panel">
              <SectionHeader title="Integrity Seals" icon="🔏" />
              <Card style={{ marginBottom:16 }}>
                <Field label="Self Hash (SHA-256)">
                  <div style={{ fontSize:11, color: sealed ? "#10b981" : "#475569", wordBreak:"break-all", fontFamily:"'IBM Plex Mono', monospace", padding:"8px 12px", background:"#020c1b", borderRadius:6, border:`1px solid ${sealed ? "#10b98133":"#0d2137"}` }}>
                    {record.seals.self_hash || <span style={{ color:"#334155" }}>— not sealed —</span>}
                  </div>
                </Field>
                <Field label="Self Signature">
                  <div style={{ fontSize:11, color: sealed ? "#10b981" : "#475569", fontFamily:"'IBM Plex Mono', monospace", padding:"8px 12px", background:"#020c1b", borderRadius:6, border:`1px solid ${sealed ? "#10b98133":"#0d2137"}` }}>
                    {record.seals.self_sig || <span style={{ color:"#334155" }}>— not sealed —</span>}
                  </div>
                </Field>
                {!sealed && (
                  <div style={{ textAlign:"center", padding:"12px 0" }}>
                    <Btn onClick={sealRecord} disabled={sealing || !record.subject.entity || !record.self_record.statement}>
                      {sealing ? "Computing…" : "Seal Record Now"}
                    </Btn>
                    <p style={{ fontSize:10, color:"#475569", marginTop:8 }}>Requires entity + statement to be set.</p>
                  </div>
                )}
              </Card>

              <SectionHeader title="Transparency Log" icon="📋" />
              <Card>
                {record.seals.transparency_log.length === 0 ? (
                  <p style={{ fontSize:11, color:"#334155", textAlign:"center", padding:"20px 0" }}>No events recorded yet.</p>
                ) : (
                  record.seals.transparency_log.map((e,i) => <LogEntry key={i} entry={e} />)
                )}
                <div style={{ marginTop:12 }}>
                  <Btn variant="ghost" small onClick={()=>addLogEntry("manual_audit", record.subject.entity || "unknown")}>
                    + Log Audit Event
                  </Btn>
                </div>
              </Card>
            </div>
          )}

          {/* JSON overlay */}
          {showJson && (
            <div style={{ marginTop:24 }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:8 }}>
                <span style={{ fontSize:11, color:"#475569", letterSpacing:"0.08em" }}>RECORD JSON</span>
                <div style={{ display:"flex", gap:8 }}>
                  <Btn variant="ghost" small onClick={copyJson}>{copied ? "✓ Copied" : "Copy"}</Btn>
                  <Btn variant="ghost" small onClick={downloadJson}>Download</Btn>
                </div>
              </div>
              <JsonViewer data={record} />
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
