// Функции для обработки данных
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
};