// Цветовая палитра RayAgro
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
};