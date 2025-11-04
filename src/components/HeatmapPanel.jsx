import React from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";

function colorByYield(y) {
  if (isNaN(y)) return "#ccc";
  const t = Math.max(0, Math.min(1, (y - 20) / 40)); // 20..60 → 0..1
  const r = Math.round(255 * t);
  const g = Math.round(180 * (1 - t));
  return `rgb(${r},${g},80)`;
}

export default function HeatmapPanel({ rows }) {
  return (
    <MapContainer center={[50, 40]} zoom={5} style={{ height: "55vh", borderRadius: "16px" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {rows.map((r, i) => (
        <CircleMarker
          key={i}
          center={[r.Lat, r.Lng]}
          radius={6}
          color={colorByYield(r.Yield)}
          fillColor={colorByYield(r.Yield)}
          fillOpacity={0.8}
        >
          <Popup>
            <b>{r.Hybrid}</b>
            <br />
            Урожайность: {r.Yield} ц/га<br />
            Масличность: {r.Oil || "-"}%
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
