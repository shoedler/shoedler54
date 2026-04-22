#!/usr/bin/env bash
# Generate keymap image for the shoedler54 shield (DE-CH layout)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

python3 "$SCRIPT_DIR/py-zmk-keymap-gen.py" \
  --shield shoedler54 \
  --keymap "$REPO_ROOT/config/boards/shields/shoedler54/shoedler54_de_ch.keymap" \
  --font "Agave Nerd Font Mono" \
  --boards-dir "$REPO_ROOT/boards" \
  -o "$SCRIPT_DIR/shoedler54_keymap.png" \
  "$@"
