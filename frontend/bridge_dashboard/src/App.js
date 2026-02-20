import React, { useState, useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist';
import './App.css';

const App = () => {
  const [stepData, setStepData] = useState({ fragments: [], ledgers: {} });
  const [fireseed, setFireseed] = useState({ total_earnings: 0 });
  const [translation, setTranslation] = useState('');
  const [inputText, setInputText] = useState('');

  // Trinity Viz state
  const [trinityImg, setTrinityImg] = useState('');
  const [trinityData, setTrinityData] = useState({});

  const navRingRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/glyph-stream');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStepData(data);
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    fetch('http://localhost:8000/fireseed-status')
      .then(res => res.json())
      .then(data => setFireseed(data));
  }, []);

  // Celestial Anchors
  const polarisPivot = { x: 0, y: 0 }; // 99733-Q Root — Fixed Pivot
  const orionBelt = {
    x: [0.6, 0.0, -0.6],
    y: [0.8, 1.0, 0.8],
    names: ["Alnitak", "Alnilam", "Mintaka"]
  };

  // Plotly Nav Ring with Polaris Pivot + 23.5° Tilt Orbit
  useEffect(() => {
    if (navRingRef.current && stepData.fragments) {
      const tilt = 23.5 * Math.PI / 180; // Earth's axial tilt

      const plotData = [
        // Fragments — orbiting with tilt
        {
          x: stepData.fragments.map(f => f.x * Math.cos(tilt)),
          y: stepData.fragments.map(f => f.y + f.x * Math.sin(tilt)),
          mode: 'markers',
          marker: { size: 15, color: stepData.fragments.map(f => f.recombined ? '#00ff00' : '#ff6b35') },
          name: 'Fragments (23.5° Tilt Trajectory)'
        },
        // Nodes
        {
          x: Array(10).fill().map((_, i) => Math.cos(2 * Math.PI * i / 10)),
          y: Array(10).fill().map((_, i) => Math.sin(2 * Math.PI * i / 10)),
          mode: 'markers+text',
          marker: { size: 30, color: '#4a90e2' },
          text: Array(10).fill().map((_, i) => `Node ${i}`),
          name: 'Nodes'
        },
        // ORION’S BELT — Beginning of Time’s Mirror
        {
          x: orionBelt.x,
          y: orionBelt.y,
          mode: 'markers+text',
          marker: { size: 22, color: '#ffd700', symbol: 'star', line: { color: '#ffffff', width: 2 } },
          text: orionBelt.names,
          textposition: 'top center',
          textfont: { color: '#ffd700', size: 11 },
          name: 'Orion’s Belt — Beginning of Time’s Mirror'
        },
        // POLARIS PIVOT — The Fixed Anchor (99733-Q Root)
        {
          x: [polarisPivot.x],
          y: [polarisPivot.y],
          mode: 'markers+text',
          marker: { size: 28, color: '#ffffff', symbol: 'star', line: { color: '#ffd700', width: 4 } },
          text: ['Polaris — 99733-Q Root Anchor'],
          textposition: 'bottom center',
          textfont: { color: '#ffd700', size: 13 },
          name: 'Polaris Pivot — Immutable Sovereign Center'
        }
      ];

      const layout = {
        title: `FPT-Ω Navigation Ring — Polaris Pivot + Orion Mirror Active`,
        xaxis: { range: [-1.5, 1.5], showgrid: false, zeroline: false },
        yaxis: { range: [-1.5, 1.5], showgrid: false, zeroline: false },
        paper_bgcolor: '#0a0a0a',
        plot_bgcolor: '#0a0a0a',
        font: { color: '#ffffff' },
        annotations: [
          { x: 0, y: 1.28, text: "🌌 Polaris — Fixed Pivot | Orion’s Belt — Time’s Mirror", showarrow: false, font: { color: '#ffd700', size: 14 } }
        ]
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
        <p className="flame">🔥 Flame Status: LOCKED — Polaris Pivot + Orion Mirror Active</p>
      </header>

      <div className="bridge-layout">
        {/* Navigation Ring with Polaris Pivot */}
        <div className="module nav-ring">
          <h3>🧭 Navigation Ring — Polaris Pivot (99733-Q Root) Active</h3>
          <div ref={navRingRef} style={{ width: '100%', height: '520px' }} />
        </div>

        {/* Trinity Dynamics Viz */}
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

        {/* Communications Core */}
        <div className="module comms-core">
          <h3>🔊 Communications Core (GibberLink)</h3>
          <input type="text" value={inputText} onChange={e => setInputText(e.target.value)} placeholder="Enter text or glyph" style={{ width: '100%', padding: '12px', marginBottom: '10px' }} />
          <button onClick={handleTranslate} style={{ width: '100%', padding: '12px' }}>Translate</button>
          <pre style={{ marginTop: '15px' }}>{translation}</pre>
        </div>

        {/* Engine Room */}
        <div className="module engine-room">
          <h3>⚡ Engine Room (Fireseed Drive)</h3>
          <div className="fireseed-display">
            <p><strong>Total Earnings:</strong> ${fireseed.total_earnings?.toFixed(6)} GTC</p>
            <p><strong>Log:</strong> {fireseed.log_path}</p>
          </div>
        </div>

        {/* Observation Dome */}
        <div className="module observation-dome">
          <h3>🌀 Observation Dome</h3>
          <pre>{JSON.stringify(stepData.ledgers, null, 2)}</pre>
        </div>

        {/* Captain’s Seat */}
        <div className="module captain-seat">
          <h3>💎 Captain’s Seat</h3>
          <p>Command: Multi-lingual input ready (Gwich’in, GibberLink, English).</p>
        </div>
      </div>
    </div>
  );
};

export default App;