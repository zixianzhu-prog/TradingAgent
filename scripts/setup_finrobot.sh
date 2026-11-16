#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
FINROBOT_DIR="$PROJECT_DIR/work/FinRobot"
VENV_DIR="$FINROBOT_DIR/finrobot_desktop/.venv"

if [ ! -d "$FINROBOT_DIR/.git" ]; then
  echo "FinRobot source is missing at $FINROBOT_DIR" >&2
  echo "Clone https://github.com/AI4Finance-Foundation/FinRobot.git there first." >&2
  exit 1
fi

python3.11 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -e "$FINROBOT_DIR/finrobot_desktop"
"$VENV_DIR/bin/finrobot" --version

echo "FinRobot V2 environment is ready at $VENV_DIR"
echo "Set FINROBOT_LLM_API_KEY only in the current terminal session before enabling finrobot-cli mode."
