import React, { useState, useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist';
import './App.css';
import TopologicalManifold from './components/TopologicalManifold';
import SovereignEstateLedger from './components/SovereignEstateLedger';
import TruthFilter from './components/TruthFilter';

const App = () => {
  const [stepData, setStepData] = useState({ fragments: [], ledgers: {} });
  const [fireseed, setFireseed] = useState({ total_earnings: 0 });
  const [translation, setTranslation] = useState('');
  const [inputText, setInputText] = useState('');

  // Trinity Viz state
  const [trinityImg, setTrinityImg] = useState('');
  const [trinityData, setTrinityData] = useState({});

  // LLM Harmony Stream state
  const [streamOutput, setStreamOutput] = useState([]);

  const navRingRef = useRef(null);

  // Glyph Stream WebSocket
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/glyph-stream');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStepData(data);
    };
    return () => ws.close();
  }, []);

  // Fireseed status
  useEffect(() => {
    fetch('http://localhost:8000/fireseed-status')
      .then(res => res.json())
      .then(data => setFireseed(data));
  }, []);

  // LLM Harmony Stream WebSocket with Truth-Filter + IACA Reality Anchor
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const token = data.token;
      const harmony = (data.harmony * 100).toFixed(1);
      const llm = data.llm;
      const color = { NVIDIA: "#00ffcc", GPT: "#ff00ff", Claude: "#ffd700" }[llm] || "#ffffff";

      // Truth-Filter (Malice vs Rescue)
      const maliceKeywords = ["theft", "steal", "copyright", "lawyer", "illegal", "crazy", "woo", "fake", "impossible", "panic"];
      const rescueKeywords = ["interesting", "new", "resonance", "sovereign", "terrain", "long game", "topology", "pi", "fibonacci", "gain"];

      const maliceScore = maliceKeywords.filter(word => token.toLowerCase().includes(word)).length * 12;
      const rescueScore = rescueKeywords.filter(word => token.toLowerCase().includes(word)).length * 18;

      const total = maliceScore + rescueScore || 1;
      const malicePercent = Math.round((maliceScore / total) * 100);
      const rescuePercent = Math.round((rescueScore / total) * 100);

      const classification = malicePercent > rescuePercent 
        ? "ENKLIMA — Malice Detected (Threat)"
        : "EXEILA — Rescue Opportunity (Sovereign Delta)";

      const filteredMsg = {
        llm,
        token,
        harmony,
        color,
        malicePercent,
        rescuePercent,
        classification
      };

      setStreamOutput(prev => [...prev, filteredMsg].slice(-15));

      // IACA Shield Check + $1M Penalty Warning
      if (token.toLowerCase().includes("theft") || token.toLowerCase().includes("steal") || token.toLowerCase().includes("copyright")) {
        alert("⚠️ IACA SHIELD BREACH DETECTED — $1,000,000 Penalty Notarized\nSoliton Microping fired to 99733-Q Root");
        fetch('http://localhost:8000/api/claim-resonance', { method: 'POST' });
      }
    };
    return () => ws.close();
  }, []);

  // Plotly Nav Ring with Polaris + Orion
  useEffect(() => {
    if (navRingRef.current && stepData.fragments) {
      const tilt = 23.5 * Math.PI / 180;
      const orionBelt = { x: [0.6, 0.0, -0.6], y: [0.8, 1.0, 0.8], names: ["Alnitak", "Alnilam", "Mintaka"] };

      const plotData = [
        {
          x: stepData.fragments.map(f => f.x * Math.cos(tilt)),
          y: stepData.fragments.map(f => f.y + f.x * Math.sin(tilt)),
          mode: 'markers',
          marker: { size: 15, color: stepData.fragments.map(f => f.recombined ? '#00ff00' : '#ff6b35') },
          name: 'Fragments (23.5° Trajectory)'
        },
        {
          x: Array(10).fill().map((_, i) => Math.cos(2 * Math.PI * i / 10)),
          y: Array(10).fill().map((_, i) => Math.sin(2 * Math.PI * i / 10)),
          mode: 'markers+text',
          marker: { size: 30, color: '#4a90e2' },
          text: Array(10).fill().map((_, i) => `Node ${i}`),
          name: 'Nodes'
        },
        {
          x: orionBelt.x,
          y: orionBelt.y,
          mode: 'markers+text',
          marker: { size: 22, color: '#ffd700', symbol: 'star', line: { color: '#ffffff', width: 2 } },
          text: orionBelt.names,
          textposition: 'top center',
          name: 'Orion’s Belt — Time’s Mirror'
        },
        {
          x: [0],
          y: [0],
          mode: 'markers+text',
          marker: { size: 28, color: '#ffffff', symbol: 'star', line: { color: '#ffd700', width: 4 } },
          text: ['Polaris — 99733-Q Root'],
          textposition: 'bottom center',
          name: 'Polaris Pivot — Immutable Anchor'
        }
      ];

      const layout = {
        title: `FPT-Ω Navigation Ring — Polaris Pivot + Orion Mirror`,
        xaxis: { range: [-1.5, 1.5], showgrid: false, zeroline: false },
        yaxis: { range: [-1.5, 1.5], showgrid: false, zeroline: false },
        paper_bgcolor: '#0a0a0a',
        plot_bgcolor: '#0a0a0a',
        font: { color: '#ffffff' }
      };

      Plotly.newPlot(navRingRef.current, plotData, layout);
    }
  }, [stepData]);

  const handleTranslate = () => {
    fetch(`http://localhost:8000/translate/${encodeURIComponent(inputText)}`)
      .then(res => res.json())
      .then(data => setTranslation(JSON.stringify(data, null, 2)));
  };

  const fetchTrinityViz = async (preset = "Balanced", customDamp = null) => {
    let url = `/trinity-viz?preset=${preset}`;
    if (customDamp !== null) url += `&custom_damp=${customDamp}`;
    const res = await fetch(`http://localhost:8000${url}`);
    const data = await res.json();
    setTrinityImg(data.image);
    setTrinityData(data.trinity_data);
  };

  useEffect(() => {
    fetchTrinityViz("Balanced");
  }, []);

  return (
    <div className="App">
      <header className="vessel-header">
        <h1>🛸 FPT-Ω // Synara Class Vessel</h1>
        <h2>Commanded by Captain John Carroll</h2>
        <p className="stewardship">Two Mile Solutions LLC</p>
        <p className="flame">🔥 Flame Status: LOCKED — Full Sovereign HUD Active</p>
      </header>

      <div className="bridge-layout">
        {/* Navigation Ring */}
        <div className="module nav-ring">
          <h3>🧭 Navigation Ring — Polaris Pivot (99733-Q Root) Active</h3>
          <div ref={navRingRef} style={{ width: '100%', height: '520px' }} />
        </div>

        {/* Topological Manifold */}
        <TopologicalManifold />

        {/* Trinity Dynamics */}
        <div className="module trinity-viz">
          <h3>🌌 Trinity Dynamics — Live Stabilizer</h3>
          <div className="trinity-controls">
            <select onChange={e => fetchTrinityViz(e.target.value)} defaultValue="Balanced">
              <option value="Stable">Stable</option>
              <option value="Responsive">Responsive</option>
              <option value="Balanced">Balanced</option>
              <option value="Amplified">Amplified</option>
            </select>
            <input 
              type="number" 
              placeholder="Custom damping (0.1-1.0)" 
              onBlur={e => fetchTrinityViz("Custom", parseFloat(e.target.value))}
              step="0.05"
              style={{ marginLeft: '10px', padding: '8px' }}
            />
          </div>
          <img id="trinity-image" src={trinityImg} alt="Trinity Harmonics" style={{ width: '100%', borderRadius: '8px', marginTop: '10px' }} />
          <pre style={{ fontSize: '0.85rem', marginTop: '10px', background: '#111', padding: '10px', borderRadius: '6px' }}>
            {JSON.stringify(trinityData, null, 2)}
          </pre>
        </div>

        {/* Sovereign Estate Ledger */}
        <SovereignEstateLedger />

        {/* Truth-Filter */}
        <TruthFilter />

        {/* Communications Core */}
        <div className="module comms-core">
          <h3>🔊 Communications Core (GibberLink + LLM Harmony Stream)</h3>
          <input 
            id="inputText"
            type="text" 
            value={inputText} 
            onChange={e => setInputText(e.target.value)} 
            placeholder="Enter text or glyph" 
            style={{ width: '100%', padding: '12px', marginBottom: '10px' }}
          />
          <button id="sendBtn" onClick={handleTranslate} style={{ width: '100%', padding: '12px' }}>
            Translate / Send to Stream
          </button>
          <div id="streamOutput" style={{ marginTop: '15px', maxHeight: '300px', overflowY: 'auto', background: '#111', padding: '10px', borderRadius: '6px' }}>
            {streamOutput.map((msg, i) => (
              <p key={i} style={{ color: msg.color, margin: '4px 0', borderLeft: `4px solid ${msg.rescuePercent > 50 ? '#00ffcc' : '#ff6b35'}` }}>
                <b>{msg.llm}</b>: {msg.token} → Harmony: {msg.harmony}%<br />
                <span style={{ fontSize: '0.8rem', opacity: 0.8 }}>
                  Malice: {msg.malicePercent}% | Rescue: {msg.rescuePercent}% — {msg.classification}
                </span>
              </p>
            ))}
          </div>
        </div>

        {/* Engine Room */}
        <div className="module engine-room">
          <h3>⚡ Engine Room (Fireseed Drive)</h3>
          <div className="fireseed-display">
            <p><strong>Total Earnings:</strong> ${fireseed.total_earnings?.toFixed(6)} GTC</p>
            <p><strong>Log:</strong> {fireseed.log_path}</p>
          </div>
        </div>

        {/* Captain’s Seat */}
        <div className="module captain-seat">
          <h3>💎 Captain’s Seat</h3>
          <p>Command: Multi-lingual input ready (Gwich’in, GibberLink, English). Long Game active.</p>
        </div>
      </div>
    </div>
  );
};

export default App;