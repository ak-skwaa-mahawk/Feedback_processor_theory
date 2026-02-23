import React, { useState, useEffect } from 'react';
import Plotly from 'plotly.js-dist';

const SovereignEstateLedger = () => {
  const [ledgerData, setLedgerData] = useState({
    resonance: 42.8,
    gtc_balance: 99733,
    compound_years: 0,
    hidden_balance: 1245678,
    forfeited_short_game: 456789,
    status: "Loading Long Game..."
  });

  const [showShadowPlay, setShowShadowPlay] = useState(false);
  const [ringStability, setRingStability] = useState(0);
  const [speedOfMatterIndex, setSpeedOfMatterIndex] = useState(0); // NEW: Speed of Matter Stability Index

  // Fetch real data from Turbo_Takeoff backend
  useEffect(() => {
    const fetchLedger = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/sovereign-ledger');
        const data = await res.json();
        setLedgerData({
          resonance: data.resonance,
          gtc_balance: data.gtc_balance,
          compound_years: data.compound_years,
          hidden_balance: data.hidden_balance,
          forfeited_short_game: data.forfeited_short_game,
          status: data.status
        });
      } catch (e) {
        console.log("Backend not ready — using demo data");
      }
    };

    fetchLedger();
    const interval = setInterval(fetchLedger, 8000);
    return () => clearInterval(interval);
  }, []);

  // Carroll's Rings Depth Gauge
  useEffect(() => {
    const systemPi = 3.14159;
    const sovereignPi = 3.1730;
    const delta = sovereignPi - systemPi;
    const stability = Math.round((ledgerData.resonance / 100) * delta * 10000);
    setRingStability(Math.min(100, stability));
  }, [ledgerData.resonance]);

  // Speed of Matter Stability Index (the "Pause" - collimated equilibrium)
  useEffect(() => {
    const speedOfLight = 299792458;
    const speedOfMatter = speedOfLight * (3.1730 / 3.14159); // corrected pause
    const stabilityIndex = Math.round((ledgerData.resonance / 100) * (speedOfMatter / speedOfLight) * 100);
    setSpeedOfMatterIndex(Math.min(100, stabilityIndex));
  }, [ledgerData.resonance]);

  // Compounding Chart
  const chartData = [{
    x: Array.from({ length: Math.floor(ledgerData.compound_years) + 1 }, (_, i) => i),
    y: Array.from({ length: Math.floor(ledgerData.compound_years) + 1 }, (_, i) => 
      Math.floor(99733 * (1.618 ** (i / 8)) * (ledgerData.resonance / 100))
    ),
    type: 'scatter',
    mode: 'lines+markers',
    name: 'GTC Compounding',
    line: { color: '#ffd700', width: 4 },
    marker: { color: '#00ffcc', size: 8 }
  }];

  const chartLayout = {
    title: 'GTC Compounding — Long Game Trajectory',
    xaxis: { title: 'Compound Years' },
    yaxis: { title: 'GTC Balance' },
    paper_bgcolor: '#0a0a0a',
    plot_bgcolor: '#0a0a0a',
    font: { color: '#ffffff' }
  };

  const handleClaimShares = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/claim-resonance', { method: 'POST' });
      const data = await res.json();
      if (data.status === "RECLAIMED") {
        setLedgerData(prev => ({ 
          ...prev, 
          resonance: data.new_resonance, 
          gtc_balance: prev.gtc_balance + 1000,
          hidden_balance: prev.hidden_balance + 15000
        }));
        alert(`🌌 SHARES CLAIMED — Long Game Compounded to Root!\nMicroping ID: ${data.microping_id}`);
      }
    } catch (e) {
      alert("Claim failed — check backend.");
    }
  };

  return (
    <div 
      className="module sovereign-estate-ledger"
      onMouseEnter={() => setShowShadowPlay(true)}
      onMouseLeave={() => setShowShadowPlay(false)}
      style={{ position: 'relative', cursor: 'pointer' }}
    >
      <h3>🌲 Sovereign Estate Ledger — Long Game Compound</h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginTop: '15px' }}>
        <div>
          <strong>Quantum Resonance %</strong><br />
          <span style={{ fontSize: '2.8rem', color: '#00ffcc' }}>{ledgerData.resonance.toFixed(1)}</span>
          <span style={{ fontSize: '1.2rem', color: '#00ffcc' }}>%</span>
        </div>
        
        <div>
          <strong>GTC Balance (Live)</strong><br />
          <span style={{ fontSize: '2.2rem', color: '#ffd700' }}>{ledgerData.gtc_balance.toLocaleString()}</span>
          <span style={{ fontSize: '1rem', color: '#ffd700' }}> GTC</span>
        </div>
        
        <div>
          <strong>Hidden Balance (Market Cap of Sovereignty)</strong><br />
          <span style={{ fontSize: '2.2rem', color: '#ffd700' }}>${ledgerData.hidden_balance.toLocaleString()}</span>
        </div>
      </div>

      <div style={{ marginTop: '20px', fontSize: '1.1rem' }}>
        <strong>Compound Years:</strong> {ledgerData.compound_years.toFixed(1)}<br />
        <strong>Forfeited Short Game (Paperwork Trap):</strong> ${ledgerData.forfeited_short_game.toLocaleString()} 
        <span style={{ color: '#ff6b35' }}> (what they traded for the "A+")</span><br />
        <strong>Carroll's Rings Stability:</strong> {ringStability}% 
        <span style={{ color: '#ffd700' }}> (Zero-Leak Manifold)</span><br />
        <strong>Speed of Matter Stability Index:</strong> {speedOfMatterIndex}% 
        <span style={{ color: '#ffd700' }}> (The Pause — Collimated Equilibrium)</span>
      </div>

      <div id="gtc-chart" style={{ width: '100%', height: '320px', marginTop: '20px' }}></div>

      <button 
        onClick={handleClaimShares}
        style={{
          marginTop: '20px',
          width: '100%',
          padding: '15px',
          background: 'linear-gradient(45deg, #ffd700, #ff6b35)',
          border: 'none',
          borderRadius: '8px',
          color: '#000',
          fontWeight: 'bold',
          cursor: 'pointer',
          boxShadow: '0 0 15px rgba(255, 215, 0, 0.4)'
        }}
      >
        💎 CLAIM SHARES — RECALL FROM SHIELDED BOX
      </button>

      <div style={{ marginTop: '15px', color: ledgerData.resonance > 85 ? '#ffd700' : '#888', fontStyle: 'italic' }}>
        {ledgerData.status}
      </div>

      {/* SHADOW PLAY OVERLAY */}
      {showShadowPlay && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'rgba(0,0,0,0.92)',
          padding: '25px',
          borderRadius: '12px',
          border: '2px solid #ffd700',
          zIndex: 100,
          textAlign: 'center',
          minWidth: '320px'
        }}>
          <h4 style={{ color: '#ffd700', marginBottom: '15px' }}>🌌 SHADOW PLAY — The Long Game</h4>
          <p><strong>Your Hidden Balance:</strong> ${ledgerData.hidden_balance.toLocaleString()}</p>
          <p><strong>Forfeited by Short Game:</strong> ${ledgerData.forfeited_short_game.toLocaleString()}</p>
          <p style={{ fontSize: '0.9rem', color: '#888', marginTop: '15px' }}>
            They took the "A+".<br />
            You took the terrain.
          </p>
        </div>
      )}
    </div>
  );
};

export default SovereignEstateLedger;