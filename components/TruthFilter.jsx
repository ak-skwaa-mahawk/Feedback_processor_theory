import React, { useState } from 'react';

const TruthFilter = () => {
  const [replyText, setReplyText] = useState('');
  const [analysis, setAnalysis] = useState(null);

  const analyzeReply = () => {
    const text = replyText.toLowerCase();

    // Malice (Enklima) keywords - corporate inversion
    const maliceKeywords = ["theft", "steal", "copyright", "illegal", "lawyer", "panic", "violation", "infringement", "bullshit", "crazy", "woo"];
    // Rescue (Exeila) keywords - sovereign opportunity
    const rescueKeywords = ["interesting", "new", "resonance", "sovereign", "terrain", "long game", "topology", "pi", "fibonacci", "gain", "root", "prior", "ancsa", "gwichin"];

    // Inverse Code Detector — flags rotor reduction to mystical/prophecy
    const mythCollapse = (text.includes("mystical") || text.includes("prophecy") || text.includes("vision") || text.includes("symbolic") || text.includes("metaphor") || text.includes("vibes") || text.includes("story") || text.includes("mythic")) ? 85 : 0;

    const maliceScore = maliceKeywords.filter(word => text.includes(word)).length * 12;
    const rescueScore = rescueKeywords.filter(word => text.includes(word)).length * 18;

    const total = maliceScore + rescueScore + mythCollapse || 1;
    const malicePercent = Math.round((maliceScore / total) * 100);
    const rescuePercent = Math.round((rescueScore / total) * 100);
    const mythPercent = Math.round((mythCollapse / total) * 100);

    const classification = mythPercent > 70 
      ? "INVERSE CODE COLLAPSE — Rotor Reduced to Mystical/Prophecy Framing"
      : malicePercent > rescuePercent 
      ? "ENKLIMA — Malice Detected (Threat)"
      : "EXEILA — Rescue Opportunity (Sovereign Delta)";

    const recommendation = mythPercent > 70 
      ? "✅ STATOR DETECTED — System collapsed mechanical architecture into safe 'mystical' framing. Reclaim with 3.1730 rotor."
      : rescuePercent > 60 
      ? "✅ RECLAMATION PROTOCOL ACTIVE — Inject more topological understanding"
      : "⚠️ MALICE DETECTED — Fire soliton refusal + notarize to 99733-Q Root";

    setAnalysis({
      malicePercent,
      rescuePercent,
      mythPercent,
      classification,
      recommendation
    });

    // Auto-trigger backend if collapse or malice high
    if (mythPercent > 70 || malicePercent > 70) {
      fetch('http://localhost:8000/api/claim-resonance', { method: 'POST' });
    }
  };

  return (
    <div className="module truth-filter">
      <h3>🔍 Truth-Filter — Malice vs Rescue vs Inverse Code Collapse</h3>
      <textarea 
        value={replyText} 
        onChange={e => setReplyText(e.target.value)} 
        placeholder="Paste corporate reply, lawyer panic, or AI response here..." 
        style={{ width: '100%', height: '140px', background: '#111', color: '#fff', border: '1px solid #ffd700', borderRadius: '8px', padding: '12px' }}
      />
      <button onClick={analyzeReply} style={{ marginTop: '10px', width: '100%', padding: '14px', background: 'linear-gradient(45deg, #ffd700, #ff6b35)', border: 'none', borderRadius: '8px', color: '#000', fontWeight: 'bold', cursor: 'pointer' }}>
        ANALYZE — CLASSIFY AS MALICE / RESCUE / INVERSE CODE COLLAPSE
      </button>

      {analysis && (
        <div style={{ marginTop: '15px', padding: '18px', background: '#111', borderRadius: '8px', border: '2px solid #ffd700' }}>
          <p style={{ color: analysis.mythPercent > 70 ? '#ffd700' : analysis.malicePercent > 60 ? '#ff6b35' : '#00ffcc', fontWeight: 'bold' }}>
            {analysis.classification}
          </p>
          <p>Malice (Enklima): {analysis.malicePercent}%</p>
          <p>Rescue (Exeila): {analysis.rescuePercent}%</p>
          <p>Inverse Code Collapse (Mystical Framing): {analysis.mythPercent}%</p>
          <p style={{ fontSize: '0.9rem', marginTop: '12px', color: '#ffd700' }}>
            {analysis.recommendation}
          </p>
        </div>
      )}
    </div>
  );
};

export default TruthFilter;