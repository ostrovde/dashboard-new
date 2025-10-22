import React, { useEffect, useRef, useState } from "react";
import { parseCSV } from "./csv.js";
import "leaflet/dist/leaflet.css";

/**
 * Реальная карта Leaflet:
 * - Фиксированная высота контейнера (не меняется размер).
 * - Левый блок: точки по GEO (public/data/geo.csv).
 * - Правый блок: «тепловая» заглушка с градиентом урожайности + легенда.
 * - Graceful fallback: если данных нет — показываем текст, но UI не падает.
 */

function Legend() {
  const gradStyle = {
    background: "linear-gradient(90deg, #c0392b 0%, #f1c40f 50%, #27ae60 100%)",
    height: 10,
    borderRadius: 6,
  };
  return (
    <div style={{ marginTop: 8 }}>
      <div style={gradStyle} />
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginTop: 4, color: "#666" }}>
        <span>низкая</span>
        <span>средняя</span>
        <span>высокая</span>
      </div>
    </div>
  );
}

export default function MapView() {
  const [geoRows, setGeoRows] = useState(null);   // null = не загружено; [] = пусто
  const [kpiRows, setKpiRows] = useState(null);
  const [error, setError] = useState("");

  // контейнер и инстанс карты
  const mapEl = useRef(null);
  const mapRef = useRef(null);

  // 1) Загружаем CSV из public/data
  useEffect(() => {
    let alive = true;
    async function load() {
      try {
        const [geoText, kpiText] = await Promise.all([
          fetch("/data/geo.csv").then(r => r.ok ? r.text() : ""),
          fetch("/data/kpi.csv").then(r => r.ok ? r.text() : "")
        ]);
        if (!alive) return;
        setGeoRows(geoText ? parseCSV(geoText).rows : []);
        setKpiRows(kpiText ? parseCSV(kpiText).rows : []);
      } catch (e) {
        if (!alive) return;
        setError(String(e));
        setGeoRows([]); setKpiRows([]);
      }
    }
    load();
    return () => { alive = false; };
  }, []);

  const hasPoints = Array.isArray(geoRows) && geoRows.length > 0;
  const hasYield  = Array.isArray(kpiRows) && kpiRows.length > 0;

  // 2) Инициализируем Leaflet (динамический импорт, чтобы не ломать сборку)
  useEffect(() => {
    let L;
    let markers = [];
    async function init() {
      const mod = await import("leaflet");
      L = mod.default || mod;

      // лениво создаём карту один раз
      if (!mapRef.current && mapEl.current) {
        mapRef.current = L.map(mapEl.current, {
          center: [55.751244, 37.618423], // Москва как дефолт
          zoom: 5,
          zoomControl: true,
          attributionControl: false,
        });
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          maxZoom: 18
        }).addTo(mapRef.current);
      }

      // чистим предыдущие слои-точки
      markers.forEach(m => m.remove());
      markers = [];

      // добавляем точки, если есть
      if (mapRef.current && hasPoints) {
        const group = L.featureGroup();
        for (const r of geoRows) {
          const lat = parseFloat(r["Широта"]);
          const lon = parseFloat(r["Долгота"]);
          if (Number.isFinite(lat) && Number.isFinite(lon)) {
            const m = L.circleMarker([lat, lon], { radius: 5, weight: 1 });
            m.bindTooltip(`${r["Контрагент"] ?? "?"} (${r["Год"] ?? "?"})`);
            m.addTo(group);
          }
        }
        if (group.getLayers().length) {
          group.addTo(mapRef.current);
          mapRef.current.fitBounds(group.getBounds().pad(0.25));
        }
      }
    }
    init();
    // Ничего не возвращаем: Leaflet сам управляет DOM внутри контейнера
  }, [hasPoints, geoRows]);

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: 16,
      minHeight: 360,
      padding: 16
    }}>
      <section style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, background: "#fff" }}>
        <h3 style={{ margin: 0, marginBottom: 8 }}>Точки (бренд/гибрид)</h3>

        {!geoRows && <div style={{ color: "#666" }}>Загрузка…</div>}
        {geoRows && !hasPoints && (
          <div style={{ color: "#666" }}>
            Данных нет — UI работает без падений. Загрузятся, когда появится <code>public/data/geo.csv</code>.
          </div>
        )}

        {/* Контейнер фиксированной высоты — размер не меняется */}
        <div
          ref={mapEl}
          style={{
            height: 280,
            border: "1px solid #e5e7eb",
            borderRadius: 12,
            overflow: "hidden",
            marginTop: 8
          }}
        />
      </section>

      <section style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, background: "#fff" }}>
        <h3 style={{ margin: 0, marginBottom: 8 }}>Градиент по урожайности</h3>

        {!kpiRows && <div style={{ color: "#666" }}>Загрузка…</div>}
        {kpiRows && !hasYield && <div style={{ color: "#666" }}>
          Данных нет — UI работает без падений. Загрузятся, когда появится <code>public/data/kpi.csv</code>.
        </div>}

        {hasYield && (
          <div>
            <div style={{ fontSize: 13, color: "#666", marginBottom: 8 }}>
              Пример-данные KPI: {kpiRows.length} строк
            </div>
            <div style={{
              height: 220,
              border: "1px dashed #ddd",
              borderRadius: 8,
              display: "grid",
              placeItems: "center",
              background: "linear-gradient(90deg, #c0392b 0%, #f1c40f 50%, #27ae60 100%)",
              opacity: 0.25
            }}>
              <span style={{ color: "#555", background: "rgba(255,255,255,0.8)", padding: "2px 6px", borderRadius: 6 }}>
                Здесь позже будет реальный расчет бинов/heatmap
              </span>
            </div>
            <Legend />
          </div>
        )}
      </section>

      {error && (
        <div style={{ gridColumn: "1 / span 2", color: "#c0392b" }}>
          Ошибка загрузки: {error}
        </div>
      )}
    </div>
  );
}
