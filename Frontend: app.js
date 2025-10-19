const ws = new WebSocket("ws://localhost:8000/ws");
const inputText = document.getElementById("inputText");
const sendBtn = document.getElementById("sendBtn");
const streamOutput = document.getElementById("streamOutput");

function getAudioEmbedding() {
    return Array.from({length:128}, () => Math.random());
}

sendBtn.onclick = () => {
    const msg = {
        text: inputText.value,
        audio_embedding: getAudioEmbedding()
    };
    ws.send(JSON.stringify(msg));
};

const llmColors = { NVIDIA: "cyan", GPT: "magenta", Claude: "yellow" };

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const token = data.token;
    const harmony = (data.harmony*100).toFixed(1);
    const llm = data.llm;
    streamOutput.innerHTML += `<p style="color:${llmColors[llm]}"><b>${llm}</b>: ${token} → Harmony: ${harmony}%</p>`;
    streamOutput.scrollTop = streamOutput.scrollHeight;
};