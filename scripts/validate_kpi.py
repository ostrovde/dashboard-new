#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KPI validator for RayAgro

Правила:
- Скрывать нули (урожайность == 0 → ошибка/исключение из набора)
- Округление до 0.1 (одна десятичная)
- Единицы: урожайность — ц/га; проценты — 0..100%
- Дедуп по ключу (Контрагент + Год)

Выход: JSON-отчёт в stdout; код возврата 0 если только предупреждения, 1 если есть ошибки.
"""
import csv, sys, json, math, os
from pathlib import Path

PCT_COLS = ["CV_%", "WAASB_proxy_%"]

def read_csv(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        missing = [c for c in ("Контрагент","Год","Урожайность_ц_га") if c not in cols]
        if missing:
            return [], {"errors":[{"msg":f"Отсутствуют колонки: {', '.join(missing)}"}]}
        for r in reader:
            rows.append({k: (v.strip() if isinstance(v,str) else v) for k,v in r.items()})
    return rows, {}

def to_float(val):
    if val is None or val == "":
        return None
    try:
        return float(str(val).replace(",", "."))
    except:
        return None

def round01(x):
    return None if x is None else round(x*10)/10.0

def validate(rows):
    errors, warns = [], []
    seen = set()
    cleaned = []
    for i, r in enumerate(rows, start=2):  # учёт заголовка
        k = (r.get("Контрагент",""), r.get("Год",""))
        if k in seen:
            errors.append({"row":i, "msg": f"Дубликат ключа Контрагент+Год: {k}"})
            continue
        seen.add(k)

        y = to_float(r.get("Урожайность_ц_га"))
        if y is None:
            errors.append({"row":i, "msg":"Пустая урожайность"})
            continue
        if y == 0:
            errors.append({"row":i, "msg":"Нулевая урожайность (должна быть скрыта/исключена)"})
            continue
        y_r = round01(y)
        # предупреждаем, если отличается больше, чем на 0.05
        if not math.isclose(y, y_r, rel_tol=0, abs_tol=0.049):
            warns.append({"row":i, "msg":f"Округление урожайности до 0.1: {y} -> {y_r}"})

        out = dict(r)
        out["Урожайность_ц_га"] = f"{y_r:.1f}"

        for c in PCT_COLS:
            v = r.get(c, "")
            if v == "":
                continue
            f = to_float(v)
            if f is None:
                errors.append({"row":i, "col":c, "msg":f"Некорректное число в {c}: '{v}'"})
                continue
            if f < 0 or f > 100:
                errors.append({"row":i, "col":c, "msg":f"{c} вне 0..100: {f}"})
            f_r = round01(f)
            if not math.isclose(f, f_r, rel_tol=0, abs_tol=0.049):
                warns.append({"row":i, "col":c, "msg":f"Округление до 0.1: {c}: {f} -> {f_r}"})
            out[c] = f"{f_r:.1f}"
        cleaned.append(out)

    return cleaned, errors, warns

def write_clean(path_in, cleaned):
    p = Path(path_in)
    out = p.parent / ("cleaned_" + p.name)
    if not cleaned:
        # всё фильтранулось — запишем пустой файл с заголовком, если возможно
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write("Контрагент,Год,Урожайность_ц_га,Mean,SD,CV_%,WAASB_proxy_%\n")
        return str(out)
    cols = list(cleaned[0].keys())
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in cleaned:
            w.writerow(r)
    return str(out)

def main():
    src = sys.argv[1] if len(sys.argv)>1 else os.getenv("KPI_CSV","data/sample_kpi.csv")
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
