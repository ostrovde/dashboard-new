#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostics runner for RayAgro:
- Проверка билд-артефактов (dist/index.html, assets/)
- KPI-валидатор (scripts/validate_kpi.py data/sample_kpi.csv)
- Сводка предупреждений по картам/единицам измерения

Выход: JSON в stdout; не «валим» пайплайн на предупреждениях, но код ошибки >0,
если нет build-артефактов или KPI-валидатор дал ошибки.
"""
import json, os, subprocess, time
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
DIST = ROOT / "dist"
LOGS = ROOT / "logs"
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
    idx = DIST / "index.html"
    assets = DIST / "assets"
    return idx.exists() and assets.exists()

def run_kpi():
    """Запуск KPI-валидатора, возвращаем dict отчёта + код процесса."""
    script = ROOT / "scripts" / "validate_kpi.py"
    src = ROOT / "data" / "sample_kpi.csv"
    if not script.exists() or not src.exists():
        return {"skipped": True, "reason": "missing validator or sample data"}, 0
    code, out, err = run(["python3", str(script), str(src)], timeout=60)
    try:
        report = json.loads(out) if out.strip().startswith("{") else {"raw": out}
    except Exception:
        report = {"raw": out}
    # сохраняем отдельный лог валидатора
    ts = int(time.time())
    (LOGS / f"validator-{ts}.json").write_text(json.dumps({"code": code, "report": report}, ensure_ascii=False, indent=2), encoding="utf-8")
    return report, code

def main():
    issues = []
    exit_code = 0

    # 1) Build artifacts
    if not have_build():
        issues.append({
            "kind": "assets",
            "where": "dist",
            "msg": "Нет build-артефактов: dist/index.html или dist/assets",
            "level": "error"
        })
        exit_code = 1

    # 2) Политика карт/единиц (информативно)
    issues.append({
        "kind": "map-kpis",
        "where": "data",
        "msg": "Скрывать нули, округление 0.1, единицы ц/га и %, дедуп по ключу Контрагент+Год",
        "fix": None,
        "level": "warn"
    })

    # 3) KPI validator
    kpi_report, kpi_code = run_kpi()
    kpi_summary = {
        "skipped": kpi_report.get("skipped", False),
        "rows_in": kpi_report.get("rows_in"),
        "rows_out": kpi_report.get("rows_out"),
        "clean_path": kpi_report.get("clean_path"),
        "errors_count": len(kpi_report.get("errors", []) or []),
        "warnings_count": len(kpi_report.get("warnings", []) or []),
    }
    if not kpi_summary["skipped"]:
        if kpi_summary["errors_count"] > 0:
            exit_code = 1
        issues.append({
            "kind": "kpi",
            "where": kpi_report.get("source", "data/sample_kpi.csv"),
            "msg": f"KPI: {kpi_summary['rows_in']}→{kpi_summary['rows_out']}, "
                   f"err={kpi_summary['errors_count']}, warn={kpi_summary['warnings_count']}",
            "level": "error" if kpi_summary["errors_count"] > 0 else "info",
            "clean_path": kpi_summary["clean_path"]
        })
    else:
        issues.append({
            "kind": "kpi",
            "where": "scripts/validate_kpi.py",
            "msg": f"KPI validator skipped: {kpi_report.get('reason')}",
            "level": "info"
        })

    # Итоговый отчёт
    report = {"issues": issues}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return exit_code

if __name__ == "__main__":
    raise SystemExit(main())
