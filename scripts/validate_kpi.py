#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KPI validator:
- input: CSV with columns (at least) Контрагент, Год, Урожайность_ц_га (или аналогичные)
- removes duplicates by (Контрагент, Год)
- removes zero/empty yields
- outputs JSON to stdout and writes cleaned CSV to data/cleaned_sample_kpi.csv
- additionally computes per-Контрагент stats across years and writes data/kpi_stats.csv:
  Mean (ц/га), SD (ц/га), CV% (%), WAASB_proxy (0..100, где 100 — стабильнее)
  rounding to 0.1 for Mean/SD/CV
"""
import csv, json, math, sys
from pathlib import Path
from statistics import mean, pstdev

ROOT = Path(__file__).resolve().parents[1]
OUT_CLEAN = ROOT / "data" / "cleaned_sample_kpi.csv"
OUT_STATS = ROOT / "data" / "kpi_stats.csv"

def to_float(val):
    if val is None or str(val).strip() == "":
        return None
    try:
        return float(str(val).replace(",", "."))
    except:
        return None

def pick(row, names):
    # case-insensitive pick
    lower = {k.lower(): v for k, v in row.items()}
    for n in names:
        if n in row and row[n] != "":
            return row[n]
        if n.lower() in lower and lower[n.lower()] != "":
            return lower[n.lower()]
    return ""

def load_rows(path):
    with open(path, "r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        return list(rdr)

def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def round01(x):
    return None if x is None or not math.isfinite(x) else round(x*10)/10.0

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: validate_kpi.py <csv>"}))
        return 2
    src = Path(sys.argv[1])
    rows = load_rows(src)

    key_dups = set()
    seen = set()
    cleaned = []
    errors = []

    for i, r in enumerate(rows, start=1):
        contr = pick(r, ["Контрагент", "contragent", "client", "Компания"]).strip()
        year  = str(pick(r, ["Год", "year"])).strip()
        yld   = to_float(pick(r, ["Урожайность_ц_га","Урожайность, ц/га","Yield_c_ha","Yield","yield","y"]))

        if (contr, year) in seen:
            errors.append({"row": i, "msg": f"Дубликат ключа Контрагент+Год: { (contr, year) }"})
            key_dups.add((contr, year))
            continue
        seen.add((contr, year))

        if yld is None or yld == 0:
            errors.append({"row": i, "msg": "Нулевая/пустая урожайность (скрыть/исключить)"})
            continue

        cleaned.append({"Контрагент": contr, "Год": year, "Урожайность_ц_га": f"{round01(yld):.1f}"})

    write_csv(OUT_CLEAN, cleaned, ["Контрагент","Год","Урожайность_ц_га"])

    # === Перегруппируем по Контрагенту, считаем Mean/SD/CV% и WAASB proxy ===
    group = {}
    for r in cleaned:
        group.setdefault(r["Контрагент"], []).append(to_float(r["Урожайность_ц_га"]))

    # SD по генеральной совокупности (pstdev), CV% = SD/Mean*100
    stats_rows = []
    sds = []
    for c, ys in group.items():
        m = mean(ys) if ys else None
        sd = pstdev(ys) if ys and len(ys) > 1 else 0.0
        cv = (sd / m * 100.0) if (m and m != 0) else 0.0
        stats_rows.append({
            "Контрагент": c,
            "Mean_ц_га": round01(m) if m is not None else "",
            "SD_ц_га": round01(sd),
            "CV_%": round01(cv),
            # waasb_proxy позже заполним после ранжирования
            "WAASB_proxy": 0.0,
        })
        sds.append(sd)

    # WAASB proxy: чем меньше SD, тем стабильнее.
    # Возьмем ранговое устойчивое преобразование в 0..100: 100 — лучший (наименьший SD).
    if sds:
        pairs = sorted([(sd, i) for i, sd in enumerate(sds)])
        ranks = {i: rank for rank, (_, i) in enumerate(pairs, start=1)}
        N = len(sds)
        for idx, row in enumerate(stats_rows):
            r = ranks[idx]
            stability = 100.0 * (1.0 - (r - 1) / max(1, N - 1))  # от 100 до ~0
            row["WAASB_proxy"] = round01(stability)

    write_csv(OUT_STATS, stats_rows, ["Контрагент","Mean_ц_га","SD_ц_га","CV_%","WAASB_proxy"])

    out = {
        "source": str(src),
        "errors": errors,
        "warnings": [],
        "clean_path": str(OUT_CLEAN),
        "stats_path": str(OUT_STATS),
        "rows_in": len(rows),
        "rows_out": len(cleaned)
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
