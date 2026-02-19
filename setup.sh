#!/usr/bin/env bash
set -euo pipefail

OS_NAME="$(uname -s)"

echo "==> Checking ffmpeg"
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg not found. Install it first:"
  if [[ "$OS_NAME" == "Darwin" ]]; then
    echo "  brew install ffmpeg"
  else
    echo "  sudo apt update && sudo apt install -y ffmpeg"
    echo "  # or: sudo dnf install -y ffmpeg"
  fi
  exit 1
fi

echo "==> Checking pipx"
if ! command -v pipx >/dev/null 2>&1; then
  echo "pipx not found. Install it first:"
  if [[ "$OS_NAME" == "Darwin" ]]; then
    echo "  brew install pipx"
  else
    echo "  sudo apt install -y pipx"
  fi
  exit 1
fi

echo "==> Ensuring pipx path"
pipx ensurepath >/dev/null 2>&1 || true

echo "==> Installing demucs with Python 3.12"
PYTHON_BIN="${PYTHON_BIN:-python3.12}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3.12 not found (expected $PYTHON_BIN). Install it and re-run."
  exit 1
fi

if ! command -v demucs >/dev/null 2>&1; then
  pipx install --python "$PYTHON_BIN" demucs
fi

echo "==> Ensuring torchcodec in demucs venv"
pipx runpip demucs install torchcodec

echo "==> Setting up local venv for web app"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "==> Done"
echo "Run: python3 web_app.py"
