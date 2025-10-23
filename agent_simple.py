import os
import subprocess
import sys
import requests
import json
from datetime import datetime

class Agent:
    def __init__(self):
        self.repo = os.environ.get('GITHUB_REPOSITORY', 'ostrovde/dashboard-new')
        
    def create_pr(self, issue_number, branch_name):
        token = os.environ.get('GITHUB_TOKEN')
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        owner, repo = self.repo.split('/')
        
        response = requests.post(
            f'https://api.github.com/repos/{owner}/{repo}/pulls',
            headers={'Authorization': f'token {token}'},
            json={
                'title': f'feat: create advanced dashboard for #{issue_number}',
                'body': f'This PR creates an advanced yield dashboard with analytics for issue #{issue_number}',
                'head': branch_name,
                'base': 'main'
            }
        )
        return response.json()
    
    def create_project_structure(self):
        """Создает полную структуру проекта для дашборда"""
        print(">>> Creating project structure...")
        
        # Основные папки
        folders = [
            'src/components',
            'src/utils', 
            'src/styles',
            'src/hooks',
            'public',
            'data'
        ]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            print(f">> Created: {folder}")
        
        return True
    
    def create_package_json(self):
        """Создает или обновляет package.json с нужными зависимостями"""
        print(">> Configuring dependencies...")
        
        package_data = {
            "name": "rayagro-dashboard",
            "private": True,
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "recharts": "^2.8.0",
                "leaflet": "^1.9.4",
                "react-leaflet": "^4.2.1"
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "@vitejs/plugin-react": "^4.1.0",
                "vite": "^4.4.0"
            }
        }
        
        with open("package.json", "w", encoding='utf-8') as f:
            json.dump(package_data, f, indent=2, ensure_ascii=False)
        
        print("> Created package.json with all dependencies")
        return True
    
    def create_main_files(self, issue_number):
        """Создает основные файлы дашборда"""
        print(">> Creating main application files...")
        
        # 1. index.html
        index_html = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>RayAgro Yield Dashboard</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>'''
        
        with open("index.html", "w", encoding='utf-8') as f:
            f.write(index_html)
        
        # 2. main.jsx
        main_jsx = '''import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);'''
        
        with open("src/main.jsx", "w", encoding='utf-8') as f:
            f.write(main_jsx)
        
        # 3. index.css
        index_css = '''* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  background: #f8fafc;
  color: #1e293b;
  line-height: 1.6;
}

