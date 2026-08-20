#!/usr/bin/env bash
set -euo pipefail

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  PYTHON=python
fi

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

echo "===== Running website tests ====="
"$PYTHON" -m pip install pytest==8.3.4
(
  cd "$ROOT/web"
  "$PYTHON" -m pytest tests -v --junitxml="$RESULTS_DIR/web.xml"
)

echo "All unit tests passed."
