#!/usr/bin/env python3
import re, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
MANIFEST = DIST / "manifest.json"

ISSUES = []

def add_issue(kind, where, msg, fix=None):
    ISSUES.append({"kind": kind, "where": where, "msg": msg, "fix": fix})

def scan_document_write():
    for p in SRC.rglob("*"):
        if p.suffix.lower() not in (".js",".jsx",".ts",".tsx"):
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "document.write" in txt:
            add_issue("document-write", str(p), "Found document.write usage",
                      "Replace with safe DOM insertion (DOMContentLoaded/requestAnimationFrame)")

def validate_assets():
    if not MANIFEST.exists():
        add_issue("assets", "dist/manifest.json", "Vite manifest not found (did build succeed?)")
        return
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception:
        add_issue("assets", "dist/manifest.json", "Manifest JSON parse error")
        return
    missing = []
    for _, entry in manifest.items():
        file = entry.get("file")
        if file and not (DIST / file).exists():
            missing.append(file)
    if missing:
        add_issue("assets", "dist", f"Missing assets: {missing[:10]}...")

def check_runtime_smells():
    for p in SRC.rglob("*"):
        if p.suffix.lower() not in (".js",".jsx",".ts",".tsx"):
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if re.search(r"from ['\"]src/.*['\"]", txt):
            add_issue("import", str(p), "Suspicious import from 'src/...'; prefer relative paths or alias")
    add_issue("map-kpis", "data", "Ensure zeros hidden, rounding 0.1, units ц/га/%; dedup key (Контрагент+Год)")

def main():
    scan_document_write()
    validate_assets()
    check_runtime_smells()
    if "--json" in sys.argv:
        print(json.dumps({"issues": ISSUES}, ensure_ascii=False, indent=2))
    else:
        for i in ISSUES:
            print(f"[{i['kind']}] {i['where']}: {i['msg']}")
            if i.get("fix"): print(f"  fix: {i['fix']}")
    sys.exit(0 if not ISSUES else 2)

if __name__ == "__main__":
    main()
