#!/usr/bin/env bash
set -euo pipefail

pick_python() {
  if [[ -n "${PYTHON:-}" ]] && command -v "$PYTHON" >/dev/null 2>&1; then
    printf '%s\n' "$PYTHON"
    return
  fi
  local candidate
  for candidate in python3.12 python3.11 python3.10 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return
    fi
  done
  echo "Python 3.9+ is required to run unit tests." >&2
  exit 1
}

PYTHON="$(pick_python)"
PY_VERSION="$("$PYTHON" -c 'import sys; print("%d.%d" % (sys.version_info[0], sys.version_info[1]))')"
PY_MAJOR="$("$PYTHON" -c 'import sys; print(sys.version_info[0])')"
PY_MINOR="$("$PYTHON" -c 'import sys; print(sys.version_info[1])')"

if [[ "$PY_MAJOR" -lt 3 ]] || { [[ "$PY_MAJOR" -eq 3 ]] && [[ "$PY_MINOR" -lt 9 ]]; }; then
  echo "Unit tests need Python 3.9 or newer. Found $PYTHON ($PY_VERSION)." >&2
  echo "Install Python 3.12, then run: PYTHON=python3.12 bash scripts/run-tests.sh" >&2
  exit 1
fi

echo "Using $PYTHON ($PY_VERSION)"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="${RESULTS_DIR:-$ROOT/test-results}"
COVERAGE_DIR="${COVERAGE_DIR:-$ROOT/coverage}"

mkdir -p "$RESULTS_DIR" "$COVERAGE_DIR"

run_service_tests() {
  local service="$1"
  local service_dir="$ROOT/services/$service"
  echo "===== Running $service tests ====="
  "$PYTHON" -m pip install -r "$service_dir/requirements.txt"
  (
    cd "$service_dir"
    "$PYTHON" -m pytest tests \
      -v \
      --junitxml="$RESULTS_DIR/${service}.xml" \
      --cov=app \
      --cov-report="xml:$COVERAGE_DIR/${service}.xml" \
      --cov-report=term
  )
}

run_service_tests hotel-service
run_service_tests room-service
run_service_tests booking-service
run_service_tests payment-service
run_service_tests notification-service

echo "===== Running website tests ====="
"$PYTHON" -m pip install pytest==8.3.4
(
  cd "$ROOT/web"
  "$PYTHON" -m pytest tests -v --junitxml="$RESULTS_DIR/web.xml"
)

echo "All unit tests passed."
