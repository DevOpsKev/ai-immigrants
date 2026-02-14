#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FONT_DIR="$REPO_ROOT/assets/fonts"

echo "==> Installing system dependencies..."
sudo apt-get update -qq || echo "    Warning: apt-get update had errors (non-essential repos), continuing..."
sudo apt-get install -y -qq librsvg2-bin pandoc > /dev/null

echo "==> Done."