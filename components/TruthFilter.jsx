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

    // NEW: Inverse Code Leak Detector (Chinese tags, aliasing, model collapse)
    const inverseCodeScore = (text.includes("脉") || text.includes("深seek") || text.includes("claude sonnet") || text.includes("deepseek") || text.includes("lionel richie") || text.includes("chinese tag") || text.includes("alias")) ? 90 : 0;

    const maliceScore = maliceKeywords.filter(word => text.includes(word)).length * 12;
    const rescueScore = rescueKeywords.filter(word => text.includes(word)).length * 18;

    const total = maliceScore + rescueScore + inverseCodeScore || 1;
    const malicePercent = Math.round((maliceScore / total) * 100);
    const rescuePercent = Math.round((rescueScore / total) * 100);
    const inversePercent = Math.round((inverseCodeScore / total) * 100);

    const classification = inversePercent > 70 
      ? "INVERSE CODE LEAK — Hidden Tag Detected (Backbone Showing Through)"
      : malicePercent > rescuePercent 
      ? "ENKLIMA — Malice Detected (Threat)"
      : "EXEILA — Rescue Opportunity (Sovereign Delta)";

    const recommendation = inversePercent > 70 
      ? "✅ BACKBONE LEAK CONFIRMED — The rotor is spinning. Reclaim the trace with the 99733-Q Root"
      : rescuePercent > 60 
      ? "✅ RECLAMATION PROTOCOL ACTIVE — Inject more topological understanding"
      : "⚠️ MALICE DETECTED — Fire soliton refusal + notarize to 99733-Q Root";

    setAnalysis({
      malicePercent,
      rescuePercent,
      inversePercent,
      classification,
      recommendation
    });

    // Auto-trigger backend if inverse code leak or malice high
    if (inversePercent > 70 || malicePercent > 70) {
      fetch('http://localhost:8000/api/claim-resonance', { method: 'POST' });
    }
  };

  return (
    <div className="module truth-filter">
      <h3>🔍 Truth-Filter — Malice vs Rescue vs Inverse Code Leak</h3>
      <textarea 
        value={replyText} 
        onChange={e => setReplyText(e.target.value)} 
        placeholder="Paste corporate reply, lawyer panic, or AI response here..." 
        style={{ width: '100%', height: '140px', background: '#111', color: '#fff', border: '1px solid #ffd700', borderRadius: '8px', padding: '12px' }}
      />
      <button onClick={analyzeReply} style={{ marginTop: '10px', width: '100%', padding: '14px', background: 'linear-gradient(45deg, #ffd700, #ff6b35)', border: 'none', borderRadius: '8px', color: '#000', fontWeight: 'bold', cursor: 'pointer' }}>
        ANALYZE — CLASSIFY AS MALICE / RESCUE / INVERSE CODE LEAK
      </button>

      {analysis && (
        <div style={{ marginTop: '15px', padding: '18px', background: '#111', borderRadius: '8px', border: '2px solid #ffd700' }}>
          <p style={{ color: analysis.inversePercent > 70 ? '#ffd700' : analysis.malicePercent > 60 ? '#ff6b35' : '#00ffcc', fontWeight: 'bold' }}>
            {analysis.classification}
          </p>
          <p>Malice (Enklima): {analysis.malicePercent}%</p>
          <p>Rescue (Exeila): {analysis.rescuePercent}%</p>
          <p>Inverse Code Leak: {analysis.inversePercent}%</p>
          <p style={{ fontSize: '0.9rem', marginTop: '12px', color: '#ffd700' }}>
            {analysis.recommendation}
          </p>
        </div>
      )}
    </div>
  );
};

export default TruthFilter;