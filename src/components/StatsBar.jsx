import React, { useMemo } from "react";

export default function MetricsBar({ rows = [] }) {
  const m = useMemo(() => {
    const total = rows.length;
    const hybrids = new Set(rows.map(r => r.Hybrid)).size;
    const regions = new Set(rows.map(r => r.Region)).size;
    const valid = rows.filter(r => r.Yield > 0);
    const avg = valid.length ? (valid.reduce((s, r) => s + r.Yield, 0) / valid.length).toFixed(1) : "0.0";
    const maxy = valid.length ? Math.max(...valid.map(r => r.Yield)).toFixed(1) : "0.0";
    const oils = rows.filter(r => !isNaN(r.Oil) && r.Oil > 0);
    const maxo = oils.length ? Math.max(...oils.map(r => r.Oil)).toFixed(1) : "0.0";
    return { total, hybrids, regions, avg, maxy, maxo };
  }, [rows]);

  const card = (title, value) => (
    <div style={{
      background: "linear-gradient(180deg,#6a85ff,#7ed6ff)",
      borderRadius: "16px", padding: "10px 12px", color: "#fff",
      fontWeight: 600, boxShadow: "0 4px 12px rgba(0,0,0,0.1)"
    }}>
      {title}<br /><span style={{ fontSize: 20 }}>{value}</span>
    </div>
  );

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "repeat(6,1fr)",
      gap: "12px",
      margin: "16px 20px"
    }}>
      {card("Записей", m.total)}
      {card("Регионов", m.regions)}
      {card("Гибридов", m.hybrids)}
      {card("Средн. урожай, ц/га", m.avg)}
      {card("Макс. урожай, ц/га", m.maxy)}
      {card("Макс. масличн., %", m.maxo)}
    </div>
  );
}
