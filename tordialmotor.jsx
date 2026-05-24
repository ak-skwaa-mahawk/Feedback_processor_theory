import { useState, useEffect, useRef, useCallback } from "react";

// ── constants ────────────────────────────────────────────────────────────────
const BLUEPRINT_PI = 3.14159265;
const BLUEPRINT_RPM = 3000;

// Simulate one stage of tolerance acceptance
// Each stage accepts a small deviation from ideal, signs off, passes it on
function buildToleranceStack(stages, tolPerStage, noiseFactor) {
  const stack = [];
  let accumulated = 0;
  for (let i = 0; i < stages; i++) {
    // Inspector signs off — deviation is within tolerance, accepted
    const deviation = (Math.random() * 2 - 1) * tolPerStage;
    accumulated += deviation;
    const effectiveRPM = BLUEPRINT_RPM + accumulated;
    const effectivePi = BLUEPRINT_PI * (effectiveRPM / BLUEPRINT_RPM);
    stack.push({
      stage: i + 1,
      stageDeviation: deviation,
      accumulatedDeviation: accumulated,
      effectiveRPM,
      effectivePi,
      accepted: true,
    });
  }
  return stack;
}

// Generate RPM signal: blueprint vs real operating, with noise
function generateSignal(points, effectiveRPM, noiseFactor) {
  const blueprint = [];
  const real = [];
  const jitter = [];
  for (let i = 0; i < points; i++) {
    const t = i / points;
    // Blueprint: clean sine at nominal RPM
    const bVal = BLUEPRINT_RPM + Math.sin(t * Math.PI * 2 * 8) * 15;
    // Real: same shape but offset by effective RPM drift + noise
    const drift = effectiveRPM - BLUEPRINT_RPM;
    const noise = (Math.random() - 0.5) * noiseFactor * 2;
    const rVal = bVal + drift + noise;
    blueprint.push(bVal);
    real.push(rVal);
    jitter.push(Math.abs(rVal - bVal));
  }
  return { blueprint, real, jitter };
}

// ── tiny chart ───────────────────────────────────────────────────────────────
function MiniChart({ data, color, height = 80, fill = false, label }) {
  const canvasRef = useRef();
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data.length) return;
    const ctx = canvas.getContext("2d");
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    const pts = data.map((v, i) => [
      (i / (data.length - 1)) * w,
      h - ((v - min) / range) * (h - 8) - 4,
    ]);
    if (fill) {
      ctx.beginPath();
      ctx.moveTo(pts[0][0], h);
      pts.forEach(([x, y]) => ctx.lineTo(x, y));
      ctx.lineTo(pts[pts.length - 1][0], h);
      ctx.closePath();
      ctx.fillStyle = color + "22";
      ctx.fill();
    }
    ctx.beginPath();
    pts.forEach(([x, y], i) => (i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)));
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.stroke();
  }, [data, color, fill]);

  return (
    <div style={{ position: "relative" }}>
      {label && (
        <div style={{ fontSize: 9, color: "#64748b", letterSpacing: "0.1em", marginBottom: 3, fontFamily: "monospace" }}>
          {label}
        </div>
      )}
      <canvas ref={canvasRef} width={320} height={height} style={{ width: "100%", height }} />
    </div>
  );
}

