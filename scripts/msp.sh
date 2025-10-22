#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="127.0.0.1"; PORT="${PORT:-8078}"; ORCH="http://$HOST:$PORT"
case "${1:-}" in
  up) pkill -f scripts/micro_orchestrator.py 2>/dev/null || true; nohup python3 "$ROOT/scripts/micro_orchestrator.py" > "$ROOT/.orchestrator.log" 2>&1 & sleep 1; curl -fsS "$ORCH/health" >/dev/null; echo "[msp] orchestrator: OK";;
  stop) pkill -f scripts/micro_orchestrator.py 2>/dev/null || true; echo "[msp] orchestrator: stopped";;
  status) curl -fsS "$ORCH/health" | jq .;;
  e2e) curl -fsS -X POST "$ORCH/run?task=e2e" | jq .; curl -fsS -X POST "$ORCH/donesheet" | jq .;;
  smoke) curl -fsS -X POST "$ORCH/run?task=smoke" | jq .;;
  pr) curl -fsS -X POST --data-binary $'### RayAgro MCP — E2E\n- KPI/GEO validated & published\n- Build + Smoke OK\n- Diagnostics report in logs/' "$ORCH/pr" | jq .; curl -fsS -X POST "$ORCH/donesheet" | jq .;;
  *) echo "Usage: scripts/msp.sh {up|stop|status|e2e|smoke|pr}" >&2; exit 1;;
esac
