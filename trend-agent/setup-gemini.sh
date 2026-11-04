#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TARGET="$PROJECT_DIR/.env"

if [ -e "$TARGET" ]; then
    echo "Refusing to overwrite existing $TARGET"
    exit 1
fi

printf "Paste your NEW Google AI Studio key (input is hidden): "
stty -echo
IFS= read -r GOOGLE_KEY
stty echo
printf "\n"

if [ -z "$GOOGLE_KEY" ]; then
    echo "No key entered; nothing was written."
    exit 1
fi

umask 077
{
    printf 'GOOGLE_API_KEY=%s\n' "$GOOGLE_KEY"
    printf '%s\n' \
        'FAST_LLM=google_genai:gemini-3.1-flash-lite' \
        'SMART_LLM=google_genai:gemini-3.1-flash-lite' \
        'STRATEGIC_LLM=google_genai:gemini-3.1-flash-lite' \
        'EMBEDDING=google_genai:models/gemini-embedding-001' \
        'RETRIEVER=duckduckgo' \
        'SCRAPER=bs' \
        'MAX_ITERATIONS=2' \
        'MAX_SUBTOPICS=3' \
        'TOTAL_WORDS=1200' \
        'LANGUAGE=chinese' \
        'IMAGE_GENERATION_ENABLED=false'
} > "$TARGET"

echo "Saved securely to $TARGET (permissions 600)."
