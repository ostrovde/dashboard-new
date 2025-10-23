import React from "react";
import MapView from "./components/MapView.jsx";
import "./index.css";

export default function updateData() {
  console.log("Updating data from Google Sheets...");
  alert("Данные обновляются из Google Sheets!");
}

function App() {
  return (
    <div className="app-root">
      <header className="app-header">
        <h1>RayAgro Yield Dashboard</h1>
        <p className="app-sub">Каркас карты с устойчивыми заглушками</p>
      </header>
      <main>
        <MapView />
      </main>
    
      <button onClick={updateData} style={{
        padding: "10px 20px", 
        backgroundColor: "#4CAF50", 
        color: "white", 
        border: "none", 
        borderRadius: "5px",
        margin: "10px",
        cursor: "pointer"
      }}>
        🔄 Обновить данные
      </button>
    </div>
  );
}
