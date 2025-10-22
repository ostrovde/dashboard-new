import React, { useEffect, useState } from "react";

/**
 * Каркас карты с graceful fallback:
 * - Левый блок: список "точек" (пока просто счётчики/заглушки)
 * - Правый блок: "тепловая" панель с легендой (красн→зелён)
 * - Никаких падений при отсутствии данных: отображаем понятный текст
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
  // Пока работаем без реальных данных. Делаем вид, что пытаемся их получить.
  const [points, setPoints] = useState(null);    // null = “не загружено”, [] = “пусто”
  const [yieldGrid, setYieldGrid] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    // Заглушка загрузки: пробуем прочитать очищенные CSV, но НЕ падаем, если их нет.
    async function tryLoad() {
      try {
        // Эти fetch будут успешны только если ты положишь файлы в public/data при сборке.
        // Нам сейчас важен устойчивый UI, поэтому просто «мягко» игнорируем 404.
        const p = await fetch("/data/cleaned_sample_geo.csv").then(r => r.ok ? r.text() : "");
        const y = await fetch("/data/cleaned_sample_kpi.csv").then(r => r.ok ? r.text() : "");
        setPoints(p ? [{}] : []);     // если файл есть — считаем, что есть точки
        setYieldGrid(y ? [{}] : []);  // если файл есть — считаем, что есть “ячейки” урожайности
      } catch (e) {
        setError(String(e));
        setPoints([]); setYieldGrid([]);
      }
    }
    tryLoad();
  }, []);

  const hasPoints = Array.isArray(points) && points.length > 0;
  const hasYield  = Array.isArray(yieldGrid) && yieldGrid.length > 0;

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: 16,
      minHeight: 320,
      padding: 16
    }}>
      <section style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, background: "#fff" }}>
        <h3 style={{ margin: 0, marginBottom: 8 }}>Точки (бренд/гибрид)</h3>
        {!points && <div style={{ color: "#666" }}>Загрузка…</div>}
        {points && !hasPoints && <div style={{ color: "#666" }}>Данные отсутствуют — UI работает без падений.</div>}
        {hasPoints && (
          <div>
            <div style={{ fontSize: 13, color: "#666", marginBottom: 8 }}>Количество точек: {points.length}</div>
            <div style={{ height: 220, border: "1px dashed #ddd", borderRadius: 8, display: "grid", placeItems: "center" }}>
              <span style={{ color: "#999" }}>Здесь будет слой точек</span>
            </div>
          </div>
        )}
      </section>

      <section style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, background: "#fff" }}>
        <h3 style={{ margin: 0, marginBottom: 8 }}>Градиент по урожайности</h3>
        {!yieldGrid && <div style={{ color: "#666" }}>Загрузка…</div>}
        {yieldGrid && !hasYield && <div style={{ color: "#666" }}>Данные отсутствуют — UI работает без падений.</div>}
        {hasYield && (
          <div>
            <div style={{ fontSize: 13, color: "#666", marginBottom: 8 }}>Ячеек: {yieldGrid.length}</div>
            <div style={{ height: 220, border: "1px dashed #ddd", borderRadius: 8, display: "grid", placeItems: "center" }}>
              <span style={{ color: "#999" }}>Здесь будет градиент (красн→зелён)</span>
            </div>
            <Legend />
          </div>
        )}
      </section>

      {error && <div style={{ gridColumn: "1 / span 2", color: "#c0392b" }}>Ошибка загрузки: {error}</div>}
    </div>
  );
}
