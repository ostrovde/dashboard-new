import React, { useState, useEffect } from "react";
import KPISection from "./components/KPISection.jsx";
import FiltersPanel from "./components/FiltersPanel.jsx";
import MapsSection from "./components/MapsSection.jsx";
import AnalyticsSection from "./components/AnalyticsSection.jsx";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Имитация загрузки данных
    setTimeout(() => {
      setData([
        { id: 1, hybrid: "Подсолнечник-1", yield: 28.5, oil: 45.2, location: "Локация A" },
        { id: 2, hybrid: "Кукуруза-1", yield: 85.3, oil: 0, location: "Локация B" },
        { id: 3, hybrid: "Подсолнечник-2", yield: 32.1, oil: 48.7, location: "Локация C" }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const tabs = [
    { id: "overview", label: "Обзор", icon: "📊" },
    { id: "analytics", label: "Аналитика", icon: "📈" },
    { id: "maps", label: "Карты", icon: "🗺️" },
    { id: "table", label: "Таблица", icon: "📋" }
  ];

  if (loading) {
    return (
      <div style={
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "400px",
        fontSize: "1.2rem",
        color: "#64748b"
      }>
        <div style={ textAlign: "center" }>
          <div style={ fontSize: "3rem", marginBottom: "1rem" }>⏳</div>
          <p>Загрузка расширенного дашборда...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <!-- Вкладки -->
      <div className="tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span style={ marginRight: "0.5rem" }>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      <!-- Панель фильтров -->
      <FiltersPanel />

      <!-- KPI показатели -->
      <KPISection data={data} />

      <!-- Контент вкладок -->
      {activeTab === "overview" && (
        <div>
          <div className="card">
            <h2 style={ marginBottom: "1rem", color: "#1e293b" }>Обзор производительности</h2>
            <p style={ color: "#64748b", lineHeight: "1.6" }>
              Добро пожаловать в расширенный дашборд урожайности RayAgro. 
              Здесь вы можете анализировать данные по гибридам, брендам и локациям.
            </p>
          </div>
          
          <div style={ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }>
            <MapsSection />
            <AnalyticsSection data={data} />
          </div>
        </div>
      )}

      {activeTab === "analytics" && (
        <div className="card">
          <h2 style={ marginBottom: "1rem", color: "#1e293b" }>Расширенная аналитика</h2>
          <p>Раздел аналитики в разработке...</p>
        </div>
      )}

      {activeTab === "maps" && (
        <MapsSection fullPage={true} />
      )}

      {activeTab === "table" && (
        <div className="card">
          <h2 style={ marginBottom: "1rem", color: "#1e293b" }>Таблица данных</h2>
          <div style={ overflowX: "auto" }>
            <table style={ width: "100%", borderCollapse: "collapse" }>
              <thead>
                <tr style={ background: "#f8fafc" }>
                  <th style={ padding: "1rem", textAlign: "left", borderBottom: "1px solid #e2e8f0" }>Гибрид</th>
                  <th style={ padding: "1rem", textAlign: "right", borderBottom: "1px solid #e2e8f0" }>Урожайность</th>
                  <th style={ padding: "1rem", textAlign: "right", borderBottom: "1px solid #e2e8f0" }>Масличность</th>
                  <th style={ padding: "1rem", textAlign: "left", borderBottom: "1px solid #e2e8f0" }>Локация</th>
                </tr>
              </thead>
              <tbody>
                {data.map(row => (
                  <tr key={row.id} style={ borderBottom: "1px solid #e2e8f0" }>
                    <td style={ padding: "1rem" }>{row.hybrid}</td>
                    <td style={ padding: "1rem", textAlign: "right", fontWeight: "600" }>{row.yield} ц/га</td>
                    <td style={ padding: "1rem", textAlign: "right" }>{row.oil}%</td>
                    <td style={ padding: "1rem" }>{row.location}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}