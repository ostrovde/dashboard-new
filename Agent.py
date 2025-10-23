import os
import subprocess
import sys
import requests
import time
import re
import json

class Agent:
    def __init__(self):
        self.repo = os.environ.get('GITHUB_REPOSITORY', 'ostrovde/dashboard-new')
        
    def create_pr(self, issue_number, branch_name):
        token = os.environ['GITHUB_TOKEN']
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
        """������� ������ ��������� ������� ��� ��������"""
        print("??? Creating project structure...")
        
        # �������� �����
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
            print(f"?? Created: {folder}")
        
        return True
    
    def create_package_json(self):
        """������� ��� ��������� package.json � ������� �������������"""
        print("?? Configuring dependencies...")
        
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
        
        with open("package.json", "w") as f:
            json.dump(package_data, f, indent=2)
        
        print("? Created package.json with all dependencies")
        return True
    
    def create_main_files(self, issue_number):
        """������� �������� ����� ��������"""
        print("?? Creating main application files...")
        
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
        
        with open("index.html", "w") as f:
            f.write(index_html)
        
        # 2. main.jsx
        main_jsx = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)'''
        
        with open("src/main.jsx", "w") as f:
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
        
        with open("src/index.css", "w") as f:
            f.write(index_css)
        
        print("? Created main application files")
        return True
    
    def create_react_components(self, issue_number):
        """������� React ���������� ��� ��������"""
        print("?? Creating React components...")
        
        # 1. App.jsx - ������� ���������
        app_jsx = f'''import React, {{ useState, useEffect }} from "react";
import Dashboard from "./components/Dashboard.jsx";
import "./index.css";

function updateData() {{
  console.log("Updating data from Google Sheets...");
  alert("������ ����������� �� Google Sheets!");
}}

