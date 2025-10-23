import React, { useState } from "react";

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
}