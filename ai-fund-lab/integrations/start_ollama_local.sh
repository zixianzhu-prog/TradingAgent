#!/bin/sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)

export OLLAMA_MODELS="$PROJECT_ROOT/tools/ollama-models"
export OLLAMA_LLM_LIBRARY=cpu
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_CONTEXT_LENGTH=1024

exec "$PROJECT_ROOT/tools/ollama-v0.40.12/ollama" serve