// ── gauge ────────────────────────────────────────────────────────────────────
function Gauge({ value, min, max, label, unit, color = "#f59e0b", size = 110 }) {
  const pct = (value - min) / (max - min);
  const angle = -140 + pct * 280;
  const cx = size / 2, cy = size / 2, r = size * 0.38;
  const arc = (deg) => {
    const rad = ((deg - 90) * Math.PI) / 180;
    return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
  };
  const [sx, sy] = arc(-140);
  const [ex, ey] = arc(angle);
  const large = pct > 0.5 ? 1 : 0;

  return (
    <div style={{ textAlign: "center" }}>
      <svg width={size} height={size * 0.75} style={{ overflow: "visible" }}>
        {/* track */}
        <path
          d={`M ${arc(-140).join(" ")} A ${r} ${r} 0 1 1 ${arc(140).join(" ")}`}
          fill="none" stroke="#1e3a5f" strokeWidth={6} strokeLinecap="round"
        />
        {/* fill */}
        {pct > 0 && (
          <path
            d={`M ${sx} ${sy} A ${r} ${r} 0 ${large} 1 ${ex} ${ey}`}
            fill="none" stroke={color} strokeWidth={6} strokeLinecap="round"
          />
        )}
        {/* needle */}
        <line
          x1={cx} y1={cy}
          x2={cx + (r - 10) * Math.cos(((angle - 90) * Math.PI) / 180)}
          y2={cy + (r - 10) * Math.sin(((angle - 90) * Math.PI) / 180)}
          stroke={color} strokeWidth={2} strokeLinecap="round"
        />
        <circle cx={cx} cy={cy} r={4} fill={color} />
      </svg>
      <div style={{ fontSize: 18, fontWeight: 700, color, fontFamily: "monospace", marginTop: -8 }}>
        {typeof value === "number" ? value.toFixed(unit === "π" ? 7 : 0) : value}
        <span style={{ fontSize: 10, color: "#64748b", marginLeft: 2 }}>{unit}</span>
      </div>
      <div style={{ fontSize: 9, color: "#475569", letterSpacing: "0.1em" }}>{label}</div>
    </div>
  );
}

// ── stage row ─────────────────────────────────────────────────────────────────
function StageRow({ s, blueprintRPM }) {
  const drift = s.accumulatedDeviation;
  const isOver = drift > 0;
  return (
    <div style={{
      display: "grid", gridTemplateColumns: "32px 1fr 90px 90px 80px",
      alignItems: "center", gap: 8, padding: "5px 10px",
      borderBottom: "1px solid #0d2137",
      background: s.stage % 2 === 0 ? "#061220" : "transparent",
    }}>
      <div style={{ fontSize: 10, color: "#334155", fontFamily: "monospace" }}>#{s.stage}</div>
      {/* deviation bar */}
      <div style={{ position: "relative", height: 6, background: "#0f2035", borderRadius: 3 }}>
        <div style={{
          position: "absolute",
          left: isOver ? "50%" : `${50 + (drift / 50) * 50}%`,
          width: `${Math.abs(drift / 50) * 50}%`,
          height: "100%",
          background: Math.abs(drift) > 30 ? "#ef4444" : Math.abs(drift) > 15 ? "#f59e0b" : "#10b981",
          borderRadius: 3,
        }} />
        <div style={{ position: "absolute", left: "50%", top: -1, width: 1, height: 8, background: "#334155" }} />
      </div>
      <div style={{ fontSize: 10, fontFamily: "monospace", color: isOver ? "#f87171" : "#34d399", textAlign: "right" }}>
        {s.stageDeviation > 0 ? "+" : ""}{s.stageDeviation.toFixed(2)} rpm
      </div>
      <div style={{ fontSize: 10, fontFamily: "monospace", color: "#94a3b8", textAlign: "right" }}>
        Σ {drift > 0 ? "+" : ""}{drift.toFixed(2)}
      </div>
      <div style={{ fontSize: 9, color: "#10b981", textAlign: "right", letterSpacing: "0.06em" }}>✓ SIGNED</div>
    </div>
  );
}

