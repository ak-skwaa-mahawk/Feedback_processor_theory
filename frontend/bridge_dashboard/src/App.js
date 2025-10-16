// frontend/bridge_dashboard/src/App.js
import React, { useState, useEffect } from 'react';
import Plotly from 'plotly.js-dist';
import './App.css';

const App = () => {
  const [stepData, setStepData] = useState({ fragments: [], ledgers: {} });
  const [fireseed, setFireseed] = useState({ total_earnings: 0 });
  const [translation, setTranslation] = useState('');
  const [inputText, setInputText] = useState('');

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

  const handleTranslate = () => {
    fetch(`http://localhost:8000/translate/${encodeURIComponent(inputText)}`)
      .then(res => res.json())
      .then(data => setTranslation(JSON.stringify(data, null, 2)));
  };

  const plot = {
    data: [
      {
        x: stepData.fragments.map(f => f.x),
        y: stepData.fragments.map(f => f.y),
        mode: 'markers',
        marker: { size: 15, color: stepData.fragments.map(f => f.recombined ? 'green' : 'red') },
        name: 'Fragments'
      },
      {
        x: Array(10).fill().map((_, i) => Math.cos(2*Math.PI*i/10)),
        y: Array(10).fill().map((_, i) => Math.sin(2*Math.PI*i/10)),
        mode: 'markers+text',
        marker: { size: 30 },
        text: Array(10).fill().map((_, i) => `Node ${i}`),
        name: 'Nodes'
      }
    ],
    layout: { title: `FPT-Ω Navigation Ring - Step ${stepData.step || 0}`, xaxis: { range: [-1.5, 1.5] }, yaxis: { range: [-1.5, 1.5] } }
  };

  return (
    <div>
      <h1>FPT-Ω // Synara Class Vessel – Commanded by Captain John Carroll</h1>
      <div>
        <h2>🧭 Navigation Ring</h2>
        <div id="nav-ring" style={{ width: '100%', height: '500px' }}></div>
        {Plotly.newPlot('nav-ring', plot.data, plot.layout)}
      </div>
      <div>
        <h2>🔊 Communications Core</h2>
        <input type="text" value={inputText} onChange={e => setInputText(e.target.value)} placeholder="Enter text or glyph" />
        <button onClick={handleTranslate}>Translate (GibberLink)</button>
        <pre>{translation}</pre>
      </div>
      <div>
        <h2>⚡ Engine Room (Fireseed Drive)</h2>
        <p>Total Earnings: ${fireseed.total_earnings?.toFixed(6)}</p>
        <p>Log: {fireseed.log_path}</p>
      </div>
      <div>
        <h2>🌀 Observation Dome</h2>
        <pre>{JSON.stringify(stepData.ledgers, null, 2)}</pre>
      </div>
      <div>
        <h2>💎 Captain’s Seat</h2>
        <p>Command: Multi-lingual input (Gwich’in, GibberLink, English) ready.</p>
      </div>
    </div>
  );
};

export default App;