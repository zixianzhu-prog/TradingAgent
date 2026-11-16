#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
echo "Gemini Keychain loading is no longer needed; running the no-API-key evidence preparation workflow."
cd "$PROJECT_DIR"
exec ./run-daily-investment-agent.sh