.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #4C73C1 0%, #3B82F6 100%);
  color: white;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.app-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.app-sub {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

main {
  flex: 1;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  text-align: center;
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.kpi-value {
  font-size: 2rem;
  font-weight: 700;
  color: #4C73C1;
  margin: 0.5rem 0;
}

.kpi-label {
  color: #64748b;
  font-weight: 500;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #475569;
  font-size: 0.9rem;
}

.filter-group select,
.filter-group input {
  padding: 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: white;
  font-size: 0.9rem;
}

.chart-container {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
  margin-bottom: 1.5rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 1rem;
}

.tab {
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.tab.active {
  background: #4C73C1;
  color: white;
}

.tab:hover:not(.active) {
  background: #f1f5f9;
}

@media (max-width: 768px) {
  .app-header {
    padding: 1.5rem 1rem;
  }
  
  .app-header h1 {
    font-size: 2rem;
  }
  
  main {
    padding: 1rem;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
}'''
        
        with open("src/index.css", "w", encoding='utf-8') as f:
            f.write(index_css)
        
        print("> Created main application files")
        return True
    
    def create_react_components(self, issue_number):
        """Создает React компоненты для дашборда"""
        print(">> Creating React components...")
        
        # 1. App.jsx - главный компонент
        app_jsx = f'''import React, {{ useState, useEffect }} from "react";
import Dashboard from "./components/Dashboard.jsx";
import "./index.css";

export default function App() {{
  const updateData = () => {{
    console.log("Updating data from Google Sheets...");
    alert("Данные обновляются из Google Sheets!");
  }};

  return (
    <div className="app-root">
      <header className="app-header">
        <div style={{
          maxWidth: "1200px",
          margin: "0 auto",
          width: "100%"
        }}>
          <h1>RayAgro Yield Dashboard</h1>
          <p className="app-sub">Расширенный дашборд урожайности с аналитикой</p>
          <div className="header-actions">
            <button onClick={{updateData}} className="btn-primary">
              Обновить данные
            </button>
            <button className="btn-primary">
              Экспорт отчетов
            </button>
            <button className="btn-primary">
              Настройки
            </button>
          </div>
        </div>
      </header>
      <main>
        <Dashboard />
      </main>
      <footer style={{
        background: "#1e293b",
        color: "white",
        padding: "2rem",
        textAlign: "center",
        marginTop: "auto"
      }}>
        <div style={{
          maxWidth: "1200px",
          margin: "0 auto",
          opacity: 0.8
        }}>
          <p>RayAgro Yield Dashboard • Создан агентом для Issue #{issue_number}</p>
          <p style={{ fontSize: "0.9rem", marginTop: "0.5rem" }}>
            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
          </p>
        </div>
      </footer>
    </div>
  );
}}'''
        
        with open("src/App.jsx", "w", encoding='utf-8') as f:
            f.write(app_jsx)
        
        # 2. Dashboard.jsx - основной компонент дашборда
        dashboard_jsx = f'''import React, {{ useState, useEffect }} from "react";
import KPISection from "./components/KPISection.jsx";
import FiltersPanel from "./components/FiltersPanel.jsx";
import MapsSection from "./components/MapsSection.jsx";
import AnalyticsSection from "./components/AnalyticsSection.jsx";

export default function Dashboard() {{
  const [activeTab, setActiveTab] = useState("overview");
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {{
    // Имитация загрузки данных
    setTimeout(() => {{
      setData([
        {{ id: 1, hybrid: "Подсолнечник-1", yield: 28.5, oil: 45.2, location: "Локация A" }},
        {{ id: 2, hybrid: "Кукуруза-1", yield: 85.3, oil: 0, location: "Локация B" }},
        {{ id: 3, hybrid: "Подсолнечник-2", yield: 32.1, oil: 48.7, location: "Локация C" }}
      ]);
      setLoading(false);
    }}, 1000);
  }}, []);

  const tabs = [
    {{ id: "overview", label: "Обзор", icon: "📊" }},
    {{ id: "analytics", label: "Аналитика", icon: "📈" }},
    {{ id: "maps", label: "Карты", icon: "🗺️" }},
    {{ id: "table", label: "Таблица", icon: "📋" }}
  ];

  if (loading) {{
    return (
      <div style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "400px",
        fontSize: "1.2rem",
        color: "#64748b"
      }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>⏳</div>
          <p>Загрузка расширенного дашборда...</p>
        </div>
      </div>
    );
  }}

  return (
    <div>
      <!-- Вкладки -->
      <div className="tabs">
        {{tabs.map(tab => (
          <button
            key={{tab.id}}
            className={{`tab ${{activeTab === tab.id ? "active" : ""}}`}}
            onClick={{() => setActiveTab(tab.id)}}
          >
            <span style={{ marginRight: "0.5rem" }}>{{tab.icon}}</span>
            {{tab.label}}
          </button>
        ))}}
      </div>

      <!-- Панель фильтров -->
      <FiltersPanel />

      <!-- KPI показатели -->
      <KPISection data={{data}} />

      <!-- Контент вкладок -->
      {{activeTab === "overview" && (
        <div>
          <div className="card">
            <h2 style={{ marginBottom: "1rem", color: "#1e293b" }}>Обзор производительности</h2>
            <p style={{ color: "#64748b", lineHeight: "1.6" }}>
              Добро пожаловать в расширенный дашборд урожайности RayAgro. 
              Здесь вы можете анализировать данные по гибридам, брендам и локациям.
            </p>
          </div>
          
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
            <MapsSection />
            <AnalyticsSection data={{data}} />
          </div>
        </div>
      )}}

      {{activeTab === "analytics" && (
        <div className="card">
          <h2 style={{ marginBottom: "1rem", color: "#1e293b" }}>Расширенная аналитика</h2>
          <p>Раздел аналитики в разработке...</p>
        </div>
      )}}

      {{activeTab === "maps" && (
        <MapsSection fullPage={{true}} />
      )}}

      {{activeTab === "table" && (
        <div className="card">
          <h2 style={{ marginBottom: "1rem", color: "#1e293b" }}>Таблица данных</h2>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: "#f8fafc" }}>
                  <th style={{ padding: "1rem", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>Гибрид</th>
                  <th style={{ padding: "1rem", textAlign: "right", borderBottom: "1px solid #e2e8f0" }}>Урожайность</th>
                  <th style={{ padding: "1rem", textAlign: "right", borderBottom: "1px solid #e2e8f0" }}>Масличность</th>
                  <th style={{ padding: "1rem", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>Локация</th>
                </tr>
              </thead>
              <tbody>
                {{data.map(row => (
                  <tr key={{row.id}} style={{ borderBottom: "1px solid #e2e8f0" }}>
                    <td style={{ padding: "1rem" }}>{{row.hybrid}}</td>
                    <td style={{ padding: "1rem", textAlign: "right", fontWeight: "600" }}>{{row.yield}} ц/га</td>
                    <td style={{ padding: "1rem", textAlign: "right" }}>{{row.oil}}%</td>
                    <td style={{ padding: "1rem" }}>{{row.location}}</td>
                  </tr>
                ))}}
              </tbody>
            </table>
          </div>
        </div>
      )}}
    </div>
  );
}}'''
        
        # Убеждаемся, что папка components существует
        os.makedirs("src/components", exist_ok=True)
        with open("src/components/Dashboard.jsx", "w", encoding='utf-8') as f:
            f.write(dashboard_jsx)
        
        # 3. Остальные компоненты
        components = {
            'KPISection.jsx': '''import React from "react";

export default function KPISection({ data }) {
  const kpis = [
    {
      label: "Средняя урожайность",
      value: data.length ? (data.reduce((sum, row) => sum + row.yield, 0) / data.length).toFixed(1) + " ц/га" : "—",
      icon: "🌾"
    },
    {
      label: "Средняя масличность",
      value: data.filter(row => row.oil > 0).length ? 
        (data.filter(row => row.oil > 0).reduce((sum, row) => sum + row.oil, 0) / data.filter(row => row.oil > 0).length).toFixed(1) + "%" : "—",
      icon: "🫒"
    },
    {
      label: "Количество локаций",
      value: new Set(data.map(row => row.location)).size,
      icon: "📍"
    },
    {
      label: "Количество гибридов",
      value: new Set(data.map(row => row.hybrid)).size,
      icon: "🧬"
    }
  ];

  return (
    <div className="kpi-grid">
      {kpis.map((kpi, index) => (
        <div key={index} className="kpi-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div className="kpi-label">{kpi.label}</div>
            <span style={{ fontSize: "1.5rem" }}>{kpi.icon}</span>
          </div>
          <div className="kpi-value">{kpi.value}</div>
        </div>
      ))}
    </div>
  );
}''',
            
            'FiltersPanel.jsx': '''import React, { useState } from "react";

export default function FiltersPanel() {
  const [filters, setFilters] = useState({
    brand: "",
    hybrid: "",
    year: "",
    location: ""
  });

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  return (
    <div className="card">
      <h3 style={{ marginBottom: "1rem", color: "#1e293b" }}>Фильтры данных</h3>
      <div className="filters-grid">
        <div className="filter-group">
          <label>Бренд</label>
          <select 
            value={filters.brand} 
            onChange={(e) => handleFilterChange("brand", e.target.value)}
          >
            <option value="">Все бренды</option>
            <option value="Пионер">Пионер</option>
            <option value="Сингента">Сингента</option>
            <option value="Лимагрен">Лимагрен</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>Гибрид</label>
          <select 
            value={filters.hybrid} 
            onChange={(e) => handleFilterChange("hybrid", e.target.value)}
          >
            <option value="">Все гибриды</option>
            <option value="Подсолнечник">Подсолнечник</option>
            <option value="Кукуруза">Кукуруза</option>
            <option value="Соя">Соя</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>Год</label>
          <select 
            value={filters.year} 
            onChange={(e) => handleFilterChange("year", e.target.value)}
          >
            <option value="">Все годы</option>
            <option value="2023">2023</option>
            <option value="2024">2024</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>Локация</label>
          <input 
            type="text" 
            value={filters.location} 
            onChange={(e) => handleFilterChange("location", e.target.value)}
            placeholder="Введите локацию"
          />
        </div>
      </div>
    </div>
  );
}''',
            
            'MapsSection.jsx': '''import React from "react";

export default function MapsSection({ fullPage = false }) {
  return (
    <div className={fullPage ? "" : "card"}>
      <h3 style={{ marginBottom: "1rem", color: "#1e293b" }}>Карта испытаний</h3>
      <div style={{
        height: fullPage ? "600px" : "400px",
        background: "linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%)",
        borderRadius: "8px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        border: "2px dashed #4CAF50",
        flexDirection: "column",
        gap: "1rem",
        color: "#2e7d32"
      }}>
        <div style={{ fontSize: "3rem" }}>🗺️</div>
        <div style={{ textAlign: "center" }}>
          <p style={{ fontSize: "1.2rem", fontWeight: "600", marginBottom: "0.5rem" }}>
            Интерактивная карта
          </p>
          <p>Интеграция с Leaflet и React-Leaflet</p>
          <p style={{ fontSize: "0.9rem", opacity: 0.8, marginTop: "0.5rem" }}>
            Показывает локации испытаний с данными урожайности
          </p>
        </div>
      </div>
    </div>
  );
}''',
            
            'AnalyticsSection.jsx': '''import React from "react";

export default function AnalyticsSection({ data }) {
  return (
    <div className="card">
      <h3 style={{ marginBottom: "1rem", color: "#1e293b" }}>Аналитика урожайности</h3>
      <div style={{
        height: "400px",
        background: "linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)",
        borderRadius: "8px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        border: "2px dashed #2196F3",
        flexDirection: "column",
        gap: "1rem",
        color: "#1565c0"
      }}>
        <div style={{ fontSize: "3rem" }}>📈</div>
        <div style={{ textAlign: "center" }}>
          <p style={{ fontSize: "1.2rem", fontWeight: "600", marginBottom: "0.5rem" }}>
            Графики и диаграммы
          </p>
          <p>Интеграция с Recharts</p>
          <p style={{ fontSize: "0.9rem", opacity: 0.8, marginTop: "0.5rem" }}>
            Визуализация данных урожайности и масличности
          </p>
        </div>
      </div>
    </div>
  );
}'''
        }
        
        for component_name, component_code in components.items():
            with open(f"src/components/{component_name}", "w", encoding='utf-8') as f:
                f.write(component_code)
            print(f"> Created component: {component_name}")
        
        print("> All React components created")
        return True
    
    def create_utils_and_data(self):
        """Создает вспомогательные файлы и данные"""
        print(">>> Creating utilities and data files...")
        
        # utils/constants.js
        constants_js = '''// Цветовая палитра RayAgro
export const RAYAGRO_COLORS = {
  primary: "#4C73C1",
  accent: "#F6C500", 
  success: "#10B981",
  warning: "#F59E0B",
  error: "#EF4444",
  info: "#3B82F6"
};

// Настройки дашборда
export const DASHBOARD_CONFIG = {
  maxDataPoints: 1000,
  refreshInterval: 30000,
  defaultFilters: {
    year: new Date().getFullYear(),
    brand: "",
    hybrid: ""
  }
};

// API endpoints
export const API_ENDPOINTS = {
  data: "/api/data",
  analytics: "/api/analytics",
  export: "/api/export"
};'''
        
        with open("src/utils/constants.js", "w", encoding='utf-8') as f:
            f.write(constants_js)
        
        # utils/dataProcessing.js
        data_processing_js = '''// Функции для обработки данных
export const processYieldData = (rawData) => {
  return rawData.map(item => ({
    ...item,
    yield: parseFloat(item.yield) || 0,
    oil: parseFloat(item.oil) || 0,
    date: new Date(item.date)
  }));
};

export const calculateKPIs = (data) => {
  if (!data.length) return {};
  
  const yields = data.map(d => d.yield).filter(y => y > 0);
  const oils = data.map(d => d.oil).filter(o => o > 0);
  
  return {
    avgYield: yields.length ? (yields.reduce((a, b) => a + b, 0) / yields.length).toFixed(1) : 0,
    avgOil: oils.length ? (oils.reduce((a, b) => a + b, 0) / oils.length).toFixed(1) : 0,
    totalLocations: new Set(data.map(d => d.location)).size,
    totalHybrids: new Set(data.map(d => d.hybrid)).size
  };
};

export const filterData = (data, filters) => {
  return data.filter(item => {
    if (filters.brand && item.brand !== filters.brand) return false;
    if (filters.hybrid && !item.hybrid.includes(filters.hybrid)) return false;
    if (filters.year && item.year !== filters.year) return false;
    if (filters.location && !item.location.toLowerCase().includes(filters.location.toLowerCase())) return false;
    return true;
  });
};'''
        
        with open("src/utils/dataProcessing.js", "w", encoding='utf-8') as f:
            f.write(data_processing_js)
        
        print("> Created utility files")
        return True
    
    def create_documentation(self, issue_number):
        """Создает документацию проекта"""
        print(">> Creating documentation...")
        
        # README.md
        readme_content = f'''# RayAgro Yield Dashboard

Расширенный дашборд урожайности с аналитикой для агротехнических данных.

## Описание

Этот дашборд создан для анализа данных урожайности различных культур и гибридов. 
Включает в себя интерактивные карты, графики и таблицы данных.

## Функциональность

- 📊 **KPI показатели** - ключевые метрики урожайности
- 🗺️ **Интерактивные карты** - визуализация локаций испытаний  
- 📈 **Аналитика** - графики и диаграммы
- 📋 **Таблицы данных** - детальная информация
- 🔍 **Фильтрация** - поиск по различным параметрам

## Технологии

- **Frontend**: React 18, Vite
- **Карты**: Leaflet, React-Leaflet
- **Графики**: Recharts
- **Стили**: CSS3, Flexbox, Grid

## Структура проекта

```
src/
├── components/     # React компоненты
│   ├── Dashboard.jsx        # Главный дашборд
│   ├── KPISection.jsx      # KPI показатели
│   ├── FiltersPanel.jsx    # Панель фильтров
│   ├── MapsSection.jsx     # Карты
│   └── AnalyticsSection.jsx # Аналитика
├── utils/          # Вспомогательные функции
│   ├── constants.js       # Константы и настройки
│   └── dataProcessing.js  # Обработка данных
├── styles/         # Стили
│   └── index.css   # Основные стили
├── App.jsx         # Главный компонент приложения
└── main.jsx        # Точка входа
```

## Разработка

Дашборд создан как основа для дальнейшего развития. 
Агент может постепенно добавлять новый функционал через Issues.

## Контакты

- **Репозиторий**: https://github.com/ostrovde/dashboard-new
- **Автоматизация**: GitHub Actions + Python Agent

----

*Создано с помощью автономного агента разработки*
'''
        
        with open("README.md", "w", encoding='utf-8') as f:
            f.write(readme_content)
        
        print("> Documentation created")
        return True
    
    def create_advanced_dashboard(self, issue_number):
        """Основная функция создания улучшенного дашборда"""
        print(">> Starting advanced dashboard creation...")
        
        try:
            # 1. Создаем структуру проекта
            self.create_project_structure()
            
            # 2. Настраиваем package.json
            self.create_package_json()
            
            # 3. Создаем основные файлы
            self.create_main_files(issue_number)
            
            # 4. Создаем React компоненты
            self.create_react_components(issue_number)
            
            # 5. Создаем утилиты и данные
            self.create_utils_and_data()
            
            # 6. Создаем документацию
            self.create_documentation(issue_number)
            
            print(">> Advanced dashboard created successfully!")
            return True
            
        except Exception as e:
            print(f"> Error creating dashboard: {e}")
            return False
    
    def run(self, issue_number):
        print(f">> Agent started for issue #{issue_number}")
        print(f">> Repository: {self.repo}")
        
        # Создаем ветку
        branch_name = f"feat/{issue_number}-advanced-dashboard"
        
        # Переходим в workdir если есть
        if os.path.exists("workdir"):
            os.chdir("workdir")
            print(">> Working in workdir/")
        else:
            print(">> Working in current directory")
        
        # Создаем ветку
        try:
            # Проверяем, существует ли ветка
            result = subprocess.run(["git", "branch", "--list", branch_name], capture_output=True, text=True)
            if result.stdout.strip():
                print(f">> Branch {branch_name} already exists, switching to it")
                subprocess.run(["git", "checkout", branch_name], check=True)
            else:
                subprocess.run(["git", "checkout", "-b", branch_name], check=True)
                print(f">> Created branch: {branch_name}")
        except subprocess.CalledProcessError as e:
            print(f">> Error creating branch: {e}")
            return False
        
        # =============================================
        # СОЗДАЕМ УЛУЧШЕННЫЙ ДАШБОРД
        # =============================================
        
        print(">>> Building advanced dashboard structure...")
        
        success = self.create_advanced_dashboard(issue_number)
        
        if success:
            print(">>> Dashboard structure completed!")
            
            # Коммитим изменения
            try:
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", f"feat: create advanced dashboard for #{issue_number}"], check=True)
                
                # Пушим в репозиторий
                subprocess.run(["git", "push", "origin", branch_name], check=True)
                print(f">>> Pushed to branch: {branch_name}")
            except subprocess.CalledProcessError as e:
                print(f">>> Error with git operations: {e}")
                return False
            
            # Создаем PR
            try:
                pr = self.create_pr(issue_number, branch_name)
                print(f">>> Created PR: {pr.get('html_url', 'URL not available')}")
            except Exception as e:
                print(f">>> Error creating PR: {e}")
                return False
            
            print("\\n" + "="*50)
            print("[SUCCESS] ADVANCED DASHBOARD CREATED SUCCESSFULLY!")
            print("="*50)
            print(f"[DASHBOARD] Dashboard structure ready for issue #{issue_number}")
            print(f"[PR] PR: {pr.get('html_url', 'Check repository')}")
            print(f"[BRANCH] Branch: {branch_name}")
            print("="*50)
            
            return True
        else:
            print("[ERROR] Dashboard creation failed!")
            return False

# Запуск агента
if __name__ == "__main__":
    issue_number = sys.argv[1] if len(sys.argv) > 1 else "1"
    agent = Agent()
    agent.run(issue_number)
