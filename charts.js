// === 2D Chart.js setup ===
const ctx = document.getElementById('alignmentChart').getContext('2d');
const llms = ['NVIDIA','GPT','Claude','Collective'];
const chartData = {
  labels: Array.from({length:100}, (_,i)=>i+1),
  datasets: llms.map((llm, idx)=>({
    label: llm,
    borderColor: ['cyan','magenta','yellow','lime'][idx],
    data: Array(100).fill(0),
    fill: false,
    tension: 0.2
  }))
};
const alignmentChart = new Chart(ctx, {
  type: 'line',
  data: chartData,
  options: { animation: false, responsive: true }
});

// === 3D Three.js setup ===
const canvas = document.getElementById('waveCanvas');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({canvas});
renderer.setSize(window.innerWidth, window.innerHeight);
camera.position.z = 50;

const colors = {NVIDIA:0x00ffff,GPT:0xff00ff,Claude:0xffff00,Collective:0x00ff00};
const lines = {};
llms.forEach(llm=>{
  const geometry = new THREE.BufferGeometry();
  const material = new THREE.LineBasicMaterial({color:colors[llm], linewidth: llm==='Collective'?4:2});
  const positions = new Float32Array(100*3);
  geometry.setAttribute('position', new THREE.BufferAttribute(positions,3));
  const line = new THREE.Line(geometry, material);
  scene.add(line);
  lines[llm] = {geometry, positions, collectiveBuffer:{}};
});

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
animate();