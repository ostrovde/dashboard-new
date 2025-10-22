import React from "react";
import MapView from "./components/MapView.jsx";
import "./index.css";

export default function App() {
  return (
    <div className="app-root">
      <header className="app-header">
        <h1>RayAgro Yield Dashboard</h1>
        <p className="app-sub">Каркас карты с устойчивыми заглушками</p>
      </header>
      <main>
        <MapView />
      </main>
    </div>
  );
}
