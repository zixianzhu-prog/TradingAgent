#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SERVICE_NAME="serenity-trade-gemini"
ACCOUNT_NAME="${USER:?USER is not set}"
SECRET_DIR="$PROJECT_DIR/.secrets"
SECRET_FILE="$SECRET_DIR/gemini_api_key"

umask 077
mkdir -p "$SECRET_DIR"
security find-generic-password \
  -a "$ACCOUNT_NAME" \
  -s "$SERVICE_NAME" \
  -w > "$SECRET_FILE"

if [ ! -s "$SECRET_FILE" ]; then
  rm -f "$SECRET_FILE"
  echo "Keychain item could not be exported." >&2
  exit 1
fi

chmod 600 "$SECRET_FILE"
echo "Local secret created with owner-only permissions; Git ignores .secrets/."
