import React, { useMemo } from "react";

/**
 * ScaleRuler
 * Props:
 *  - payload: object returned from /scale/annotate
 *  - width (px), height (px)
 */
export default function ScaleRuler({ payload, width = 640, height = 80 }) {
  if (!payload) return null;

  const { band_index, floor_marker, top_marker, length_human } = payload;
  const N = top_marker.band_index;

  const x = useMemo(() => {
    // simple linear placement across N bands
    const pct = (band_index / N);
    return Math.max(0, Math.min(1, pct)) * width;
  }, [band_index, width, N]);

  const floorLabel = `${floor_marker.name}`;
  const topLabel = `${top_marker.name}`;
  const currentLabel = `${length_human.value} ${length_human.unit}`;

  return (
    <svg width={width} height={height} className="rounded-2xl shadow border">
      {/* axis */}
      <line x1="16" y1={height/2} x2={width-16} y2={height/2} strokeWidth="2" />

      {/* floor tick */}
      <line x1="16" y1={height/2 - 14} x2="16" y2={height/2 + 14} strokeWidth="2" />
      <text x="16" y={height/2 + 28} textAnchor="start" fontSize="12">{floorLabel}</text>

      {/* top tick */}
      <line x1={width-16} y1={height/2 - 14} x2={width-16} y2={height/2 + 14} strokeWidth="2" />
      <text x={width-16} y={height/2 + 28} textAnchor="end" fontSize="12">{topLabel}</text>

      {/* current marker */}
      <circle cx={16 + (width-32) * (band_index / N)} cy={height/2} r="6" />
      <text x={x} y={height/2 - 18} textAnchor="middle" fontWeight="600" fontSize="12">
        n={band_index} • {currentLabel}
      </text>
    </svg>
  );
}
