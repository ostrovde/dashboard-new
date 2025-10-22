#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostics runner for RayAgro:
- Build artifacts check (dist/)
- KPI validator (scripts/validate_kpi.py data/sample_kpi.csv)
- GEO validator (scripts/geo_check.py data/sample_geo.csv)
- Public data presence (public/data/kpi.csv, public/data/geo.csv)
- Map/KPI policy reminder
Exits with code>0 on build absence or validator errors; public/data missing is warn with suggested fix.
"""
import json, os, subprocess, time
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
DIST = ROOT / "dist"
LOGS = ROOT / "logs"
PUBD = ROOT / "public" / "data"
LOGS.mkdir(exist_ok=True)

def run(cmd, timeout=300):
    p = subprocess.Popen(cmd, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out, err
    except subprocess.TimeoutExpired:
        p.kill(); out, err = p.communicate()
        return 124, out, err

def have_build():
    return (DIST / "index.html").exists() and (DIST / "assets").exists()

def _run_json(cmd, log_prefix, timeout=60):
    code, out, err = run(cmd, timeout=timeout)
    try:
        payload = json.loads(out) if out.strip().startswith("{") else {"raw": out}
    except Exception:
        payload = {"raw": out}
    ts = int(time.time())
    (LOGS / f"{log_prefix}-{ts}.json").write_text(
        json.dumps({"code": code, "report": payload}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return payload, code

def run_kpi():
    script = ROOT / "scripts" / "validate_kpi.py"
    src = ROOT / "data" / "sample_kpi.csv"
    if not script.exists() or not src.exists():
        return {"skipped": True, "reason": "missing validator or sample data"}, 0
    return _run_json(["python3", str(script), str(src)], "validator-kpi", timeout=60)

def run_geo():
    script = ROOT / "scripts" / "geo_check.py"
    src = ROOT / "data" / "sample_geo.csv"
    if not script.exists() or not src.exists():
        return {"skipped": True, "reason": "missing geo validator or sample data"}, 0
    return _run_json(["python3", str(script), str(src)], "validator-geo", timeout=60)

def main():
    issues = []
    exit_code = 0

    # 1) Build artifacts
    if not have_build():
        issues.append({"kind":"assets","where":"dist","msg":"Нет build-артефактов: dist/index.html или dist/assets","level":"error"})
        exit_code = 1

    # 2) Policy reminder
    issues.append({
        "kind":"map-kpis","where":"data",
        "msg":"Скрывать нули, округление 0.1, единицы ц/га и %, дедуп по ключу Контрагент+Год",
        "fix": None, "level":"warn"
    })

    # 3) KPI validator
    kpi_report, _ = run_kpi()
    if not kpi_report.get("skipped"):
        kpi_errs = len(kpi_report.get("errors", []) or [])
        kpi_warns = len(kpi_report.get("warnings", []) or [])
        issues.append({
            "kind":"kpi","where":kpi_report.get("source","data/sample_kpi.csv"),
            "msg":f"KPI: {kpi_report.get('rows_in')}→{kpi_report.get('rows_out')}, err={kpi_errs}, warn={kpi_warns}",
            "level":"error" if kpi_errs>0 else "info",
            "clean_path":kpi_report.get("clean_path")
        })
        if kpi_errs>0: exit_code = 1
    else:
        issues.append({"kind":"kpi","where":"scripts/validate_kpi.py","msg":f"skipped: {kpi_report.get('reason')}","level":"info"})

    # 4) GEO validator
    geo_report, _ = run_geo()
    if not geo_report.get("skipped"):
        geo_errs = len(geo_report.get("errors", []) or [])
        geo_warns = len(geo_report.get("warnings", []) or [])
        issues.append({
            "kind":"geo","where":geo_report.get("source","data/sample_geo.csv"),
            "msg":f"GEO: {geo_report.get('rows_in')}→{geo_report.get('rows_out')}, err={geo_errs}, warn={geo_warns}",
            "level":"error" if geo_errs>0 else "info",
            "clean_path":geo_report.get("clean_path")
        })
        if geo_errs>0: exit_code = 1
    else:
        issues.append({"kind":"geo","where":"scripts/geo_check.py","msg":f"skipped: {geo_report.get('reason')}","level":"info"})

    # 5) Public data presence (front reads /data/*.csv from dist)
    need = [("public/data/kpi.csv","/data/kpi.csv"), ("public/data/geo.csv","/data/geo.csv")]
    for fs_path, url_path in need:
        p = ROOT / fs_path
        if not p.exists():
            issues.append({
                "kind":"public-data","where":fs_path,
                "msg":f"Отсутствует {url_path} (frontend будет 404)",
                "level":"warn",
                "fix":"Запусти: /run?task=publish (если есть cleaned_*), или /run?task=ensure (создать заглушки)"
            })

    report = {"issues": issues}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return exit_code

if __name__ == "__main__":
    raise SystemExit(main())
