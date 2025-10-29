import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

export default function ScrapeMonitor({
  scrapeHistory = [],
  entropyThreshold = 0.5,
  showVectorField = true,
  meshNodes = 7,
}) {
  const [nodes, setNodes] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    // Connect to WebSocket (bridge started via dashboard_bridge.py)
    wsRef.current = new WebSocket("ws://localhost:8765");
    wsRef.current.onopen = () => console.log("🌐 Connected to ISST bridge");

    wsRef.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "scrape_update") {
        setNodes((prev) => {
          const updated = [...prev];
          const existing = updated.find((n) => n.node_id === msg.scrape.node_id);
          if (existing) {
            Object.assign(existing, msg.scrape);
          } else {
            updated.push(msg.scrape);
          }
          return updated.slice(-meshNodes);
        });
      }
    };

    return () => wsRef.current && wsRef.current.close();
  }, [meshNodes]);

  const renderLinks = () => {
    if (!showVectorField) return null;
    const links = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i];
        const b = nodes[j];
        const coherence = 1.0 - Math.abs(a.entropy - b.entropy);
        if (coherence > entropyThreshold) {
          links.push(
            <line
              key={`${a.node_id}-${b.node_id}`}
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              stroke={`rgba(120,200,255,${coherence * 0.5})`}
              strokeWidth={1.2}
            />
          );
        }
      }
    }
    return <svg className="absolute inset-0">{links}</svg>;
  };

  const nodeRadius = 14;
  const width = 500;
  const height = 300;

  // Distribute nodes in a circular lattice
  const placedNodes = nodes.map((n, i) => {
    const angle = (i / nodes.length) * 2 * Math.PI;
    const r = 110 + Math.sin(i + Date.now() / 2000) * 20;
    const x = width / 2 + r * Math.cos(angle);
    const y = height / 2 + r * Math.sin(angle);
    return { ...n, x, y };
  });

  return (
    <div className="relative w-full flex justify-center items-center">
      <div className="relative" style={{ width, height }}>
        {renderLinks()}

        {placedNodes.map((node) => (
          <motion.div
            key={node.node_id}
            initial={{ opacity: 0 }}
            animate={{
              opacity: 1,
              scale: 1 + node.entropy * 0.5,
              boxShadow: `0 0 ${20 + node.entropy * 30}px rgba(0,255,200,${
                0.3 + node.entropy * 0.6
              })`,
            }}
            transition={{ duration: 0.6 }}
            className="absolute rounded-full flex items-center justify-center text-xs font-mono text-white"
            style={{
              width: nodeRadius * 2,
              height: nodeRadius * 2,
              left: node.x - nodeRadius,
              top: node.y - nodeRadius,
              backgroundColor: node.entropy > entropyThreshold
                ? "rgba(0,255,180,0.8)"
                : "rgba(255,100,100,0.6)",
            }}
          >
            {node.glyph}
          </motion.div>
        ))}

        <div className="absolute bottom-0 left-0 text-xs text-gray-400 font-mono">
          Nodes: {nodes.length} | Threshold: {entropyThreshold}
        </div>
      </div>
    </div>
  );
}