export default function App() {{
  return (
    <div className="app-root">
      <header className="app-header">
        <div style={{{
          maxWidth: "1200px",
          margin: "0 auto",
          width: "100%"
        }}>
          <h1>RayAgro Yield Dashboard</h1>
          <p className="app-sub">����������� ������� ����������� � ����������</p>
          <div className="header-actions">
            <button onClick={{updateData}} className="btn-primary">
              ?? �������� ������
            </button>
            <button className="btn-primary">
              ?? ������� �������
            </button>
            <button className="btn-primary">
              ?? ���������
            </button>
          </div>
        </div>
      </header>
      <main>
        <Dashboard />
      </main>
      <footer style={{{
        background: "#1e293b",
        color: "white",
        padding: "2rem",
        textAlign: "center",
        marginTop: "auto"
      }}>
        <div style={{{
          maxWidth: "1200px",
          margin: "0 auto",
          opacity: 0.8
        }}>
          <p>?? RayAgro Yield Dashboard � ������ ������� ��� Issue #{issue_number}</p>
          <p style={{ fontSize: "0.9rem", marginTop: "0.5rem" }}>
            {time.strftime('%Y-%m-%d %H:%M:%S')}
          </p>
        </div>
      </footer>
    </div>
  );
}}'''
        
        with open("src/App.jsx", "w") as f:
            f.write(app_jsx)
        
        # 2. Dashboard.jsx - �������� ��������� ��������
        dashboard_jsx = '''import React, { useState, useEffect } from "react";
import KPISection from "./components/KPISection.jsx";
import FiltersPanel from "./components/FiltersPanel.jsx";
import MapsSection from "./components/MapsSection.jsx";
import AnalyticsSection from "./components/AnalyticsSection.jsx";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // �������� �������� ������
    setTimeout(() => {
      setData([
        { id: 1, hybrid: "������������-1", yield: 28.5, oil: 45.2, location: "������� A" },
        { id: 2, hybrid: "��������-1", yield: 85.3, oil: 0, location: "������� B" },
        { id: 3, hybrid: "������������-2", yield: 32.1, oil: 48.7, location: "������� C" }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const tabs = [
    { id: "overview", label: "?? �����", icon: "??" },
    { id: "analytics", label: "?? ���������", icon: "??" },
    { id: "maps", label: "??? �����", icon: "???" },
    { id: "table", label: "?? �������", icon: "??" }
  ];

  if (loading) {
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
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>??</div>
          <p>�������� ������������ ��������...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* ������� */}
      <div className="tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span style={{ marginRight: "0.5rem" }}>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* ������ �������� */}
      <FiltersPanel />

      {/* KPI ���������� */}
      <KPISection data={data} />

      {/* ������� ������� */}
      {activeTab === "overview" && (
        <div>
          <div className="card">
            <h2 style={{ marginBottom: "1rem", color: "#1e293b" }}>?? ����� ������������������</h2>
            <p style={{ color: "#64748b", lineHeight: "1.6" }}>
              ����� ���������� � ����������� ������� ����������� RayAgro. 
              ����� �� ������ ������������� ������ �� ��������, ������� � ��������.
            </p>
          </div>
          
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
            <MapsSection />
            <AnalyticsSection data={data} />
          </div>
        </div>
      )}

      {activeTab === "analytics" && (
        <div className="card">
          <h2 style={{ marginBottom: "1rem", color: "#1e293b" }}>?? ����������� ���������</h2>
          <p>������ ��������� � ����������...</p>
        </div>
      )}

      {activeTab === "maps" && (
        <MapsSection fullPage={true} />
      )}

      {activeTab === "table" && (
        <div className="card">
          <h2 style={{ marginBottom: "1rem", color: "#1e293b" }}>?? ������� ������</h2>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: "#f8fafc" }}>
                  <th style={{ padding: "1rem", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>������</th>
                  <th style={{ padding: "1rem", textAlign: "right", borderBottom: "1px solid #e2e8f0" }}>�����������</th>
                  <th style={{ padding: "1rem", textAlign: "right", borderBottom: "1px solid #e2e8f0" }}>�����������</th>
                  <th style={{ padding: "1rem", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>�������</th>
                </tr>
              </thead>
              <tbody>
                {data.map(row => (
                  <tr key={row.id} style={{ borderBottom: "1px solid #e2e8f0" }}>
                    <td style={{ padding: "1rem" }}>{row.hybrid}</td>
                    <td style={{ padding: "1rem", textAlign: "right", fontWeight: "600" }}>{row.yield} �/��</td>
                    <td style={{ padding: "1rem", textAlign: "right" }}>{row.oil}%</td>
                    <td style={{ padding: "1rem" }}>{row.location}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}'''
        
        with open("src/components/Dashboard.jsx", "w") as f:
            f.write(dashboard_jsx)
        
        # 3. ��������� ����������
        components = {
            'KPISection.jsx': '''import React from "react";

export default function KPISection({ data }) {
  const kpis = [
    {
      label: "?? ������� �����������",
      value: data.length ? (data.reduce((sum, row) => sum + row.yield, 0) / data.length).toFixed(1) + " �/��" : "�",
      icon: "??"
    },
    {
      label: "??? ������� �����������",
      value: data.filter(row => row.oil > 0).length ? 
        (data.filter(row => row.oil > 0).reduce((sum, row) => sum + row.oil, 0) / data.filter(row => row.oil > 0).length).toFixed(1) + "%" : "�",
      icon: "??"
    },
    {
      label: "?? ���������� �������",
      value: new Set(data.map(row => row.location)).size,
      icon: "??"
    },
    {
      label: "?? ���������� ��������",
      value: new Set(data.map(row => row.hybrid)).size,
      icon: "??"
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
      <h3 style={{ marginBottom: "1rem", color: "#1e293b" }}>?? ������� ������</h3>
      <div className="filters-grid">
        <div className="filter-group">
          <label>�����</label>
          <select 
            value={filters.brand} 
            onChange={(e) => handleFilterChange("brand", e.target.value)}
          >
            <option value="">��� ������</option>
            <option value="������">������</option>
            <option value="��������">��������</option>
            <option value="��������">��������</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>������</label>
          <select 
            value={filters.hybrid} 
            onChange={(e) => handleFilterChange("hybrid", e.target.value)}
          >
            <option value="">��� �������</option>
            <option value="������������-1">������������-1</option>
            <option value="��������-1">��������-1</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>���</label>
          <select 
            value={filters.year} 
            onChange={(e) => handleFilterChange("year", e.target.value)}
          >
            <option value="">��� ����</option>
            <option value="2023">2023</option>
            <option value="2022">2022</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>�������</label>
          <select 
            value={filters.location} 
            onChange={(e) => handleFilterChange("location", e.target.value)}
          >
            <option value="">��� �������</option>
            <option value="������� A">������� A</option>
            <option value="������� B">������� B</option>
          </select>
        </div>
      </div>
      
      <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
        <button className="btn-primary" style={{ background: "#4C73C1" }}>
          ��������� �������
        </button>
        <button 
          className="btn-primary" 
          style={{ background: "#64748b" }}
          onClick={() => setFilters({ brand: "", hybrid: "", year: "", location: "" })}
        >
          ��������
        </button>
      </div>
    </div>
  );
}''',
            
            'MapsSection.jsx': '''import React from "react";

export default function MapsSection({ fullPage = false }) {
  return (
    <div className={fullPage ? "" : "card"}>
      <h3 style={{ marginBottom: "1rem", color: "#1e293b" }}>??? ����� ���������</h3>
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
        <div style={{ fontSize: "3rem" }}>??</div>
        <div style={{ textAlign: "center" }}>
          <p style={{ fontSize: "1.2rem", fontWeight: "600", marginBottom: "0.5rem" }}>
            ������������� �����
          </p>
          <p>���������� � Leaflet � React-Leaflet</p>
          <p style={{ fontSize: "0.9rem", opacity: 0.8, marginTop: "0.5rem" }}>
            ���������� ������� ��������� � ������� �����������
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
      <h3 style={{ marginBottom: "1rem", color: "#1e293b" }}>?? ��������� �����������</h3>
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
        <div style={{ fontSize: "3rem" }}>??</div>
        <div style={{ textAlign: "center" }}>
          <p style={{ fontSize: "1.2rem", fontWeight: "600", marginBottom: "0.5rem" }}>
            ������� � ���������
          </p>
          <p>���������� � Recharts</p>
          <p style={{ fontSize: "0.9rem", opacity: 0.8, marginTop: "0.5rem" }}>
            ������������ ������ ����������� � �����������
          </p>
        </div>
      </div>
    </div>
  );
}'''
        }
        
        for component_name, component_code in components.items():
            with open(f"src/components/{component_name}", "w") as f:
                f.write(component_code)
            print(f"? Created component: {component_name}")
        
        print("? All React components created")
        return True
    
    def create_utils_and_data(self):
        """������� ��������������� ����� � ������"""
        print("??? Creating utilities and data files...")
        
        # utils/constants.js
        constants_js = '''// �������� ������� RayAgro
export const RAYAGRO_COLORS = {
  primary: "#4C73C1",
  accent: "#F6C500", 
  success: "#10B981",
  warning: "#F59E0B",
  error: "#EF4444",
  info: "#3B82F6"
};

// ��������� ��������
export const DASHBOARD_CONFIG = {
  maxPointsOnMap: 1000,
  defaultYearRange: [2015, 2025],
  yieldThreshold: 30,
  refreshInterval: 300000 // 5 �����
};

// ������ � �� �����
export const BRAND_COLORS = {
  "������": "#2563eb",
  "��������": "#f59e0b",
  "��������": "#10b981",
  "���": "#ef4444",
  "LG": "#8b5cf6"
};'''
        
        with open("src/utils/constants.js", "w") as f:
            f.write(constants_js)
        
        # utils/dataProcessing.js
        data_processing_js = '''// ������� ��� ��������� ������
export const processYieldData = (data) => {
  return data.filter(item => item.yield > 0)
    .sort((a, b) => b.yield - a.yield);
};

export const calculateStats = (data) => {
  const yields = data.map(item => item.yield).filter(y => y > 0);
  if (yields.length === 0) return { mean: 0, max: 0, min: 0 };
  
  return {
    mean: yields.reduce((a, b) => a + b, 0) / yields.length,
    max: Math.max(...yields),
    min: Math.min(...yields),
    count: yields.length
  };
};

export const groupByBrand = (data) => {
  const groups = {};
  data.forEach(item => {
    if (!groups[item.brand]) groups[item.brand] = [];
    groups[item.brand].push(item);
  });
  return groups;
};'''
        
        with open("src/utils/dataProcessing.js", "w") as f:
            f.write(data_processing_js)
        
        # ������ ������
        sample_data = '''ID,Hybrid,Brand,Year,Yield,Oil,Location,Lat,Lon
1,������������-1,��������,2023,28.5,45.2,������� A,52.5,31.5
2,��������-1,������,2023,85.3,,������� B,53.0,32.0
3,������������-2,��������,2023,32.1,48.7,������� C,52.7,31.7'''
        
        with open("data/sample-data.csv", "w") as f:
            f.write(sample_data)
        
        print("? Utilities and data files created")
        return True
    
    def create_documentation(self, issue_number):
        """������� ������������ �������"""
        print("?? Creating documentation...")
        
        readme_content = f'''# ?? RayAgro Yield Dashboard

## ����������� ������� ����������� � ����������

### ������ ������������� �������
- **Issue**: #{issue_number}
- **���� ��������**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **������**: ?? �������� ����������

## ?? �����������

### ?? ������������ ������
- ������������� ������� �����������
- �������� ����� ������� ���������
- KPI ���������� � �������� �������

### ??? ������������  
- ����� ��������� � ����������
- �������� ����� �����������
- ���������� �� ��������

### ?? ���������
- ��������� �������� � �������
- �������������� ������
- ������ � ��������

### ?? ���������
- ���������� ������
- ������� ��� ������ ��������
- ������� � ���������

## ??? ����������

- **Frontend**: React 18, Vite
- **�������**: Recharts
- **�����**: Leaflet, React-Leaflet
- **�����**: CSS3, Flexbox/Grid

## ?? ��������� � ������

\\`\\`\\`bash
# ��������� ������������
npm install

# ������ � ������ ����������
npm run dev

# ������ ��� production
npm run build
\\`\\`\\`

## ??? ��������� �������

\\`\\`\\`
src/
+-- components/     # React ����������
�   +-- Dashboard.jsx      # ������� ���������
�   +-- KPISection.jsx     # KPI ����������
�   +-- FiltersPanel.jsx   # ������ ��������
�   +-- MapsSection.jsx    # ������ ����
�   L-- AnalyticsSection.jsx # ���������
+-- utils/          # ��������������� �������
�   +-- constants.js       # ��������� � ���������
�   L-- dataProcessing.js  # ��������� ������
+-- styles/         # �����
�   L-- index.css   # �������� �����
+-- App.jsx         # ������� ��������� ����������
L-- main.jsx        # ����� �����
\\`\\`\\`

## ?? ����������

������� ������ ��� ������ ��� ����������� ��������. 
����� ����� ���������� ��������� ����� ���������� ����� Issues.

## ?? ��������

- **�����������**: https://github.com/ostrovde/dashboard-new
- **�������������**: GitHub Actions + Python Agent

---

*������� � ������� ����������� ������ ����������* ??
'''
        
        with open("README.md", "w", encoding='utf-8') as f:
            f.write(readme_content)
        
        # ���� � ������ ��������
        roadmap_content = f'''# ??? ���� �������� ��������

## �������: {time.strftime('%Y-%m-%d %H:%M:%S')}
## Issue: #{issue_number}

## ? ���������
- [x] ������� ��������� React �������
- [x] ������������ �����������
- [x] ������� �������
- [x] KPI ����������
- [x] ������ ��������
- [x] ���������� ������
- [x] ���������� ������������ (Recharts, Leaflet)

## ?? � ����������
- [ ] ���������� �������� ������
- [ ] ������������� ����� Leaflet
- [ ] ������� Recharts
- [ ] ���������� ������
- [ ] ������� �������

## ?? ����� �� �������

### ��������� ������
1. **���������� ����** - �������� Leaflet ����������
2. **�������** - �������� Recharts ��� ������������
3. **�������� ������** - ���������� CSV/API
4. **����������� �������** - �������� ������ ����������

### ������������ ����
- Machine learning ��������
- Real-time ����������
- ��������� ����������
- ���������� � Google Sheets

## ?? ����������

1. **�������**: �������������� ����� � �������
2. **�������**: ����������� ���������
3. **������**: �������������� ������������

---
*���� ����� ����������� �� ���� �������� �������*
'''
        
        with open("ROADMAP.md", "w", encoding='utf-8') as f:
            f.write(roadmap_content)
        
        print("? Documentation created")
        return True
    
    def create_advanced_dashboard(self, issue_number):
        """�������� ������� �������� ����������� ��������"""
        print("?? Starting advanced dashboard creation...")
        
        try:
            # 1. ������� ��������� �������
            self.create_project_structure()
            
            # 2. ����������� package.json
            self.create_package_json()
            
            # 3. ������� �������� �����
            self.create_main_files(issue_number)
            
            # 4. ������� React ����������
            self.create_react_components(issue_number)
            
            # 5. ������� ������� � ������
            self.create_utils_and_data()
            
            # 6. ������� ������������
            self.create_documentation(issue_number)
            
            print("?? Advanced dashboard created successfully!")
            return True
            
        except Exception as e:
            print(f"? Error creating dashboard: {e}")
            return False
    
    def run(self, issue_number):
        print(f"?? Agent started for issue #{issue_number}")
        print(f"?? Repository: {self.repo}")
        
        # ������� �����
        branch_name = f"feat/{issue_number}-advanced-dashboard"
        
        # ��������� � workdir ���� ����
        if os.path.exists("workdir"):
            os.chdir("workdir")
            print("?? Working in workdir/")
        else:
            print("?? Working in current directory")
        
        # ������� �����
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        print(f"?? Created branch: {branch_name}")
        
        # =============================================
        # ������� ���������� �������
        # =============================================
        
        print("??? Building advanced dashboard structure...")
        
        success = self.create_advanced_dashboard(issue_number)
        
        if not success:
            print("? Dashboard creation failed")
            return "Dashboard creation failed"
        
        # =============================================
        # ������ � ���
        # =============================================
            
        # ��������� ��� ���������
        subprocess.run(["git", "add", "."], check=True)
        
        # ��������
        commit_message = f"feat: create advanced dashboard structure for #{issue_number}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("?? Changes committed")
        
        # �����
        subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)
        print("?? Changes pushed to GitHub")
        
        # ������� PR
        try:
            pr_result = self.create_pr(issue_number, branch_name)
            pr_url = pr_result.get('html_url', 'URL not available')
            print(f"?? PR created: {pr_url}")
        except Exception as e:
            print(f"?? PR creation failed: {e}")
            pr_url = f"https://github.com/{self.repo}/pull/new/{branch_name}"
        
        print(f"? Success! Branch: {branch_name}")
        print("?? Advanced dashboard structure completed!")
        print("?? Next steps: Run 'npm install' and 'npm run dev'")
        
        return f"Advanced dashboard created | PR: {pr_url}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        issue_num = sys.argv[1]
    else:
        issue_num = input("Enter issue number: ")
    
    agent = Agent()
    result = agent.run(issue_num)
    print(result)