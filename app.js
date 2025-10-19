// frontend/app.js
// Enhanced Trinity Harmonics with demo toggle and stats

const ws = new WebSocket("ws://localhost:8765");
const canvas = document.getElementById("convergenceCanvas");
const log = document.getElementById("log");
const promptInput = document.getElementById("prompt");
const startBtn = document.getElementById("startBtn");
const statsBtn = document.getElementById("statsBtn");
const demoToggle = document.getElementById("demoToggle");
const statusBadges = document.getElementById("statusBadges");
const statsDisplay = document.getElementById("statsDisplay");

let isDemoMode = false;
let availableLLMs = [];

// WebSocket handlers
ws.onopen = () => {
  appendLog("✓ WebSocket connected", "system");
  startBtn.disabled = false;
};

ws.onclose = () => {
  appendLog("✗ WebSocket closed", "system");
  startBtn.disabled = true;
};

ws.onerror = (err) => {
  appendLog(`✗ WebSocket error: ${err}`, "system");
};

// UI handlers
startBtn.onclick = () => {
  const prompt = promptInput.value || "Explain harmonic convergence in multi-LLM systems.";
  ws.send(JSON.stringify({type: "start", prompt}));
  appendLog(`▶ Starting Trinity with prompt: "${prompt}"`, "system");
};

statsBtn.onclick = () => {
  ws.send(JSON.stringify({type: "get_stats"}));
};

demoToggle.onchange = () => {
  ws.send(JSON.stringify({type: "toggle_demo"}));
};

// Three.js visualization setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / (window.innerHeight * 0.6), 0.1, 1000);
camera.position.z = 120;

const renderer = new THREE.WebGLRenderer({canvas, antialias: true});
renderer.setSize(window.innerWidth, window.innerHeight * 0.6);
renderer.setClearColor(0x000000);

// Create multiple lines for each LLM
const llmLines = {};
const llmColors = {
  "NVIDIA": 0x76b900,
  "GPT": 0x00a67e,
  "CLAUDE": 0x9b59b6
};

Object.entries(llmColors).forEach(([llm, color]) => {
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(300 * 3);
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const material = new THREE.LineBasicMaterial({color, linewidth: 2});
  const line = new THREE.Line(geometry, material);
  scene.add(line);
  llmLines[llm] = {line, geometry, positions, index: 0};
});

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  
  // Rotate camera slowly
  camera.position.x = Math.sin(Date.now() * 0.0001) * 120;
  camera.position.z = Math.cos(Date.now() * 0.0001) * 120;
  camera.lookAt(0, 0, 0);
  
  renderer.render(scene, camera);
}
animate();

// Window resize handler
window.addEventListener('resize', () => {
  const width = window.innerWidth;
  const height = window.innerHeight * 0.6;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
});

// Log message helper
function appendLog(message, type = "info") {
  const div = document.createElement('div');
  div.className = `token ${type}`;
  div.textContent = message;
  log.prepend(div);
  
  // Keep only last 100 messages
  while (log.children.length > 100) {
    log.removeChild(log.lastChild);
  }
}

// Update status badges
function updateStatus(data) {
  const badges = [];
  
  if (data.demo_mode) {
    badges.push('<span class="badge demo">DEMO MODE</span>');
  }
  
  if (data.available_llms) {
    availableLLMs = data.available_llms;
    data.available_llms.forEach(llm => {
      badges.push(`<span class="badge">${llm.toUpperCase()}</span>`);
    });
  }
  
  if (data.cache_enabled) {
    badges.push('<span class="badge">CACHE ON</span>');
  }
  
  statusBadges.innerHTML = badges.join('');
}

// Update stats display
function updateStats(stats) {
  const cache = stats.cache;
  const session = stats.session;
  
  const html = `
    <div style="margin-top:12px;padding-top:12px;border-top:1px solid #333;">
      <div class="stat"><strong>Cache Hit Rate:</strong> ${cache.hit_rate_percent.toFixed(1)}%</div>
      <div class="stat"><strong>Cache Hits:</strong> ${cache.cache_hits} / ${cache.total_calls}</div>
      <div class="stat"><strong>Cache Size:</strong> ${cache.lru_info.currsize} / ${cache.max_cache_size}</div>
      <div class="stat"><strong>Tokens Processed:</strong> ${session.tokens_processed}</div>
      <div class="stat"><strong>Audio Active:</strong> ${session.has_audio ? 'Yes' : 'No'}</div>
    </div>
  `;
  
  statsDisplay.innerHTML = html;
}

// WebSocket message handler
ws.onmessage = (evt) => {
  const data = JSON.parse(evt.data);
  
  switch (data.type) {
    case "connected":
      updateStatus(data);
      demoToggle.checked = data.demo_mode;
      isDemoMode = data.demo_mode;
      appendLog(`✓ Connected - Demo: ${data.demo_mode}, LLMs: ${data.available_llms.join(', ')}`, "system");
      break;
    
    case "text":
      const {tokenIndex, llm, token, harmony, demo_mode} = data;
      const llmLower = llm.toLowerCase();
      
      // Append to log
      const demoFlag = demo_mode ? " [DEMO]" : "";
      appendLog(`${llm} [${tokenIndex}]: ${token} → harmony: ${harmony.toFixed(3)}${demoFlag}`, llmLower);
      
      // Update visualization
      if (llmLines[llm]) {
        const llmData = llmLines[llm];
        const idx = llmData.index % 100;
        const posIdx = idx * 3;
        
        // Position based on LLM (spread them out)
        const llmOffset = Object.keys(llmLines).indexOf(llm) * 20 - 20;
        
        llmData.positions[posIdx] = (idx - 50) * 1.5;
        llmData.positions[posIdx + 1] = (harmony * 30) + llmOffset;
        llmData.positions[posIdx + 2] = Math.sin(tokenIndex * 0.1) * 10;
        
        llmData.geometry.attributes.position.needsUpdate = true;
        llmData.index++;
      }
      break;
    
    case "completion":
      appendLog(`✓ ${data.llm} completed (${data.tokens} tokens)`, "system");
      break;
    
    case "audio_energy":
      appendLog(`🎤 Audio energy: ${data.energy.toFixed(3)}`, "system");
      break;
    
    case "demo_toggled":
      isDemoMode = data.demo_mode;
      demoToggle.checked = data.demo_mode;
      appendLog(`⚙ Demo mode: ${data.demo_mode ? 'ON' : 'OFF'}`, "system");
      updateStatus({demo_mode: data.demo_mode});
      break;
    
    case "stats":
      updateStats(data);
      appendLog("📊 Stats updated", "system");
      break;
    
    case "pong":
      appendLog("🏓 Pong received", "system");
      break;
    
    default:
      console.log("Unknown message type:", data.type);
  }
};

// Auto-request stats every 10 seconds
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({type: "get_stats"}));
  }
}, 10000);