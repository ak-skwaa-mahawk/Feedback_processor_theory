// frontend/components/ScaleTable.jsx
import React, { useEffect, useState } from "react";

export default function ScaleTable({ n0 = 60, n1 = 70, sig = 4 }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`/scale/table?n0=${n0}&n1=${n1}&sig=${sig}`)
      .then(r => r.json())
      .then(setData)
      .catch(console.error);
  }, [n0, n1, sig]);

  if (!data) return null;

  return (
    <div className="p-3 rounded-2xl shadow border">
      <div className="mb-2 font-semibold">
        Scale Ladder (n={data.n0}…{data.n1})
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left">
            <th className="py-1">Band</th>
            <th className="py-1">Length (m, raw)</th>
            <th className="py-1">Human</th>
          </tr>
        </thead>
        <tbody>
          {data.rows.map((r) => (
            <tr key={r.band} className="border-t">
              <td className="py-1">{r.band}</td>
              <td className="py-1">{r.length_m}</td>
              <td className="py-1">{r.length_human.value} {r.length_human.unit}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
