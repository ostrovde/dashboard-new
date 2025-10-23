import React from "react";

export default function MapsSection({ fullPage = false }) {
  return (
    <div className={fullPage ? "" : "card"}>
      <h3 style={{ marginBottom: "1rem", color: "#1e293b" }}>Карта испытаний</h3>
      <div style={{
        height: fullPage ? "600px" : "400px",
        background: "linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%)",
        borderRadius: "8px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        border: "2px dashed #4CAF50",
        flexDirection: "column",
        gap: "1rem",
        color: "#2e7d32"
      }}>
        <div style={{ fontSize: "3rem" }}>🗺️</div>
        <div style={{ textAlign: "center" }}>
          <p style={{ fontSize: "1.2rem", fontWeight: "600", marginBottom: "0.5rem" }}>
            Интерактивная карта
          </p>
          <p>Интеграция с Leaflet и React-Leaflet</p>
          <p style={{ fontSize: "0.9rem", opacity: 0.8, marginTop: "0.5rem" }}>
            Показывает локации испытаний с данными урожайности
          </p>
        </div>
      </div>
    </div>
  );
}