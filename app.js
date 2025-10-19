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
        { label: 'Claude', data: [], borderColor: 'yellow', tension: 0.3 }
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
    chartData.labels.push(...Array(5).fill(inputText.value)); // placeholder
};

// Multi-LLM token streaming
const llmColors = { NVIDIA: 'cyan', GPT: 'magenta', Claude: 'yellow' };

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const token = data.token;
    const harmony = data.harmony;
    const llm = data.llm;

    // Update stream output
    const p = document.createElement('p');
    p.style.color = llmColors[llm];
    p.innerHTML = `<b>${llm}</b>: ${token} → Harmony: ${(harmony*100).toFixed(1)}%`;
    streamOutput.appendChild(p);
    streamOutput.scrollTop = streamOutput.scrollHeight;

    // Update chart
    const dataset = harmonyChart.data.datasets.find(ds => ds.label === llm);
    dataset.data.push(harmony);
    if (dataset.data.length > 50) dataset.data.shift();  // keep last 50 points
    harmonyChart.update();
};