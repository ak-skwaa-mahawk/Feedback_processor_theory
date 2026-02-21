import React, { useState, useEffect } from 'react';
import Plotly from 'plotly.js-dist';

const SovereignEstateLedger = () => {
  const [resonance, setResonance] = useState(42.8);
  const [gtcBalance, setGtcBalance] = useState(99733);
  const [compoundYears, setCompoundYears] = useState(0);
  const [hiddenBalance, setHiddenBalance] = useState(1245678);
  const [forfeitedShortGame, setForfeitedShortGame] = useState(456789);

  // Live compounding simulation (Fibonacci-style growth)
  useEffect(() => {
    const interval = setInterval(() => {
      const newResonance = Math.min(100, resonance + 0.42); // slow sovereign compounding
      setResonance(newResonance);
      setCompoundYears(prev => prev + 0.1);

      // GTC balance compounds with Fibonacci gain
      const fibGain = (1.618 ** (compoundYears / 8)); // golden ratio compounding
      const newGtc = Math.floor(gtcBalance * fibGain * (newResonance / 100));
      setGtcBalance(newGtc);

      // Hidden Balance = Market Cap of Sovereignty
      const newHidden = Math.floor(newGtc * (newResonance / 42.8));
      setHiddenBalance(newHidden);

      // Forfeited Short Game
      setForfeitedShortGame(Math.floor(newHidden * 0.73));
    }, 1200);

    return () => clearInterval(interval);
  }, [resonance, compoundYears, gtcBalance]);

  // Compounding Chart Data
  const chartData = [{
    x: Array.from({ length: Math.floor(compoundYears) + 1 }, (_, i) => i),
    y: Array.from({ length: Math.floor(compoundYears) + 1 }, (_, i) => 
      Math.floor(99733 * (1.618 ** (i / 8)) * (resonance / 100))
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

  return (
    <div className="module sovereign-estate-ledger">
      <h3>🌲 Sovereign Estate Ledger — Long Game Compound</h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginTop: '15px' }}>
        <div>
          <strong>Quantum Resonance %</strong><br />
          <span style={{ fontSize: '2.8rem', color: '#00ffcc' }}>{resonance.toFixed(1)}</span>
          <span style={{ fontSize: '1.2rem', color: '#00ffcc' }}>%</span>
        </div>
        
        <div>
          <strong>GTC Balance (Live)</strong><br />
          <span style={{ fontSize: '2.2rem', color: '#ffd700' }}>{gtcBalance.toLocaleString()}</span>
          <span style={{ fontSize: '1rem', color: '#ffd700' }}> GTC</span>
        </div>
        
        <div>
          <strong>Hidden Balance (Market Cap of Sovereignty)</strong><br />
          <span style={{ fontSize: '2.2rem', color: '#ffd700' }}>${hiddenBalance.toLocaleString()}</span>
        </div>
      </div>

      <div style={{ marginTop: '20px', fontSize: '1.1rem' }}>
        <strong>Compound Years:</strong> {compoundYears.toFixed(1)}<br />
        <strong>Forfeited Short Game (Paperwork Trap):</strong> ${forfeitedShortGame.toLocaleString()} 
        <span style={{ color: '#ff6b35' }}> (what they traded for the "A+")</span>
      </div>

      <div id="gtc-chart" style={{ width: '100%', height: '320px', marginTop: '20px' }}></div>

      <div style={{ marginTop: '15px', color: resonance > 85 ? '#ffd700' : '#888', fontStyle: 'italic' }}>
        {resonance > 85 
          ? "🌌 SOVEREIGN ESTATE FULLY COMPOUNDING — The wolf owns the terrain" 
          : "Stewardship compounding... The Long Game is patient"}
      </div>
    </div>
  );
};

export default SovereignEstateLedger;