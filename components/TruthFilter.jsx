import React, { useState } from 'react';

const TruthFilter = () => {
  const [replyText, setReplyText] = useState('');
  const [analysis, setAnalysis] = useState(null);

  const analyzeReply = () => {
    // Simple sovereign symptom vs delta filter (expandable with real NLP later)
    const symptomKeywords = ["theft", "steal", "copyright", "lawyer", "illegal", "crazy", "woo", "fake", "impossible"];
    const deltaKeywords = ["interesting", "new", "resonance", "sovereign", "terrain", "long game", "topology", "pi", "fibonacci"];

    const symptomScore = symptomKeywords.filter(word => replyText.toLowerCase().includes(word)).length * 10;
    const deltaScore = deltaKeywords.filter(word => replyText.toLowerCase().includes(word)).length * 15;

    const total = symptomScore + deltaScore || 1;
    const symptomPercent = Math.round((symptomScore / total) * 100);
    const deltaPercent = Math.round((deltaScore / total) * 100);

    const actualDelta = deltaPercent > 60 ? "Strong injection of new information" : 
                       deltaPercent > 30 ? "Moderate resonance detected" : "Mostly symptom — low new information";

    setAnalysis({
      symptomPercent,
      deltaPercent,
      actualDelta,
      recommendation: deltaPercent > 50 ? "✅ Continue the dive — you are injecting sovereign topology" : "⚠️ Increase clarity — the wolf’s howl needs to cut through more"
    });
  };

  return (
    <div className="module truth-filter">
      <h3>🔍 Truth-Filter — Symptom vs Actual Delta</h3>
      <textarea 
        value={replyText} 
        onChange={e => setReplyText(e.target.value)} 
        placeholder="Paste a reply or peer judgment here..." 
        style={{ width: '100%', height: '120px', background: '#111', color: '#fff', border: '1px solid #ffd700', borderRadius: '8px', padding: '10px' }}
      />
      <button onClick={analyzeReply} style={{ marginTop: '10px', width: '100%', padding: '12px', background: '#ffd700', color: '#000', border: 'none', borderRadius: '8px', fontWeight: 'bold' }}>
        ANALYZE REPLY — STRIP THE SYMPTOM
      </button>

      {analysis && (
        <div style={{ marginTop: '15px', padding: '15px', background: '#111', borderRadius: '8px', border: '1px solid #ffd700' }}>
          <p><strong>Symptom (Ego/Law/Noise):</strong> {analysis.symptomPercent}%</p>
          <p><strong>Actual Delta (New Information Injected):</strong> {analysis.deltaPercent}%</p>
          <p style={{ color: analysis.deltaPercent > 50 ? '#00ffcc' : '#ff6b35', fontWeight: 'bold' }}>
            {analysis.actualDelta}
          </p>
          <p style={{ fontSize: '0.9rem', marginTop: '10px' }}>
            {analysis.recommendation}
          </p>
        </div>
      )}
    </div>
  );
};

export default TruthFilter;