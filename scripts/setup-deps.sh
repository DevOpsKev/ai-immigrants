#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "==> Installing system dependencies..."
sudo apt-get update -qq || echo "    Warning: apt-get update had errors (non-essential repos), continuing..."
sudo apt-get install -y -qq \
  pandoc \
  texlive-xetex \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-latex-recommended \
  lmodern \
  > /dev/null

echo "==> Verifying..."
command -v pandoc > /dev/null && echo "    pandoc: OK" || { echo "    pandoc: MISSING"; exit 1; }
command -v xelatex > /dev/null && echo "    xelatex: OK" || { echo "    xelatex: MISSING"; exit 1; }
fc-list | grep -q "TeX Gyre Pagella" && echo "    TeX Gyre Pagella: OK" || { echo "    TeX Gyre Pagella: MISSING"; exit 1; }
fc-list | grep -q "TeX Gyre Heros" && echo "    TeX Gyre Heros: OK" || { echo "    TeX Gyre Heros: MISSING"; exit 1; }

echo "==> Done."