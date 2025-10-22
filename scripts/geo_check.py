#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geo validator for RayAgro
Проверяем входной CSV с координатами для карт:
- Обязательные столбцы: Контрагент, Год, Широта, Долгота
- Диапазоны: Широта [-90..90], Долгота [-180..180]
- Дедуп по ключу (Контрагент+Год)
- Округление координат до 1e-6 (≈ 0.1 м) для стабильности рендера
Выход: JSON-отчёт; code 0 при отсутствии ошибок, 1 если есть ошибки.
Создаём очищенный файл data/cleaned_<name>.csv
"""
import csv, sys, json, os, math
from pathlib import Path

REQ = ["Контрагент","Год","Широта","Долгота"]

def to_float(v):
    if v is None or v == "": return None
    try:
        return float(str(v).replace(",", "."))
    except:
        return None

def round6(x):
    return None if x is None else round(x, 6)

def read_csv(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        cols = r.fieldnames or []
        miss = [c for c in REQ if c not in cols]
        if miss:
            return [], {"errors":[{"msg": f"Отсутствуют колонки: {', '.join(miss)}"}]}
        for row in r:
            rows.append({k: (v.strip() if isinstance(v,str) else v) for k,v in row.items()})
    return rows, {}

def validate(rows):
    errors, warns, cleaned = [], [], []
    seen = set()
    for i, row in enumerate(rows, start=2):  # учитываем заголовок
        k = (row.get("Контрагент",""), row.get("Год",""))
        if k in seen:
            errors.append({"row": i, "msg": f"Дубликат ключа Контрагент+Год: {k}"})
            continue
        seen.add(k)

        lat = to_float(row.get("Широта"))
        lon = to_float(row.get("Долгота"))
        if lat is None or lon is None:
            errors.append({"row": i, "msg": "Пустые/нечисловые координаты"})
            continue
        if not (-90 <= lat <= 90):
            errors.append({"row": i, "col":"Широта", "msg": f"Вне диапазона [-90..90]: {lat}"})
            continue
        if not (-180 <= lon <= 180):
            errors.append({"row": i, "col":"Долгота", "msg": f"Вне диапазона [-180..180]: {lon}"})
            continue

        out = dict(row)
        out["Широта"] = f"{round6(lat):.6f}"
        out["Долгота"] = f"{round6(lon):.6f}"
        cleaned.append(out)
    return cleaned, errors, warns

def write_clean(path_in, cleaned):
    p = Path(path_in)
    out = p.parent / ("cleaned_" + p.name)
    if not cleaned:
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(",".join(REQ) + "\n")
        return str(out)
    cols = list(cleaned[0].keys())
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in cleaned:
            w.writerow(r)
    return str(out)

def main():
    src = sys.argv[1] if len(sys.argv)>1 else os.getenv("GEO_CSV","data/sample_geo.csv")
    rows, err = read_csv(src)
    report = {"source": src, "errors":[], "warnings":[], "clean_path": None, "rows_in": len(rows), "rows_out": 0}
    if err:
        report["errors"] = err.get("errors",[])
        print(json.dumps(report, ensure_ascii=False, indent=2))
        sys.exit(1)
    cleaned, errors, warns = validate(rows)
    report["errors"] = errors
    report["warnings"] = warns
    report["rows_out"] = len(cleaned)
    report["clean_path"] = write_clean(src, cleaned)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if not errors else 1)

if __name__ == "__main__":
    main()
