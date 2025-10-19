const socket = io();

const startBtn = document.getElementById('startBtn');
const promptInput = document.getElementById('prompt');
const logsDiv = document.getElementById('logs');

startBtn.onclick = () => {
  const prompt = promptInput.value || "Let's discuss multi-LLM harmonic convergence.";
  logsDiv.innerHTML = "";
  socket.emit('startConversation', prompt);
};

const ctx = document.getElementById('similarityChart').getContext('2d');
const chartData = {
  labels: [],
  datasets: [
    { label: 'NVIDIA', data: [], borderColor: 'red', fill: false },
    { label: 'GPT', data: [], borderColor: 'blue', fill: false },
    { label: 'Claude', data: [], borderColor: 'green', fill: false },
  ]
};

const similarityChart = new Chart(ctx, {
  type: 'line',
  data: chartData,
  options: { scales: { y: { min: 0, max: 1 } } }
});

socket.on('update', (log) => {
  const turnIterLabel = `T${log.iteration}`;
  chartData.labels.push(turnIterLabel);
  
  // Compute cosine similarity to combined output
  // (You can implement real-time embeddings on frontend too)
  chartData.datasets[0].data.push(Math.random()); // placeholder
  chartData.datasets[1].data.push(Math.random());
  chartData.datasets[2].data.push(Math.random());

  similarityChart.update();

  logsDiv.innerHTML += `<p><b>Iteration ${log.iteration}:</b> Combined: ${log.combined}</p>`;
});

socket.on('turnComplete', ({ turn, turnOutput }) => {
  logsDiv.innerHTML += `<h3>Turn ${turn} Complete</h3>`;
});