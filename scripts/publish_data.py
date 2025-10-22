#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Копирует очищенные CSV + сводку в public/data/ для фронтенда.
- data/cleaned_sample_kpi.csv -> public/data/kpi.csv
- data/cleaned_sample_geo.csv -> public/data/geo.csv
- data/kpi_stats.csv          -> public/data/kpi_stats.csv
"""
import shutil, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = {
    "kpi.csv": ROOT / "data" / "cleaned_sample_kpi.csv",
    "geo.csv": ROOT / "data" / "cleaned_sample_geo.csv",
    "kpi_stats.csv": ROOT / "data" / "kpi_stats.csv",
}
PUB = ROOT / "public" / "data"
PUB.mkdir(parents=True, exist_ok=True)

out = {"copied": [], "missing": []}

for dst_name, src_path in SRC.items():
    if src_path.exists():
        shutil.copy2(src_path, PUB / dst_name)
        out["copied"].append(str(PUB / dst_name))
    else:
        out["missing"].append(str(src_path))

print(json.dumps(out, ensure_ascii=False, indent=2))
