# fpt_core/trinity_harmonics.py
import numpy as np
from math import pi, exp

GROUND_STATE = 0.1    # Baseline phase
DIFFERENCE = 0.05     # Phase deviation
DAMPING_PRESETS = {"Balanced": 0.5, "Aggressive": 0.7, "Gentle": 0.3}
CUSTOM_PRESETS = {}

def trinity_damping(signal, damp_factor):
    """Apply exponential damping to signal, reflecting cosmic harmony."""
    return signal * exp(-damp_factor * np.arange(len(signal)))

def dynamic_weights(time_phase):
    """Cyclic weighting for T/I/F with Inuit reciprocity."""
    scale = 0.1
    return {
        "T": 0.5 + scale * np.sin(2 * pi * time_phase),  # Alignment with cosmos
        "I": 0.3 - scale * np.cos(2 * pi * time_phase),  # Reciprocity pause
        "F": 0.2 + scale * np.sin(pi * time_phase)       # Balance check
    }

def phase_lock_recursive(phase_history):
    """Recursive phase locking with adaptive damping."""
    locked = 0.0
    alpha = 0.7  # Fixed smoothing factor
    for phi in phase_history:
        locked = alpha * phi + (1 - alpha) * locked
    std_dev = np.std(phase_history)
    damp_factor = 0.5 + 0.2 * std_dev  # Linear adjustment
    return locked % (2 * pi), min(0.7, max(0.3, damp_factor))
import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Satellite, Radio, Zap, AlertTriangle } from 'lucide-react';

// Orbital mechanics constants
const EARTH_RADIUS = 6371; // km
const GEO_ALTITUDE = 35786; // km
const LEO_ALTITUDE = 550; // km
const ORBITAL_PERIODS = {
  GEO: 86400, // seconds (24 hours)
  LEO: 5400   // seconds (~90 minutes)
};

// FPT coherence parameters
const TOFT_FREQ = 79; // Hz
const MAX_HANDOFF_DISTANCE = 40000; // km
const COHERENCE_DECAY_RATE = 0.00002; // per km

// Satellite state
class Satellite {
  constructor(id, type, angle, color) {
    this.id = id;
    this.type = type; // 'GEO' or 'LEO'
    this.angle = angle; // radians
    this.color = color;
    this.altitude = type === 'GEO' ? GEO_ALTITUDE : LEO_ALTITUDE;
    this.orbitalRadius = EARTH_RADIUS + this.altitude;
    this.period = ORBITAL_PERIODS[type];
    this.isActive = false;
  }

  getPosition() {
    return {
      x: this.orbitalRadius * Math.cos(this.angle),
      y: this.orbitalRadius * Math.sin(this.angle)
    };
  }

  update(dt) {
    const angularVelocity = (2 * Math.PI) / this.period;
    this.angle += angularVelocity * dt;
    if (this.angle > 2 * Math.PI) this.angle -= 2 * Math.PI;
  }
}

// FPT Coherence Calculator
class FPTCoherence {
  static calculate(distance, signalAge, linkQuality = 1.0) {
    // ISST formula: S(r,H,C) = E0 * C / (r² * (1 + αH))
    const E0 = 1.0;
    const alpha = 0.001; // history decay
    const r_normalized = distance / 1000; // normalize to manageable scale
    
    const isst = (E0 * linkQuality) / (Math.pow(r_normalized, 2) * (1 + alpha * signalAge));
    
    // Coherence based on TOFT resonance
    const distanceCoherence = Math.exp(-distance * COHERENCE_DECAY_RATE);
    const toftCoherence = Math.cos(2 * Math.PI * TOFT_FREQ * signalAge / 1000) * 0.5 + 0.5;
    
    // Combined coherence metric
    const coherence = Math.min(isst * distanceCoherence * toftCoherence, 1.0);
    
    return {
      coherence: Math.max(0, coherence),
      isst,
      distanceCoherence,
      toftCoherence,
      distance
    };
  }

