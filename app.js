const ws = new WebSocket("ws://localhost:8000/ws");
const inputText = document.getElementById("inputText");
const sendBtn = document.getElementById("sendBtn");
const streamOutput = document.getElementById("streamOutput");

// Chart.js setup
const ctx = document.getElementById('harmonyChart').getContext('2d');
const chartData = {
    labels: [],
    datasets: [
        { label: 'NVIDIA', data: [], borderColor: 'cyan', tension: 0.3 },
        { label: 'GPT', data: [], borderColor: 'magenta', tension: 0.3 },
        { label: 'Claude', data: [], borderColor: 'yellow', tension: 0.3 },
        { label: 'Collective', data: [], borderColor: 'lime', borderWidth: 3, tension: 0.4 }
    ]
};
const harmonyChart = new Chart(ctx, {
    type: 'line',
    data: chartData,
    options: {
        scales: {
            y: { min: 0, max: 1, title: { text: "Harmony Score", display: true } }
        }
    }
});

function getAudioEmbedding() {
    return Array.from({length:128}, () => Math.random());
}

sendBtn.onclick = () => {
    const msg = {
        text: inputText.value,
        audio_embedding: getAudioEmbedding()
    };
    ws.send(JSON.stringify(msg));
    chartData.labels.push(inputText.value);
};

// Token streaming & collective resonance
const llmColors = { NVIDIA: 'cyan', GPT: 'magenta', Claude: 'yellow' };
const harmonyBuffer = {};  // {tokenIndex: {NVIDIA:0.5, GPT:0.6, Claude:0.4}}

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const {token, harmony, llm, tokenIndex} = data;

    // Buffer harmony
    if (!harmonyBuffer[tokenIndex]) harmonyBuffer[tokenIndex] = {};
    harmonyBuffer[tokenIndex][llm] = harmony;

    // Compute collective mean
    const currentHarmonies = harmonyBuffer[tokenIndex];
    const collective = Object.values(currentHarmonies).reduce((a,b)=>a+b,0)/Object.keys(currentHarmonies).length;

    // Update stream output
    const p = document.createElement('p');
    p.style.color = llmColors[llm];
    p.innerHTML = `<b>${llm}</b>: ${token} → Harmony: ${(harmony*100).toFixed(1)}% | Collective: ${(collective*100).toFixed(1)}%`;
    streamOutput.appendChild(p);
    streamOutput.scrollTop = streamOutput.scrollHeight;

    // Update chart
    const dataset = harmonyChart.data.datasets.find(ds => ds.label === llm);
    dataset.data.push(harmony);

    const collectiveDataset = harmonyChart.data.datasets.find(ds => ds.label === 'Collective');
    collectiveDataset.data.push(collective);

    // Keep last 50 points
    chartData.datasets.forEach(ds => { if(ds.data.length>50) ds.data.shift(); });
    if(chartData.labels.length>50) chartData.labels.shift();

    harmonyChart.update();
};