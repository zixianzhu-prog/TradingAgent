#!/bin/sh
set -eu

SERVICE_NAME="serenity-trade-gemini"
ACCOUNT_NAME="${USER:?USER is not set}"

printf "Paste a newly generated Gemini API key (input is hidden): "
stty -echo < /dev/tty
trap 'stty echo < /dev/tty' EXIT HUP INT TERM
IFS= read -r GEMINI_KEY < /dev/tty
stty echo < /dev/tty
trap - EXIT HUP INT TERM
printf "\n"

if [ -z "$GEMINI_KEY" ]; then
  echo "No key entered; Keychain was not changed." >&2
  exit 1
fi

security add-generic-password \
  -U \
  -a "$ACCOUNT_NAME" \
  -s "$SERVICE_NAME" \
  -w "$GEMINI_KEY" >/dev/null

unset GEMINI_KEY
echo "Gemini API key saved in macOS Keychain under service: $SERVICE_NAME"
