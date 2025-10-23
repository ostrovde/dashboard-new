import React from "react";

export default function AnalyticsSection({ data }) {
  return (
    <div className="card">
      <h3 style={{ marginBottom: "1rem", color: "#1e293b" }}>Аналитика урожайности</h3>
      <div style={{
        height: "400px",
        background: "linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)",
        borderRadius: "8px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        border: "2px dashed #2196F3",
        flexDirection: "column",
        gap: "1rem",
        color: "#1565c0"
      }}>
        <div style={{ fontSize: "3rem" }}>📈</div>
        <div style={{ textAlign: "center" }}>
          <p style={{ fontSize: "1.2rem", fontWeight: "600", marginBottom: "0.5rem" }}>
            Графики и диаграммы
          </p>
          <p>Интеграция с Recharts</p>
          <p style={{ fontSize: "0.9rem", opacity: 0.8, marginTop: "0.5rem" }}>
            Визуализация данных урожайности и масличности
          </p>
        </div>
      </div>
    </div>
  );
}