import React, { useEffect, useRef, useState, useMemo } from "react";
import { parseCSV } from "./csv.js";
import { redYellowGreen, equalBreaks, binIndex } from "./scale.js";
import "leaflet/dist/leaflet.css";

/**
 * Лево: реальная карта Leaflet с точками из public/data/geo.csv (как было).
 * Право: бинированная «тепловая» панель по урожайности из public/data/kpi.csv.
 * - размер контейнеров фиксирован (карта 280px, тепловая 220px);
 * - UI не падает при отсутствии данных (graceful fallback).
 */

function Legend({ edges }) {
  if (!edges || edges.length < 2) {
    return (
      <div style={{ marginTop: 8 }}>
        <div style={{ height: 10, borderRadius: 6, background: "linear-gradient(90deg,#c0392b,#f1c40f,#27ae60)" }} />
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginTop: 4, color: "#666" }}>
          <span>низкая</span><span>средняя</span><span>высокая</span>
        </div>
      </div>
    );
  }
  const bins = edges.length - 1;
  return (
    <div style={{ marginTop: 10 }}>
      <div style={{ display: "grid", gridTemplateColumns: `repeat(${bins}, 1fr)`, gap: 4 }}>
        {Array.from({ length: bins }).map((_, i) => {
          const t = bins === 1 ? 1 : i / (bins - 1);
          return <div key={i} style={{ height: 10, borderRadius: 4, background: redYellowGreen(t) }} />;
        })}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: `repeat(${bins}, 1fr)`, gap: 4, marginTop: 4, fontSize: 11, color: "#666" }}>
        {Array.from({ length: bins }).map((_, i) => {
          const lo = edges[i], hi = edges[i + 1];
          const label = `${lo.toFixed(1)}–${hi.toFixed(1)}`;
          return <div key={i} style={{ textAlign: "center" }}>{label}</div>;
        })}
      </div>
    </div>
  );
}

export default function MapView() {
  const [geoRows, setGeoRows] = useState(null); // null = не загружено; [] = пусто
  const [kpiRows, setKpiRows] = useState(null);
  const [error, setError] = useState("");

  // Leaflet карта
  const mapEl = useRef(null);
  const mapRef = useRef(null);

  // грузим CSV из public/data
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

  // извлекаем массив урожайностей из kpiRows
  const yields = useMemo(() => {
    if (!hasYield) return [];
    const pick = (obj, keys) => {
      for (const k of keys) if (obj[k] != null) return obj[k];
      // кейс-инсensitive поиск
      const lower = Object.fromEntries(Object.entries(obj).map(([k,v]) => [k.toLowerCase(), v]));
      for (const k of keys.map(k => k.toLowerCase())) if (lower[k] != null) return lower[k];
      return null;
    };
    const keys = ["Урожайность_ц_га","Урожайность, ц/га","Yield_c_ha","Yield","yield","y"];
    const toNum = (v) => {
      if (v == null || v === "") return NaN;
      const n = parseFloat(String(v).replace(",", "."));
      return isFinite(n) ? n : NaN;
    };
    return kpiRows
      .map(r => toNum(pick(r, keys)))
      .filter(x => isFinite(x));
  }, [kpiRows, hasYield]);

  // считаем бины (равные интервалы) и делаем маленькую "тепловую" матрицу
  const { edges, matrix } = useMemo(() => {
    const bins = 6;
    if (!yields.length) return { edges: null, matrix: [] };
    const min = Math.min(...yields), max = Math.max(...yields);
    const edges = equalBreaks(min, max, bins);

    // заполняем матрицу 10x20 цветными ячейками (чисто визуально, без геопривязки)
    const rows = 10, cols = 20;
    const values = yields.length < rows * cols
      ? [...yields, ...Array(rows * cols - yields.length).fill(yields[yields.length - 1])]
      : yields.slice(0, rows * cols);
    const matrix = [];
    for (let r = 0; r < rows; r++) {
      const row = [];
      for (let c = 0; c < cols; c++) {
        const v = values[r * cols + c];
        const bi = binIndex(v, edges);
        const t = (edges.length - 2) === 0 ? 1 : bi / (edges.length - 2);
        row.push({ v, bi, color: redYellowGreen(t) });
      }
      matrix.push(row);
    }
    return { edges, matrix };
  }, [yields]);

  // инициализация Leaflet и точки
  useEffect(() => {
    let L;
    let group;
    async function init() {
      const mod = await import("leaflet");
      L = mod.default || mod;

      if (!mapRef.current && mapEl.current) {
        mapRef.current = L.map(mapEl.current, {
          center: [55.751244, 37.618423],
          zoom: 5,
          zoomControl: true,
          attributionControl: false,
        });
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          maxZoom: 18
        }).addTo(mapRef.current);
      }

      // удалим прежние маркеры (если были)
      if (group) group.remove();

      if (mapRef.current && hasPoints) {
        group = L.featureGroup();
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
  }, [hasPoints, geoRows]);

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: 16,
      minHeight: 360,
      padding: 16
    }}>
      {/* ЛЕВО: точки */}
      <section style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, background: "#fff" }}>
        <h3 style={{ margin: 0, marginBottom: 8 }}>Точки (бренд/гибрид)</h3>

        {!geoRows && <div style={{ color: "#666" }}>Загрузка…</div>}
        {geoRows && !hasPoints && (
          <div style={{ color: "#666" }}>
            Данных нет — UI работает без падений. Появятся при наличии <code>public/data/geo.csv</code>.
          </div>
        )}

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

      {/* ПРАВО: бинированная тепловая панель */}
      <section style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, background: "#fff" }}>
        <h3 style={{ margin: 0, marginBottom: 8 }}>Градиент по урожайности</h3>

        {!kpiRows && <div style={{ color: "#666" }}>Загрузка…</div>}
        {kpiRows && !hasYield && (
          <div style={{ color: "#666" }}>
            Данных нет — UI работает без падений. Появятся при наличии <code>public/data/kpi.csv</code>.
          </div>
        )}

        {hasYield && (
          <>
            <div style={{ fontSize: 13, color: "#666", marginBottom: 8 }}>
              Строк KPI: {kpiRows.length}
            </div>
            <div
              style={{
                height: 220,
                border: "1px solid #e5e7eb",
                borderRadius: 12,
                overflow: "hidden",
                padding: 8,
                background: "#fff"
              }}
            >
              {/* Матрица 10x20, фиксированная, чтобы размер не менялся */}
              <div style={{
                display: "grid",
                gridTemplateRows: "repeat(10, 1fr)",
                gap: 2,
                height: "100%"
              }}>
                {matrix.map((row, ri) => (
                  <div key={ri} style={{ display: "grid", gridTemplateColumns: "repeat(20, 1fr)", gap: 2 }}>
                    {row.map((cell, ci) => (
                      <div
                        key={ci}
                        title={isFinite(cell.v) ? `${cell.v.toFixed(1)} ц/га` : "—"}
                        style={{ height: "100%", background: cell.color, borderRadius: 2 }}
                      />
                    ))}
                  </div>
                ))}
              </div>
            </div>
            <Legend edges={edges} />
          </>
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
