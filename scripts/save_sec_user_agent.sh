#!/bin/sh
set -eu
PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SECRET_DIR="$PROJECT_DIR/.secrets"
SECRET_FILE="$SECRET_DIR/sec_user_agent"
mkdir -p "$SECRET_DIR"
chmod 700 "$SECRET_DIR"
printf "Enter a descriptive SEC User-Agent with contact email\nExample: SerenityResearch your-email@example.com\n> "
IFS= read -r VALUE
case "$VALUE" in
  *"@"*) ;;
  *) echo "The SEC User-Agent must include a contact email." >&2; exit 2 ;;
esac
umask 077
printf '%s\n' "$VALUE" > "$SECRET_FILE"
chmod 600 "$SECRET_FILE"
echo "SEC User-Agent saved locally. Git ignores .secrets/."
