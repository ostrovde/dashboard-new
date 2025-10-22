import React, { useEffect, useRef, useState, useMemo } from "react";
import { parseCSV } from "./csv.js";
import { redYellowGreen, equalBreaks, binIndex } from "./scale.js";
import "leaflet/dist/leaflet.css";

/**
 * Лево: карта Leaflet с точками из public/data/geo.csv.
 * Право: тепловая сетка по bbox и таблица метрик из public/data/kpi_stats.csv.
 * Размеры фиксированы, UI не падает без данных.
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
          const label = `${lo.toFixed(1)}–${hi.toFixed(1)} ц/га`;
          return <div key={i} style={{ textAlign: "center" }}>{label}</div>;
        })}
      </div>
    </div>
  );
}

function pick(row, keys) {
  const lower = Object.fromEntries(Object.entries(row).map(([k,v]) => [k.toLowerCase(), v]));
  for (const k of keys) {
    if (row[k] != null && row[k] !== "") return row[k];
    if (lower[k.toLowerCase()] != null && lower[k.toLowerCase()] !== "") return lower[k.toLowerCase()];
  }
  return "";
}
const toNum = (v) => {
  if (v == null || v === "") return NaN;
  const n = parseFloat(String(v).replace(",", "."));
  return Number.isFinite(n) ? n : NaN;
};

function StatsTable({ rows }) {
  if (!rows || !rows.length) return null;
  const sorted = [...rows].sort((a,b) => {
    const aw = toNum(a["WAASB_proxy"]) || 0, bw = toNum(b["WAASB_proxy"]) || 0;
    if (bw !== aw) return bw - aw;
    const acv = toNum(a["CV_%"]) || 0, bcv = toNum(b["CV_%"]) || 0;
    return acv - bcv;
  });

  return (
    <div style={{ marginTop: 12 }}>
      <div style={{ fontSize: 13, color: "#666", marginBottom: 6 }}>Метрики по контрагентам</div>
      <div style={{ maxHeight: 180, overflow: "auto", border: "1px solid #eee", borderRadius: 8 }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ background: "#fafafa" }}>
              <th style={{ textAlign: "left", padding: "6px 8px", borderBottom: "1px solid #eee" }}>Контрагент</th>
              <th style={{ textAlign: "right", padding: "6px 8px", borderBottom: "1px solid #eee" }}>Mean (ц/га)</th>
              <th style={{ textAlign: "right", padding: "6px 8px", borderBottom: "1px solid #eee" }}>SD (ц/га)</th>
              <th style={{ textAlign: "right", padding: "6px 8px", borderBottom: "1px solid #eee" }}>CV (%)</th>
              <th style={{ textAlign: "right", padding: "6px 8px", borderBottom: "1px solid #eee" }}>WAASB proxy</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((r, i) => (
              <tr key={i} style={{ borderBottom: "1px solid #f2f2f2" }}>
                <td style={{ padding: "6px 8px" }}>{r["Контрагент"]}</td>
                <td style={{ padding: "6px 8px", textAlign: "right" }}>{r["Mean_ц_га"]}</td>
                <td style={{ padding: "6px 8px", textAlign: "right" }}>{r["SD_ц_га"]}</td>
                <td style={{ padding: "6px 8px", textAlign: "right" }}>{r["CV_%"]}</td>
                <td style={{ padding: "6px 8px", textAlign: "right" }}>{r["WAASB_proxy"]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function MapView() {
  const [geoRows, setGeoRows] = useState(null);
  const [kpiRows, setKpiRows] = useState(null);
  const [statsRows, setStatsRows] = useState(null);
  const [error, setError] = useState("");

  // единственные ссылки Leaflet (без дублирования)
  const mapEl = useRef(null);
  const mapRef = useRef(null);

  // загрузка CSV
  useEffect(() => {
    let alive = true;
    async function load() {
      try {
        const [geoText, kpiText, statsText] = await Promise.all([
          fetch("/data/geo.csv").then(r => r.ok ? r.text() : ""),
          fetch("/data/kpi.csv").then(r => r.ok ? r.text() : ""),
          fetch("/data/kpi_stats.csv").then(r => r.ok ? r.text() : "")
        ]);
        if (!alive) return;
        setGeoRows(geoText ? parseCSV(geoText).rows : []);
        setKpiRows(kpiText ? parseCSV(kpiText).rows : []);
        setStatsRows(statsText ? parseCSV(statsText).rows : []);
      } catch (e) {
        if (!alive) return;
        setError(String(e));
        setGeoRows([]); setKpiRows([]); setStatsRows([]);
      }
    }
    load();
    return () => { alive = false; };
  }, []);

  const hasPoints = Array.isArray(geoRows) && geoRows.length > 0;
  const hasYield  = Array.isArray(kpiRows) && kpiRows.length > 0;

  // join geo×kpi
  const joined = useMemo(() => {
    if (!hasPoints || !hasYield) return [];
    const kpiMap = new Map();
    for (const r of kpiRows) {
      const contr = String(pick(r, ["Контрагент","contragent","client","Компания"])).trim();
      const year  = String(pick(r, ["Год","year"])).trim();
      const yld   = toNum(pick(r, ["Урожайность_ц_га","Урожайность, ц/га","Yield_c_ha","Yield","yield","y"]));
      if (Number.isFinite(yld) && yld > 0) {
        kpiMap.set(`${contr}||${year}`, yld);
      }
    }
    const pts = [];
    for (const r of geoRows) {
      const contr = String(pick(r, ["Контрагент","contragent","client","Компания"])).trim();
      const year  = String(pick(r, ["Год","year"])).trim();
      const lat   = toNum(pick(r, ["Широта","lat","latitude"]));
      const lon   = toNum(pick(r, ["Долгота","lon","long","lng","longitude"]));
      const yld   = kpiMap.get(`${contr}||${year}`);
      if (Number.isFinite(lat) && Number.isFinite(lon) && Number.isFinite(yld)) {
        pts.push({ lat, lon, yld, contr, year });
      }
    }
    return pts;
  }, [geoRows, kpiRows, hasPoints, hasYield]);

  // bbox
  const bbox = useMemo(() => {
    if (!joined.length) return null;
    let minLat=+90, maxLat=-90, minLon=+180, maxLon=-180;
    for (const p of joined) {
      if (p.lat < minLat) minLat = p.lat;
      if (p.lat > maxLat) maxLat = p.lat;
      if (p.lon < minLon) minLon = p.lon;
      if (p.lon > maxLon) maxLon = p.lon;
    }
    return { minLat, maxLat, minLon, maxLon };
  }, [joined]);

  // агрегирование в сетку
  const rowsN = 10, colsN = 20;
  const gridAgg = useMemo(() => {
    if (!bbox || !joined.length) return { edges: null, grid: null, means: [] };
    const { minLat, maxLat, minLon, maxLon } = bbox;
    const latSpan = Math.max(1e-9, maxLat - minLat);
    const lonSpan = Math.max(1e-9, maxLon - minLon);

    const sum = Array.from({ length: rowsN }, () => Array(colsN).fill(0));
    const cnt = Array.from({ length: rowsN }, () => Array(colsN).fill(0));
    for (const p of joined) {
      const ry = Math.floor((1 - (p.lat - minLat) / latSpan) * rowsN);
      const cx = Math.floor(((p.lon - minLon) / lonSpan) * colsN);
      const r = Math.min(rowsN - 1, Math.max(0, ry));
      const c = Math.min(colsN - 1, Math.max(0, cx));
      sum[r][c] += p.yld;
      cnt[r][c] += 1;
    }
    const mean = sum.map((row, r) => row.map((v, c) => cnt[r][c] ? v / cnt[r][c] : NaN));
    const vals = mean.flat().filter(Number.isFinite);
    const min = vals.length ? Math.min(...vals) : 0;
    const max = vals.length ? Math.max(...vals) : 1;
    const edges = equalBreaks(min, max, 6);
    return { edges, grid: mean, means: vals };
  }, [bbox, joined]);

  // Leaflet точки (один useEffect)
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
      if (group) group.remove();

      if (mapRef.current) {
        group = L.featureGroup();
        for (const p of joined) {
          const m = L.circleMarker([p.lat, p.lon], { radius: 5, weight: 1 });
          m.bindTooltip(`${p.contr} (${p.year}) — ${p.yld.toFixed(1)} ц/га`);
          m.addTo(group);
        }
        if (group.getLayers().length) {
          group.addTo(mapRef.current);
          mapRef.current.fitBounds(group.getBounds().pad(0.25));
        }
      }
    }
    init();
  }, [joined]);

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: 16,
      minHeight: 360,
      padding: 16
    }}>
      {/* ЛЕВО: карта */}
      <section style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, background: "#fff" }}>
        <h3 style={{ margin: 0, marginBottom: 8 }}>Точки (бренд/гибрид)</h3>
        {geoRows === null ? <div style={{ color: "#666" }}>Загрузка…</div> : null}
        {geoRows && !hasPoints ? (
          <div style={{ color: "#666" }}>Нет данных — добавьте <code>public/data/geo.csv</code>.</div>
        ) : null}
        <div
          ref={mapEl}
          style={{ height: 280, border: "1px solid #e5e7eb", borderRadius: 12, overflow: "hidden", marginTop: 8 }}
        />
      </section>

      {/* ПРАВО: тепловая сетка + таблица метрик */}
      <section style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, background: "#fff" }}>
        <h3 style={{ margin: 0, marginBottom: 8 }}>Градиент по урожайности (bbox-сетка)</h3>

        {(!gridAgg.grid || !gridAgg.means.length) ? (
          <div style={{ color: "#666" }}>
            Нет данных для сетки. Нужны <code>public/data/geo.csv</code> и <code>public/data/kpi.csv</code> с совпадающими
            ключами <em>Контрагент+Год</em>.
          </div>
        ) : (
          <>
            <div style={{ fontSize: 13, color: "#666", marginBottom: 8 }}>
              Ячейки с данными: {gridAgg.means.length}; диапазон: {Math.min(...gridAgg.means).toFixed(1)}–{Math.max(...gridAgg.means).toFixed(1)} ц/га
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
              <div style={{ display: "grid", gridTemplateRows: `repeat(${10}, 1fr)`, gap: 2, height: "100%" }}>
                {gridAgg.grid.map((row, ri) => (
                  <div key={ri} style={{ display: "grid", gridTemplateColumns: `repeat(${20}, 1fr)`, gap: 2 }}>
                    {row.map((v, ci) => {
                      if (!Number.isFinite(v)) {
                        return <div key={ci} style={{ height: "100%", background: "#eee", borderRadius: 2 }} title="нет данных" />;
                      }
                      const bi = binIndex(v, gridAgg.edges);
                      const t = (gridAgg.edges.length - 2) === 0 ? 1 : bi / (gridAgg.edges.length - 2);
                      return (
                        <div key={ci} title={`${v.toFixed(1)} ц/га`}
                          style={{ height: "100%", background: redYellowGreen(t), borderRadius: 2 }} />
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
            <Legend edges={gridAgg.edges} />
          </>
        )}

        {/* Таблица метрик ниже — не зависит от наличия сетки */}
        <StatsTable rows={statsRows || []} />
      </section>

      {error && (
        <div style={{ gridColumn: "1 / span 2", color: "#c0392b" }}>
          Ошибка загрузки: {error}
        </div>
      )}
    </div>
  );
}
