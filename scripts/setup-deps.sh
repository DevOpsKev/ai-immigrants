#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FONT_DIR="$REPO_ROOT/assets/fonts"

echo "==> Installing system dependencies..."
sudo apt-get update -qq || echo "    Warning: apt-get update had errors (non-essential repos), continuing..."
sudo apt-get install -y -qq librsvg2-bin pandoc > /dev/null

echo "==> Verifying..."
command -v rsvg-convert > /dev/null && echo "    rsvg-convert: OK" || { echo "    rsvg-convert: MISSING"; exit 1; }
command -v pandoc > /dev/null && echo "    pandoc: OK" || { echo "    pandoc: MISSING"; exit 1; }
fc-list | grep -q "Alfa Slab One" && echo "    Alfa Slab One: OK" || { echo "    Alfa Slab One: MISSING"; exit 1; }
fc-list | grep -q "Archivo Black" && echo "    Archivo Black: OK" || { echo "    Archivo Black: MISSING"; exit 1; }
fc-list | grep -q "Inter" && echo "    Inter: OK" || { echo "    Inter: MISSING"; exit 1; }

echo "==> Done."