#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ensure public/data/ has CSV placeholders for frontend:
- creates public/data/ if missing
- creates kpi.csv and geo.csv with headers if missing
- does NOT overwrite existing files
Outputs JSON summary
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "public" / "data"
PUB.mkdir(parents=True, exist_ok=True)

kpi_path = PUB / "kpi.csv"
geo_path = PUB / "geo.csv"

created = []
skipped = []

if not kpi_path.exists():
    kpi_path.write_text("Контрагент,Год,Урожайность_ц_га\n", encoding="utf-8")
    created.append(str(kpi_path))
else:
    skipped.append(str(kpi_path))

if not geo_path.exists():
    geo_path.write_text("Контрагент,Год,Широта,Долгота\n", encoding="utf-8")
    created.append(str(geo_path))
else:
    skipped.append(str(geo_path))

print(json.dumps({"created": created, "skipped": skipped}, ensure_ascii=False, indent=2))
