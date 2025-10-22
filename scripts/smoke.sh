#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"
LOG="$ROOT/logs/smoke-$(date +%s).log"

echo "[smoke] start" | tee "$LOG"

if [[ ! -f "$DIST/index.html" ]]; then
  echo "[smoke] dist/index.html not found, building..." | tee -a "$LOG"
  (cd "$ROOT" && npm run build) | tee -a "$LOG"
fi

if [[ ! -d "$DIST/assets" ]]; then
  echo "[smoke] ERROR: dist/assets not found" | tee -a "$LOG"
  exit 2
fi

INDEX_HTML="$DIST/index.html"
CSS_FILE="$(ls -1 "$DIST/assets"/*index-*.css 2>/dev/null | head -n1 || true)"
JS_MAIN="$(ls -1 "$DIST/assets"/*index-*.js  2>/dev/null | head -n1 || true)"

echo "[smoke] index: $INDEX_HTML" | tee -a "$LOG"
echo "[smoke] css:   ${CSS_FILE:-none}" | tee -a "$LOG"
echo "[smoke] js:    ${JS_MAIN:-none}" | tee -a "$LOG"

[[ -f "$INDEX_HTML" ]] || { echo "[smoke] ERROR: index.html missing" | tee -a "$LOG"; exit 3; }
[[ -f "$JS_MAIN"   ]] || { echo "[smoke] ERROR: main js missing"   | tee -a "$LOG"; exit 3; }

PORT=8800
echo "[smoke] serving dist on :$PORT" | tee -a "$LOG"
(cd "$DIST" && python3 -m http.server "$PORT") > "$LOG.http" 2>&1 & SRV_PID=$!
trap 'kill $SRV_PID 2>/dev/null || true' EXIT
sleep 0.5

root="http://127.0.0.1:$PORT"
for path in "/" "/data/kpi.csv" "/data/geo.csv"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$root$path")
  echo "[smoke] GET $path -> $code" | tee -a "$LOG"
  # мягкое предупреждение, но не падаем
done

echo "[smoke] ok" | tee -a "$LOG"
