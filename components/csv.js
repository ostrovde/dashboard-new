export function parseCSV(text) {
  // очень простой парсер: первая строка — заголовки; разделитель — запятая
  // поддрежка кавычек минимальная (для наших демо-датасетов хватает)
  const lines = text.replace(/\r/g, "").trim().split("\n");
  if (!lines.length) return { columns: [], rows: [] };
  const columns = lines[0].split(",");
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const vals = lines[i].split(",");
    const row = {};
    for (let c = 0; c < columns.length; c++) {
      row[columns[c]] = (vals[c] ?? "").trim();
    }
    rows.push(row);
  }
  return { columns, rows };
}