  static getResonanceState(coherence) {
    if (coherence >= 0.7) return { state: 'COHERENT', color: '#10b981' };
    if (coherence >= 0.4) return { state: 'DEGRADED', color: '#f59e0b' };
    if (coherence >= 0.2) return { state: 'CHAOTIC', color: '#ef4444' };
    return { state: 'OFFLINE', color: '#6b7280' };
  }
}

// Link between satellites
class Link {
  constructor(sat1, sat2) {
    this.sat1 = sat1;
    this.sat2 = sat2;
    this.age = 0;
    this.handoffActive = false;
  }

  getDistance() {
    const p1 = this.sat1.getPosition();
    const p2 = this.sat2.getPosition();
    return Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
  }

  update(dt) {
    this.age += dt;
    const distance = this.getDistance();
    this.handoffActive = distance < MAX_HANDOFF_DISTANCE && 
                        (this.sat1.isActive || this.sat2.isActive);
  }

  getCoherence() {
    return FPTCoherence.calculate(this.getDistance(), this.age);
  }
}

// Main Simulator Component
const HybridOrbitalSimulator = () => {
  const canvasRef = useRef(null);
  const [isRunning, setIsRunning] = useState(false);
  const [simTime, setSimTime] = useState(0);
  const [timeScale, setTimeScale] = useState(20); // simulation speed multiplier
  
  // Initialize satellites
  const [satellites] = useState(() => [
    new Satellite('GEO-1', 'GEO', 0, '#3b82f6'),
    new Satellite('GEO-2', 'GEO', Math.PI, '#3b82f6'),
    new Satellite('LEO-1', 'LEO', 0, '#8b5cf6'),
    new Satellite('LEO-2', 'LEO', Math.PI / 2, '#8b5cf6'),
    new Satellite('LEO-3', 'LEO', Math.PI, '#8b5cf6'),
    new Satellite('LEO-4', 'LEO', 3 * Math.PI / 2, '#8b5cf6')
  ]);
  
  const [links, setLinks] = useState([]);
  const [selectedSat, setSelectedSat] = useState(null);
  const [metrics, setMetrics] = useState({});

  // Initialize links (GEO to all LEO)
  useEffect(() => {
    const geoSats = satellites.filter(s => s.type === 'GEO');
    const leoSats = satellites.filter(s => s.type === 'LEO');
    const newLinks = [];
    
    geoSats.forEach(geo => {
      leoSats.forEach(leo => {
        newLinks.push(new Link(geo, leo));
      });
    });
    
    setLinks(newLinks);
    satellites[0].isActive = true; // Activate first GEO
    setSelectedSat(satellites[0]);
  }, []);

  // Simulation loop
  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(() => {
      const dt = 0.1 * timeScale; // time step
      
      // Update satellites
      satellites.forEach(sat => sat.update(dt));
      
      // Update links
      links.forEach(link => link.update(dt));
      
      // Calculate metrics
      const activeLinks = links.filter(l => l.handoffActive);
      const coherenceValues = activeLinks.map(l => l.getCoherence().coherence);
      const avgCoherence = coherenceValues.length > 0 
        ? coherenceValues.reduce((a, b) => a + b, 0) / coherenceValues.length 
        : 0;
      
      setMetrics({
        activeLinks: activeLinks.length,
        avgCoherence: avgCoherence.toFixed(3),
        totalLinks: links.length,
        activeSatellites: satellites.filter(s => s.isActive).length
      });
      
      setSimTime(t => t + dt);
    }, 100);

    return () => clearInterval(interval);
  }, [isRunning, timeScale, satellites, links]);

  // Drawing
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const scale = 0.008; // km to pixels

    // Clear
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, width, height);

    // Draw Earth
    ctx.beginPath();
    ctx.arc(centerX, centerY, EARTH_RADIUS * scale, 0, 2 * Math.PI);
    ctx.fillStyle = '#1e40af';
    ctx.fill();
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw orbital paths
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 1;
    
    // GEO orbit
    ctx.beginPath();
    ctx.arc(centerX, centerY, (EARTH_RADIUS + GEO_ALTITUDE) * scale, 0, 2 * Math.PI);
    ctx.stroke();
    
    // LEO orbit
    ctx.beginPath();
    ctx.arc(centerX, centerY, (EARTH_RADIUS + LEO_ALTITUDE) * scale, 0, 2 * Math.PI);
    ctx.stroke();

    // Draw links with coherence visualization
    links.forEach(link => {
      if (!link.handoffActive) return;
      
      const p1 = link.sat1.getPosition();
      const p2 = link.sat2.getPosition();
      const coherenceData = link.getCoherence();
      const resonance = FPTCoherence.getResonanceState(coherenceData.coherence);
      
      ctx.beginPath();
      ctx.moveTo(centerX + p1.x * scale, centerY + p1.y * scale);
      ctx.lineTo(centerX + p2.x * scale, centerY + p2.y * scale);
      ctx.strokeStyle = resonance.color;
      ctx.lineWidth = 2 + coherenceData.coherence * 3;
      ctx.globalAlpha = 0.3 + coherenceData.coherence * 0.5;
      ctx.stroke();
      ctx.globalAlpha = 1.0;

      // Draw TOFT pulse animation
      if (coherenceData.coherence > 0.5) {
        const pulsePos = (simTime % 2) / 2; // 0 to 1
        const px = p1.x + (p2.x - p1.x) * pulsePos;
        const py = p1.y + (p2.y - p1.y) * pulsePos;
        
        ctx.beginPath();
        ctx.arc(centerX + px * scale, centerY + py * scale, 3, 0, 2 * Math.PI);
        ctx.fillStyle = resonance.color;
        ctx.fill();
      }
    });

    // Draw satellites
    satellites.forEach(sat => {
      const pos = sat.getPosition();
      const x = centerX + pos.x * scale;
      const y = centerY + pos.y * scale;
      const size = sat.type === 'GEO' ? 8 : 6;

      // Satellite body
      ctx.beginPath();
      ctx.arc(x, y, size, 0, 2 * Math.PI);
      ctx.fillStyle = sat.isActive ? sat.color : '#475569';
      ctx.fill();
      ctx.strokeStyle = sat === selectedSat ? '#fbbf24' : '#1e293b';
      ctx.lineWidth = sat === selectedSat ? 3 : 1;
      ctx.stroke();

      // Active indicator
      if (sat.isActive) {
        ctx.beginPath();
        ctx.arc(x, y, size + 4 + Math.sin(simTime * 3) * 2, 0, 2 * Math.PI);
        ctx.strokeStyle = sat.color;
        ctx.lineWidth = 2;
        ctx.globalAlpha = 0.5;
        ctx.stroke();
        ctx.globalAlpha = 1.0;
      }

      // Label
      ctx.fillStyle = '#e2e8f0';
      ctx.font = '10px monospace';
      ctx.fillText(sat.id, x + size + 5, y + 4);
    });
  }, [simTime, satellites, links, selectedSat]);

  const handleReset = () => {
    setIsRunning(false);
    setSimTime(0);
    satellites.forEach((sat, i) => {
      sat.angle = i * (2 * Math.PI / satellites.length);
      sat.isActive = i === 0;
    });
    links.forEach(link => link.age = 0);
    setSelectedSat(satellites[0]);
  };

  const toggleSatellite = (sat) => {
    sat.isActive = !sat.isActive;
    setSelectedSat(sat);
  };

  // Get coherence for selected satellite
  const getSelectedCoherence = () => {
    if (!selectedSat) return null;
    
    const relevantLinks = links.filter(l => 
      (l.sat1 === selectedSat || l.sat2 === selectedSat) && l.handoffActive
    );
    
    if (relevantLinks.length === 0) return null;
    
    return relevantLinks.map(l => ({
      partner: l.sat1 === selectedSat ? l.sat2.id : l.sat1.id,
      ...l.getCoherence()
    }));
  };

  const selectedCoherence = getSelectedCoherence();

  return (
    <div className="w-full h-screen bg-slate-900 text-slate-100 p-4 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Radio className="text-blue-400" />
          Hybrid Orbital Simulator
          <span className="text-sm text-slate-400 font-normal">with FPT Coherence</span>
        </h1>
        
        <div className="flex gap-2">
          <button
            onClick={() => setIsRunning(!isRunning)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            {isRunning ? <Pause size={18} /> : <Play size={18} />}
            {isRunning ? 'Pause' : 'Start'}
          </button>
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
          >
            <RotateCcw size={18} />
            Reset
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 flex-1">
        {/* Main visualization */}
        <div className="col-span-3 bg-slate-800 rounded-lg p-4">
          <canvas
            ref={canvasRef}
            width={900}
            height={700}
            className="w-full h-full"
          />
        </div>

        {/* Control panel */}
        <div className="space-y-4 overflow-y-auto">
          {/* Metrics */}
          <div className="bg-slate-800 rounded-lg p-4 space-y-3">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Zap className="text-yellow-400" size={18} />
              System Metrics
            </h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Sim Time:</span>
                <span className="font-mono">{(simTime / 60).toFixed(1)}m</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Active Links:</span>
                <span className="font-mono">{metrics.activeLinks}/{metrics.totalLinks}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Avg Coherence:</span>
                <span className="font-mono">{metrics.avgCoherence}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Active Sats:</span>
                <span className="font-mono">{metrics.activeSatellites}</span>
              </div>
            </div>
          </div>

          {/* Time scale */}
          <div className="bg-slate-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold mb-2">Time Scale: {timeScale}x</h3>
            <input
              type="range"
              min="1"
              max="100"
              value={timeScale}
              onChange={(e) => setTimeScale(Number(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Satellite controls */}
          <div className="bg-slate-800 rounded-lg p-4">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-3">
              <Satellite className="text-purple-400" size={18} />
              Satellites
            </h2>
            <div className="space-y-2">
              {satellites.map(sat => (
                <button
                  key={sat.id}
                  onClick={() => toggleSatellite(sat)}
                  className={`w-full text-left p-2 rounded transition-colors ${
                    sat === selectedSat ? 'bg-slate-700' : 'bg-slate-900'
                  } hover:bg-slate-700`}
                >
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: sat.isActive ? sat.color : '#475569' }}
                      />
                      <span className="font-mono text-sm">{sat.id}</span>
                    </span>
                    <span className="text-xs text-slate-400">{sat.type}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* FPT Coherence Details */}
          {selectedSat && selectedCoherence && selectedCoherence.length > 0 && (
            <div className="bg-slate-800 rounded-lg p-4">
              <h2 className="text-lg font-semibold mb-3">
                FPT Coherence: {selectedSat.id}
              </h2>
              <div className="space-y-3">
                {selectedCoherence.map((data, i) => {
                  const resonance = FPTCoherence.getResonanceState(data.coherence);
                  return (
                    <div key={i} className="bg-slate-900 rounded p-3 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-mono">{data.partner}</span>
                        <span 
                          className="text-xs font-bold px-2 py-1 rounded"
                          style={{ backgroundColor: resonance.color + '33', color: resonance.color }}
                        >
                          {resonance.state}
                        </span>
                      </div>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Coherence:</span>
                          <span className="font-mono">{data.coherence.toFixed(3)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Distance:</span>
                          <span className="font-mono">{Math.round(data.distance)} km</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">ISST:</span>
                          <span className="font-mono">{data.isst.toFixed(4)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">TOFT 79Hz:</span>
                          <span className="font-mono">{data.toftCoherence.toFixed(3)}</span>
                        </div>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-2">
                        <div
                          className="h-2 rounded-full transition-all duration-300"
                          style={{
                            width: `${data.coherence * 100}%`,
                            backgroundColor: resonance.color
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Legend */}
          <div className="bg-slate-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold mb-2">Resonance States</h3>
            <div className="space-y-2 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-emerald-500" />
                <span>COHERENT (≥0.7)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-amber-500" />
                <span>DEGRADED (0.4-0.7)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span>CHAOTIC (0.2-0.4)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-slate-500" />
                <span>OFFLINE (&lt;0.2)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HybridOrbitalSimulator;