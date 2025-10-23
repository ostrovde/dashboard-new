import React, { useState, useEffect } from "react";
import Dashboard from "./components/Dashboard.jsx";
import "./index.css";

export default function App() {
  const updateData = () => {
    console.log("Updating data from Google Sheets...");
    alert("Данные обновляются из Google Sheets!");
  };

  return (
    <div className="app-root">
      <header className="app-header">
        <div style={
          maxWidth: "1200px",
          margin: "0 auto",
          width: "100%"
        }>
          <h1>RayAgro Yield Dashboard</h1>
          <p className="app-sub">Расширенный дашборд урожайности с аналитикой</p>
          <div className="header-actions">
            <button onClick={updateData} className="btn-primary">
              Обновить данные
            </button>
            <button className="btn-primary">
              Экспорт отчетов
            </button>
            <button className="btn-primary">
              Настройки
            </button>
          </div>
        </div>
      </header>
      <main>
        <Dashboard />
      </main>
      <footer style={
        background: "#1e293b",
        color: "white",
        padding: "2rem",
        textAlign: "center",
        marginTop: "auto"
      }>
        <div style={
          maxWidth: "1200px",
          margin: "0 auto",
          opacity: 0.8
        }>
          <p>RayAgro Yield Dashboard • Создан агентом для Issue #35</p>
          <p style={ fontSize: "0.9rem", marginTop: "0.5rem" }>
            2025-10-23 17:33:35
          </p>
        </div>
      </footer>
    </div>
  );
}