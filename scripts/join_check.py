#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Join check between cleaned GEO and KPI:
- keys: (Контрагент, Год)
- input: data/cleaned_sample_geo.csv, data/cleaned_sample_kpi.csv
- output: JSON with counts and small samples of unmatched keys
Exit code: 0 if any matches > 0, 1 otherwise.
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "data" / "cleaned_sample_geo.csv"
KPI = ROOT / "data" / "cleaned_sample_kpi.csv"

def read_keys(path, cols):
    rows = []
    if not path.exists():
        return rows
    with open(path, "r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            key = (str(r.get(cols[0], "")).strip(), str(r.get(cols[1], "")).strip())
            if key[0] and key[1]:
                rows.append(key)
    return rows

def main():
    geo_keys = read_keys(GEO, ("Контрагент","Год"))
    kpi_keys = read_keys(KPI, ("Контрагент","Год"))

    sg = set(geo_keys)
    sk = set(kpi_keys)
    inter = sg & sk
    only_geo = sorted(sg - sk)[:10]
    only_kpi = sorted(sk - sg)[:10]

    out = {
        "geo_file": str(GEO),
        "kpi_file": str(KPI),
        "geo_keys": len(sg),
        "kpi_keys": len(sk),
        "matched": len(inter),
        "only_geo_samples": only_geo,
        "only_kpi_samples": only_kpi,
        "hint": "Совпадений 0 — проверьте написание 'Контрагент' и 'Год' в обоих наборах и их значения."
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if len(inter) > 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
