#!/usr/bin/env bash
set -eo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
node "$here/export_frames.js"

while IFS= read -r svg; do
  convert -density 120 -background '#fffefa' "$svg" "${svg%.svg}.png"
done < <(find "$here/exports" -name 'build-*.svg' -type f | sort)

while IFS= read -r dir; do
  mapfile -t frames < <(find "$dir" -maxdepth 1 -name 'build-*.png' -type f | sort)
  if ((${#frames[@]})); then
    convert -delay 150 -loop 0 "${frames[@]}" "$dir/sequence.gif"
  fi
done < <(find "$here/exports" -mindepth 1 -maxdepth 1 -type d | sort)

echo "PNG frames and looping GIFs are in $here/exports"
