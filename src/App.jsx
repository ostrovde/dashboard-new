// 🌻 RayAgro Dashboard — Phase 2 UI
import React, { useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { motion } from "framer-motion";

export default function App() {
  const [selected, setSelected] = useState(null);

  const mockPoints = [
    { id: 1, name: "Safari", lat: 47.2, lng: 39.7, yield: 42 },
    { id: 2, name: "Gektor", lat: 48.3, lng: 41.9, yield: 38 },
    { id: 3, name: "Harizma", lat: 50.1, lng: 36.2, yield: 46 },
  ];

  const colors = (y) => (y > 45 ? "#3cb371" : y > 40 ? "#f6c500" : "#e63946");

  return (
    <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", height: "100vh" }}>
      {/* Sidebar */}
      <motion.aside
        initial={{ x: -60, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{
          background: "#f5f5f7",
          borderRight: "1px solid #ddd",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
        }}
      >
        <div>
          <h2 style={{ color: "#4c73c1", marginBottom: "10px" }}>🌻 RayAgro Dashboard</h2>
          <p style={{ fontSize: "14px", color: "#555" }}>Фаза 2 — интерфейс карт и фильтров</p>
        </div>
        <div style={{ fontSize: "12px", color: "#777" }}>© RayAgro 2025</div>
      </motion.aside>

      {/* Main Content */}
      <div style={{ display: "grid", gridTemplateRows: "1fr 80px", height: "100%" }}>
        {/* Two maps side by side */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr" }}>
          {[0, 1].map((idx) => (
            <MapContainer
              key={idx}
              center={[48, 40]}
              zoom={6}
              scrollWheelZoom={false}
              style={{ height: "100%", width: "100%" }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution="&copy; OpenStreetMap contributors"
              />
              {mockPoints.map((p) => (
                <CircleMarker
                  key={p.id}
                  center={[p.lat, p.lng]}
                  pathOptions={{ color: colors(p.yield) }}
                  radius={10}
                  eventHandlers={{
                    click: () => setSelected(p),
                  }}
                >
                  <Tooltip>
                    <strong>{p.name}</strong>
                    <br />{p.yield} ц/га
                  </Tooltip>
                </CircleMarker>
              ))}
            </MapContainer>
          ))}
        </div>

        {/* Bottom filter bar */}
        <motion.footer
          initial={{ y: 60, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.4 }}
          style={{
            background: "#fff",
            borderTop: "1px solid #ddd",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-around",
            fontSize: "14px",
            color: "#333",
          }}
