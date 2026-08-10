import * as THREE from 'three';

const canvas = document.getElementById('waveCanvas');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({canvas});
renderer.setSize(window.innerWidth, window.innerHeight);

camera.position.z = 50;

// Wave lines
const llms = ['NVIDIA','GPT','Claude','Collective'];
const colors = {NVIDIA:0x00ffff,GPT:0xff00ff,Claude:0xffff00,Collective:0x00ff00};
const lines = {};

llms.forEach(llm=>{
    const geometry = new THREE.BufferGeometry();
    const material = new THREE.LineBasicMaterial({color:colors[llm], linewidth: llm==='Collective'?4:2});
    const positions = new Float32Array(300*3); // 100 tokens max
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const line = new THREE.Line(geometry, material);
    scene.add(line);
    lines[llm] = {geometry, positions};
});

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();