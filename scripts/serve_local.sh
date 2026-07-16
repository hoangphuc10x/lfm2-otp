#!/usr/bin/env bash
# Dựng endpoint cục bộ bằng docker-compose để tự benchmark trước khi nộp.
# Cần image đã build (scripts/build_and_push.sh) và GPU + nvidia-container-toolkit.
#
#   bash scripts/serve_local.sh up      # khởi động + chờ healthy
#   bash scripts/serve_local.sh logs
#   bash scripts/serve_local.sh down
set -euo pipefail
cmd="${1:-up}"

case "$cmd" in
  up)
    docker compose up -d
    echo "[serve] chờ healthcheck..."
    for i in $(seq 1 60); do
      if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
        echo "[serve] healthy tại http://localhost:8000"; exit 0
      fi
      sleep 5
    done
    echo "[serve] chưa healthy sau 5 phút — xem 'docker compose logs'"; exit 1
    ;;
  logs) docker compose logs -f ;;
  down) docker compose down ;;
  *) echo "dùng: $0 {up|logs|down}"; exit 1 ;;
esac
