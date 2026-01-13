#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC_SVG="$ROOT_DIR/static/images/ncs-white.svg"
OUT_DIR="$ROOT_DIR/static/images"

if [ ! -f "$SRC_SVG" ]; then
  echo "ERROR: Source logo not found: $SRC_SVG" >&2
  exit 1
fi

if ! command -v convert >/dev/null 2>&1; then
  echo "ERROR: ImageMagick 'convert' not found. Install it (e.g. sudo apt-get install -y imagemagick librsvg2-bin)" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

# 512 normal
convert -size 512x512 xc:'#0d2c54' \
  \( "$SRC_SVG" -resize 420x420 \) \
  -gravity center -composite \
  "$OUT_DIR/pwa-512.png"

# 512 maskable (extra padding)
convert -size 512x512 xc:'#0d2c54' \
  \( "$SRC_SVG" -resize 340x340 \) \
  -gravity center -composite \
  "$OUT_DIR/pwa-512-maskable.png"

# 192 normal
convert "$OUT_DIR/pwa-512.png" -resize 192x192 "$OUT_DIR/pwa-192.png"

# 192 maskable
convert "$OUT_DIR/pwa-512-maskable.png" -resize 192x192 "$OUT_DIR/pwa-192-maskable.png"

# iOS apple touch icon
convert "$OUT_DIR/pwa-512.png" -resize 180x180 "$OUT_DIR/apple-touch-icon.png"

echo "Generated:"
ls -la "$OUT_DIR/pwa-192.png" "$OUT_DIR/pwa-192-maskable.png" "$OUT_DIR/pwa-512.png" "$OUT_DIR/pwa-512-maskable.png" "$OUT_DIR/apple-touch-icon.png"
