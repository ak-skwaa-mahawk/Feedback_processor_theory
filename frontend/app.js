let ws = new WebSocket("ws://localhost:8765");
ws.onopen = () => console.log("WebSocket connected");

let tokenIndex = 0;
const lineData = { positions: new Float32Array(300*3) }; // 100 points

// 3D Setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById("convergenceCanvas") });
renderer.setSize(window.innerWidth, window.innerHeight);
camera.position.z = 50;
const geometry = new THREE.BufferGeometry();
geometry.setAttribute('position', new THREE.BufferAttribute(lineData.positions, 3));
const material = new THREE.LineBasicMaterial({ color: 0x00ff00 });
const line = new THREE.Line(geometry, material);
scene.add(line);

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if(msg.type==="harmony"){
        const score = msg.score;
        const idx = (tokenIndex % 100) * 3;
        lineData.positions[idx] = tokenIndex % 100 - 50;      // X
        lineData.positions[idx+1] = score * 20;              // Y
        lineData.positions[idx+2] = Math.sin(tokenIndex)*5;  // Z
        geometry.attributes.position.needsUpdate = true;
        tokenIndex++;
    }
}

// Audio Capture
async function captureAudio() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio:true });
    const audioCtx = new AudioContext();
    const source = audioCtx.createMediaStreamSource(stream);
    const processor = audioCtx.createScriptProcessor(4096,1,1);
    source.connect(processor);
    processor.connect(audioCtx.destination);

    processor.onaudioprocess = (e) => {
        const input = e.inputBuffer.getChannelData(0);
        const float32Data = Float32Array.from(input);
        const b64 = btoa(String.fromCharCode(...new Uint8Array(float32Data.buffer)));
        ws.send(JSON.stringify({ type:"audio_chunk", data:b64 }));
    }
}
captureAudio();