#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${PORT:-8088}"
LOG="${HOME}/http${PORT}.log"

case "${1:-}" in
  start)
    # убьём все процессы на порту и поднимем чисто
    fuser -k "${PORT}/tcp" 2>/dev/null || true
    cd "${ROOT}/dist"
    nohup python3 -m http.server "${PORT}" > "${LOG}" 2>&1 &
    sleep 0.7
    curl -I "http://127.0.0.1:${PORT}/" | sed -n '1p'
    ;;

  stop)
    fuser -k "${PORT}/tcp" 2>/dev/null || true
    echo "stopped :${PORT}"
    ;;

  status)
    ss -lntp | grep " ${PORT} " || echo "no listener on :${PORT}"
    tail -n 20 "${LOG}" 2>/dev/null || true
    ;;

  restart)
    "$0" stop
    "$0" start
    ;;

  *)
    echo "Usage: $0 {start|stop|status|restart}"
    exit 2
    ;;
esac
