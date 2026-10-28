#!/bin/sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
RUNTIME_ROOT="$PROJECT_ROOT/.runtime/rdagent"

mkdir -p "$RUNTIME_ROOT" "$PROJECT_ROOT/.runtime/prefect"
export ARTIFACT_SIGNING_KEY_PATH="$RUNTIME_ROOT/artifact_signing.key"
export PREFECT_HOME="$PROJECT_ROOT/.runtime/prefect"

exec "$PROJECT_ROOT/work/RD-Agent/.venv/bin/rdagent" "$@"
