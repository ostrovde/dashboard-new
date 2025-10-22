#!/usr/bin/env python3
# diagnostics.py — версия без зависимости от Vite manifest
# Проверяет:
# 1) Наличие dist/index.html и dist/assets/*
# 2) Ссылки в dist/index.html (href/src) реально существуют
# 3) document.write в исходниках и в собранных js
# 4) Подсказки по картам/метрикам
import re, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
ASSETS = DIST / "assets"

ISSUES = []

def add_issue(kind, where, msg, fix=None, level="warn"):
    ISSUES.append({"kind": kind, "where": where, "msg": msg, "fix": fix, "level": level})

def exists_check():
    if not DIST.exists():
        add_issue("dist", "dist", "Папка dist не найдена. Сборка проходила?", level="error")
        return
    if not (DIST / "index.html").exists():
        add_issue("dist", "dist/index.html", "Файл index.html не найден в dist.", level="error")
    if not ASSETS.exists():
        add_issue("assets", "dist/assets", "Папка dist/assets не найдена. Rolldown/Vite сложил ассеты куда-то ещё?", level="warn")

def parse_index_links():
    index = DIST / "index.html"
    if not index.exists():
        return
    html = index.read_text(encoding="utf-8", errors="ignore")
    paths = set()
    # простейший парс: href="..." и src="..."
    for attr in re.findall(r'(?:href|src)=["\']([^"\']+)["\']', html):
        # интересуют относительные пути внутри dist
        if attr.startswith("http://") or attr.startswith("https://") or attr.startswith("//"):
            continue
        # убираем ведущие слеши
        rel = attr[1:] if attr.startswith("/") else attr
        paths.add(rel)
    missing = []
    for rel in sorted(paths):
        p = DIST / rel
        if not p.exists():
            missing.append(rel)
    if missing:
        add_issue("assets", "dist/index.html", f"В index.html есть ссылки на отсутствующие файлы: {missing[:10]}...", level="error")

def scan_document_write_sources():
    for p in SRC.rglob("*"):
        if p.suffix.lower() not in (".js", ".jsx", ".ts", ".tsx"):
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "document.write" in txt:
            add_issue("document-write", str(p), "Найден document.write в исходниках", 
                      "Заменить на безопасную вставку (DOMContentLoaded/requestAnimationFrame)")

def scan_document_write_build():
    if not ASSETS.exists():
        return
    for p in ASSETS.rglob("*.js"):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "document.write" in txt:
            add_issue("document-write", str(p), "Найден document.write в собранном бандле",
                      "Починить в исходниках, затем пересобрать")

def runtime_smells_sources():
    for p in SRC.rglob("*"):
        if p.suffix.lower() not in (".js", ".jsx", ".ts", ".tsx"):
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        # импорты вида from 'src/...' часто ломаются в проде без alias
        if re.search(r"from ['\"]src/.*['\"]", txt):
            add_issue("import", str(p), "Подозрительный импорт 'src/...'; лучше относительный путь или alias")

def kpi_hints():
    add_issue("map-kpis", "data", "Скрывать нули, округление 0.1, единицы ц/га и %, дедуп по ключу Контрагент+Год")

def main():
    exists_check()
    parse_index_links()
    scan_document_write_sources()
    scan_document_write_build()
    runtime_smells_sources()
    kpi_hints()

    # Вывод
    if "--json" in sys.argv:
        print(json.dumps({"issues": ISSUES}, ensure_ascii=False, indent=2))
    else:
        for i in ISSUES:
            print(f"[{i['level']}] [{i['kind']}] {i['where']}: {i['msg']}")
            if i.get("fix"): print(f"  fix: {i['fix']}")
    # Диагностика не должна блочить пайплайн на этом этапе:
    # Возвращаем 0, даже если есть предупреждения/ошибки — мы просто репортим.
    sys.exit(0)

if __name__ == "__main__":
    main()
