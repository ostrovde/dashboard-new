import React from "react";

export default function KPISection({ data }) {
  const kpis = [
    {
      label: "Средняя урожайность",
      value: data.length ? (data.reduce((sum, row) => sum + row.yield, 0) / data.length).toFixed(1) + " ц/га" : "—",
      icon: "🌾"
    },
    {
      label: "Средняя масличность",
      value: data.filter(row => row.oil > 0).length ? 
        (data.filter(row => row.oil > 0).reduce((sum, row) => sum + row.oil, 0) / data.filter(row => row.oil > 0).length).toFixed(1) + "%" : "—",
      icon: "🫒"
    },
    {
      label: "Количество локаций",
      value: new Set(data.map(row => row.location)).size,
      icon: "📍"
    },
    {
      label: "Количество гибридов",
      value: new Set(data.map(row => row.hybrid)).size,
      icon: "🧬"
    }
  ];

  return (
    <div className="kpi-grid">
      {kpis.map((kpi, index) => (
        <div key={index} className="kpi-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div className="kpi-label">{kpi.label}</div>
            <span style={{ fontSize: "1.5rem" }}>{kpi.icon}</span>
          </div>
          <div className="kpi-value">{kpi.value}</div>
        </div>
      ))}
    </div>
  );
}