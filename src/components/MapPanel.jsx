import React from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";

function colorByHybrid(h) {
  const hash = [...(h || "")].reduce((a, c) => a + c.charCodeAt(0), 0);
  const r = (hash * 29) % 255, g = (hash * 59) % 255, b = (hash * 97) % 255;
  return `rgb(${r},${g},${b})`;
}

export default function MapPanel({ rows }) {
  return (
    <MapContainer center={[50, 40]} zoom={5} style={{ height: "55vh", borderRadius: "16px" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {rows.map((r, i) => (
        <CircleMarker
          key={i}
          center={[r.Lat, r.Lng]}
          radius={6}
          color={colorByHybrid(r.Hybrid)}
          fillColor={colorByHybrid(r.Hybrid)}
          fillOpacity={0.7}
        >
          <Popup>
            <b>{r.Hybrid}</b><br />
            Урожайность: {r.Yield} ц/га<br />
            {r.Region} {r.Year}
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