// ── main ──────────────────────────────────────────────────────────────────────
export default function TordialMotor() {
  const [stages, setStages] = useState(6);
  const [tolPerStage, setTolPerStage] = useState(8);
  const [noiseFactor, setNoiseFactor] = useState(12);
  const [stack, setStack] = useState([]);
  const [signal, setSignal] = useState({ blueprint: [], real: [], jitter: [] });
  const [running, setRunning] = useState(false);
  const animRef = useRef();
  const tickRef = useRef(0);

  const regenerate = useCallback(() => {
    const s = buildToleranceStack(stages, tolPerStage, noiseFactor);
    setStack(s);
    const last = s[s.length - 1];
    setSignal(generateSignal(320, last.effectiveRPM, noiseFactor));
  }, [stages, tolPerStage, noiseFactor]);

  useEffect(() => { regenerate(); }, [regenerate]);

  // live tick when running
  useEffect(() => {
    if (!running) { cancelAnimationFrame(animRef.current); return; }
    const tick = () => {
      tickRef.current++;
      if (tickRef.current % 18 === 0) regenerate();
      animRef.current = requestAnimationFrame(tick);
    };
    animRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animRef.current);
  }, [running, regenerate]);

  const last = stack[stack.length - 1] || {};
  const effectiveRPM = last.effectiveRPM || BLUEPRINT_RPM;
  const effectivePi = last.effectivePi || BLUEPRINT_PI;
  const drift = effectiveRPM - BLUEPRINT_RPM;
  const piDrift = effectivePi - BLUEPRINT_PI;
  const driftColor = Math.abs(drift) > 20 ? "#ef4444" : Math.abs(drift) > 8 ? "#f59e0b" : "#10b981";

  return (
    <div style={{ minHeight: "100vh", background: "#020c1b", color: "#e2e8f0", fontFamily: "'DM Mono', 'Courier New', monospace" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Barlow+Condensed:wght@600;700;800&display=swap');
        * { box-sizing: border-box; }
        input[type=range] { -webkit-appearance: none; height: 4px; border-radius: 2px; background: #1e3a5f; outline: none; width: 100%; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; width: 14px; height: 14px; border-radius: 50%; background: #0ea5e9; cursor: pointer; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
        @keyframes fade-in { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
        .fade { animation: fade-in 0.3s ease; }
      `}</style>

      {/* header */}
      <div style={{ padding: "16px 24px", borderBottom: "1px solid #0d2137", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ fontFamily: "'Barlow Condensed', sans-serif", fontSize: 26, fontWeight: 800, letterSpacing: "0.04em", color: "#f1f5f9" }}>
            TORDIAL <span style={{ color: "#0ea5e9" }}>//</span> BLDC TOLERANCE TRACKER
          </div>
          <div style={{ fontSize: 10, color: "#334155", letterSpacing: "0.12em" }}>
            BLUEPRINT π = {BLUEPRINT_PI} · TARGET RPM = {BLUEPRINT_RPM} · STAGES ACCEPTED
          </div>
        </div>
        <button onClick={() => setRunning(v => !v)} style={{
          background: running ? "#ef444422" : "#0ea5e922",
          border: `1px solid ${running ? "#ef4444" : "#0ea5e9"}`,
          color: running ? "#f87171" : "#38bdf8",
          padding: "8px 18px", borderRadius: 6, cursor: "pointer",
          fontFamily: "'DM Mono', monospace", fontSize: 12, letterSpacing: "0.08em",
        }}>
          {running ? "■ STOP" : "▶ RUN LIVE"}
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 0, minHeight: "calc(100vh - 61px)" }}>

        {/* left: main content */}
        <div style={{ padding: 20, borderRight: "1px solid #0d2137" }}>

          {/* gauges */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 20 }}>
            <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, padding: 16, textAlign: "center" }}>
              <Gauge value={effectiveRPM} min={BLUEPRINT_RPM - 60} max={BLUEPRINT_RPM + 60} label="EFFECTIVE RPM" unit="rpm" color={driftColor} />
            </div>
            <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, padding: 16, textAlign: "center" }}>
              <Gauge value={effectivePi} min={3.135} max={3.155} label="EFFECTIVE π" unit="π" color="#8b5cf6" />
            </div>
            <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, padding: 16 }}>
              <div style={{ fontSize: 9, color: "#475569", letterSpacing: "0.1em", marginBottom: 8 }}>RPM DRIFT</div>
              <div style={{ fontSize: 28, fontWeight: 700, color: driftColor, fontFamily: "'Barlow Condensed', sans-serif" }}>
                {drift >= 0 ? "+" : ""}{drift.toFixed(2)}
              </div>
              <div style={{ fontSize: 9, color: "#334155" }}>from blueprint</div>
              <div style={{ marginTop: 10, fontSize: 9, color: "#475569", letterSpacing: "0.1em" }}>π DRIFT</div>
              <div style={{ fontSize: 18, fontWeight: 700, color: "#8b5cf6" }}>
                {piDrift >= 0 ? "+" : ""}{piDrift.toFixed(7)}
              </div>
            </div>
            <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, padding: 16 }}>
              <div style={{ fontSize: 9, color: "#475569", letterSpacing: "0.1em", marginBottom: 6 }}>NULL POINT</div>
              <div style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>
                Where is π when running?
              </div>
              <div style={{ fontSize: 13, color: "#f59e0b", fontWeight: 600 }}>
                {effectivePi.toFixed(7)}
              </div>
              <div style={{ fontSize: 9, color: "#334155", marginTop: 4 }}>vs blueprint {BLUEPRINT_PI}</div>
              <div style={{ marginTop: 10, padding: "4px 8px", background: Math.abs(piDrift) < 0.0002 ? "#10b98122" : "#f59e0b22", borderRadius: 4, fontSize: 9, color: Math.abs(piDrift) < 0.0002 ? "#10b981" : "#f59e0b", textAlign: "center", letterSpacing: "0.06em" }}>
                {Math.abs(piDrift) < 0.0002 ? "NEAR BLUEPRINT" : "OPERATIONAL DRIFT DETECTED"}
              </div>
            </div>
          </div>

          {/* signals */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 20 }}>
            <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, padding: 14 }}>
              <div style={{ fontSize: 9, color: "#475569", letterSpacing: "0.1em", marginBottom: 8 }}>RPM SIGNAL — BLUEPRINT vs ACTUAL</div>
              <div style={{ position: "relative" }}>
                <MiniChart data={signal.blueprint} color="#334155" height={70} />
                <div style={{ position: "absolute", top: 0, left: 0, right: 0 }}>
                  <MiniChart data={signal.real} color="#0ea5e9" height={70} />
                </div>
              </div>
              <div style={{ display: "flex", gap: 12, marginTop: 6 }}>
                <span style={{ fontSize: 9, color: "#334155" }}>▬ blueprint</span>
                <span style={{ fontSize: 9, color: "#0ea5e9" }}>▬ actual</span>
              </div>
            </div>
            <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, padding: 14 }}>
              <div style={{ fontSize: 9, color: "#475569", letterSpacing: "0.1em", marginBottom: 8 }}>
                JITTER VISIBILITY — noise floor: {noiseFactor} rpm
              </div>
              <MiniChart data={signal.jitter} color="#f59e0b" height={70} fill />
              <div style={{ fontSize: 9, color: "#64748b", marginTop: 6 }}>
                Lower noise floor → jitter shows more abruptly
              </div>
            </div>
          </div>

          {/* tolerance stack table */}
          <div style={{ background: "#0a1628", border: "1px solid #0d2137", borderRadius: 10, overflow: "hidden" }}>
            <div style={{ padding: "10px 10px", borderBottom: "1px solid #0d2137", display: "grid", gridTemplateColumns: "32px 1fr 90px 90px 80px", gap: 8 }}>
              {["STAGE", "DEVIATION BAR", "STAGE Δ", "ΣACCUM.", "STATUS"].map(h => (
                <div key={h} style={{ fontSize: 9, color: "#334155", letterSpacing: "0.08em" }}>{h}</div>
              ))}
            </div>
            <div className="fade" key={stack.map(s=>s.stageDeviation).join()}>
              {stack.map(s => <StageRow key={s.stage} s={s} blueprintRPM={BLUEPRINT_RPM} />)}
            </div>
            <div style={{ padding: "10px 10px", borderTop: "1px solid #0d2137", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 10, color: "#475569" }}>All stages signed off. Compound drift = {drift.toFixed(2)} rpm</span>
              <span style={{ fontSize: 10, color: driftColor, letterSpacing: "0.06em" }}>
                EFFECTIVE π = {effectivePi.toFixed(7)}
              </span>
            </div>
          </div>

        </div>

        {/* right: controls */}
        <div style={{ padding: 20 }}>
          <div style={{ fontSize: 10, color: "#334155", letterSpacing: "0.12em", marginBottom: 16 }}>SYSTEM PARAMETERS</div>

          {[
            { label: "INSPECTION STAGES", value: stages, min: 2, max: 12, step: 1, set: setStages, unit: "stages", color: "#0ea5e9" },
            { label: "TOLERANCE PER STAGE", value: tolPerStage, min: 1, max: 30, step: 0.5, set: setTolPerStage, unit: "rpm", color: "#f59e0b" },
            { label: "NOISE FLOOR", value: noiseFactor, min: 0.5, max: 40, step: 0.5, set: setNoiseFactor, unit: "rpm", color: "#8b5cf6" },
          ].map(({ label, value, min, max, step, set, unit, color }) => (
            <div key={label} style={{ marginBottom: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ fontSize: 9, color: "#475569", letterSpacing: "0.1em" }}>{label}</span>
                <span style={{ fontSize: 12, color, fontWeight: 600 }}>{value} {unit}</span>
              </div>
              <input type="range" min={min} max={max} step={step} value={value}
                onChange={e => set(Number(e.target.value))}
                style={{ accentColor: color }} />
            </div>
          ))}

          <button onClick={regenerate} style={{
            width: "100%", background: "#0ea5e915", border: "1px solid #0ea5e944",
            color: "#38bdf8", padding: "10px", borderRadius: 6, cursor: "pointer",
            fontFamily: "'DM Mono', monospace", fontSize: 12, letterSpacing: "0.08em",
            marginBottom: 20,
          }}>
            ↻ NEW SAMPLE
          </button>

          {/* explainer */}
          <div style={{ fontSize: 10, color: "#334155", lineHeight: 1.7, borderTop: "1px solid #0d2137", paddingTop: 16 }}>
            <div style={{ color: "#475569", marginBottom: 8, letterSpacing: "0.08em" }}>TORDIAL PRINCIPLE</div>
            <p style={{ margin: "0 0 8px" }}>
              Each inspection stage accepts a deviation within tolerance and signs off. Individually acceptable. But they <span style={{ color: "#f59e0b" }}>compound</span>.
            </p>
            <p style={{ margin: "0 0 8px" }}>
              The motor doesn't run at blueprint π. It runs at the <span style={{ color: "#8b5cf6" }}>effective π</span> produced by every stage that said "good enough."
            </p>
            <p style={{ margin: "0 0 8px" }}>
              The <span style={{ color: "#f59e0b" }}>null point</span> is where π actually lives during operation. Track it. That's your real build state.
            </p>
            <p style={{ margin: 0, color: "#1e3a5f" }}>
              Lower the noise floor → jitter from drift becomes visible. That's the signal you build toward.
            </p>
          </div>

          {/* optimal state readout */}
          <div style={{ marginTop: 16, background: "#0a1628", border: `1px solid ${driftColor}44`, borderRadius: 8, padding: 14 }}>
            <div style={{ fontSize: 9, color: "#475569", letterSpacing: "0.1em", marginBottom: 8 }}>OPTIMAL BUILD STATE</div>
            <div style={{ fontSize: 11, color: "#94a3b8", marginBottom: 4 }}>If you manufactured to this run:</div>
            <div style={{ fontSize: 13, color: driftColor, fontWeight: 600 }}>
              Target RPM: {effectiveRPM.toFixed(1)}
            </div>
            <div style={{ fontSize: 13, color: "#8b5cf6", fontWeight: 600 }}>
              Target π: {effectivePi.toFixed(7)}
            </div>
            <div style={{ fontSize: 9, color: "#334155", marginTop: 6 }}>
              Drift eliminated at source. Heatsink shrinks.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}