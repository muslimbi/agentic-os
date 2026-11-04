#!/usr/bin/env sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_DIR"

if [ ! -x .venv/bin/agentic-os-server ]; then
  printf '%s\n' "Virtual environment not found. Run ./install.sh first." >&2
  exit 1
fi

HOST=${HOST:-127.0.0.1}
PORT=${PORT:-8765}

case "$HOST" in
  127.0.0.1|localhost|::1) ;;
  *) printf '%s\n' "Warning: this unauthenticated scaffold is exposed on $HOST." >&2 ;;
esac

exec .venv/bin/agentic-os-server --host "$HOST" --port "$PORT"
