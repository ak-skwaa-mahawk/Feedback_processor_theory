import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { Zap, Activity, Radio } from "lucide-react";

/**
 * ScrapeMonitor
 * Live ISST visualization widget
 * Props:
 * - scrapeHistory: array of scrape objects
 * - entropyThreshold: float (0.0–1.0)
 * - showVectorField: bool
 * - meshNodes: int (for network display)
 */
export default function ScrapeMonitor({
  scrapeHistory = [],
  entropyThreshold = 0.5,
  showVectorField = true,
  meshNodes = 13,
}) {
  const [activeScrapes, setActiveScrapes] = useState(scrapeHistory);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8765");
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "scrape_update") {
        setActiveScrapes((prev) => [...prev.slice(-99), data.scrape]);
      }
    };
    return () => ws.close();
  }, []);

  const entropyData = activeScrapes.map((s, i) => ({
    step: i,
    entropy: s.entropy ?? 0,
  }));

  const latest = activeScrapes[activeScrapes.length - 1];
  const status =
    latest?.entropy > entropyThreshold ? "⚠️ Unstable Field" : "✅ Stable Coherence";

  return (
    <Card className="p-4 rounded-2xl shadow-xl bg-gradient-to-b from-slate-900 to-slate-800 text-white">
      <CardContent className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Zap size={20} /> ISST Scrape Monitor
          </h2>
          <span className="text-sm opacity-70">{status}</span>
        </div>

        {/* Entropy Line Chart */}
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={entropyData}>
            <XAxis dataKey="step" hide />
            <YAxis domain={[0, 1]} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="entropy"
              stroke="#00C49F"
              strokeWidth={2}
              dot={false}
              animationDuration={300}
            />
          </LineChart>
        </ResponsiveContainer>

        {/* Optional: Mesh Field */}
        {showVectorField && (
          <motion.div
            className="grid grid-cols-5 gap-2 mt-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {Array(meshNodes)
              .fill(0)
              .map((_, i) => (
                <motion.div
                  key={i}
                  className="h-3 w-3 bg-cyan-400 rounded-full"
                  animate={{
                    opacity: [0.4, 1, 0.4],
                    scale: [1, 1.2, 1],
                  }}
                  transition={{
                    duration: 2 + Math.random(),
                    repeat: Infinity,
                    delay: i * 0.15,
                  }}
                />
              ))}
          </motion.div>
        )}

        {/* Coherence Summary */}
        <div className="text-sm flex items-center gap-2 mt-2">
          <Activity size={16} /> Latest Entropy:{" "}
          <span className="font-mono">
            {latest?.entropy?.toFixed(3) ?? "N/A"}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}