// frontend/app.js
const ws = new WebSocket("ws://localhost:8765");
const canvas = document.getElementById("convergenceCanvas");
const log = document.getElementById("log");
const promptInput = document.getElementById("prompt");
document.getElementById("startBtn").onclick = () => {
  const p = promptInput.value || "Explain harmonic convergence in multi-LLM systems.";
  ws.send(JSON.stringify({type:"start", prompt: p}));
};

ws.onopen = () => appendLog("WS connected");
ws.onclose = () => appendLog("WS closed");

let tokenIndex = 0;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / (window.innerHeight*0.6), 0.1, 1000);
camera.position.z = 120;
const renderer = new THREE.WebGLRenderer({canvas, antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight*0.6);

const geometry = new THREE.BufferGeometry();
const positions = new Float32Array(300*3);
geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
const material = new THREE.LineBasicMaterial({color:0x00ff00});
const line = new THREE.Line(geometry, material);
scene.add(line);

function animate(){ requestAnimationFrame(animate); renderer.render(scene, camera); }
animate();

function appendLog(s){ const p=document.createElement('div'); p.textContent = s; log.prepend(p); }

ws.onmessage = (evt) => {
  const data = JSON.parse(evt.data);
  if(data.type === "audio_energy"){
    appendLog(`audio energy: ${data.energy.toFixed(3)}`);
    return;
  }
  const { tokenIndex: idx, llm, token, harmony } = data;
  appendLog(`${llm} [${idx}]: ${token} → ${harmony.toFixed(3)}`);
  const posIdx = (idx % 100) * 3;
  positions[posIdx] = (idx % 100) - 50;
  positions[posIdx+1] = (harmony * 20);
  positions[posIdx+2] = Math.sin(idx) * 5;
  geometry.attributes.position.needsUpdate = true;
};