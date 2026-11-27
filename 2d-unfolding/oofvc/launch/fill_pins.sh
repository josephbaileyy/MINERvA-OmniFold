#!/bin/bash
# OOFVC: write launch/bound/ with every pin computed by command (EVW5D's fill_pins.sh form).
#   bash fill_pins.sh <tool commit>
# The tool commit must be an ancestor of HEAD (or HEAD) and carry, byte for byte, this checkout's 2d-unfolding/oofvc/
# (the remote scripts run from a clone at that commit). Order: the tool commit into the remote scripts, then their
# digests into the launcher. Refuses if any placeholder is left.
set -euo pipefail
TOOLC=${1:?tool commit}
HERE=$(cd "$(dirname "$0")" && pwd)
TOP=$(git -C "$HERE" rev-parse --show-toplevel)
B="$HERE/bound"
[ ! -e "$B" ] || { echo "STOP: $B exists"; exit 2; }
full=$(git -C "$TOP" rev-parse --verify "$TOOLC^{commit}")
git -C "$TOP" merge-base --is-ancestor "$full" HEAD || { echo "STOP: $full is not an ancestor of HEAD"; exit 2; }
for f in $(git -C "$TOP" ls-tree -r --name-only "$full" -- 2d-unfolding/oofvc); do
  case "$f" in */launch/bound/*) continue;; esac
  [ "$(git -C "$TOP" show "$full:$f" | shasum -a 256 | cut -d' ' -f1)" = "$(shasum -a 256 "$TOP/$f" | cut -d' ' -f1)" ] \
    || { echo "STOP: $f differs from the tool commit's"; exit 2; }
done
mkdir "$B"
for s in oofvc_dump.sh oofvc_units.sh oofvc_post.sh; do
  sed -e "s/__TOOL_COMMIT__/$full/" "$HERE/$s" > "$B/$s"
done
D=$(shasum -a 256 "$B/oofvc_dump.sh" | cut -d' ' -f1)
U=$(shasum -a 256 "$B/oofvc_units.sh" | cut -d' ' -f1)
P=$(shasum -a 256 "$B/oofvc_post.sh" | cut -d' ' -f1)
sed -e "s/__DUMP_SHA256__/$D/g" -e "s/__UNITS_SHA256__/$U/" -e "s/__POST_SHA256__/$P/" "$HERE/oofvc_launch.sh" > "$B/oofvc_launch.sh"
if grep -n '__[A-Z0-9_]*__' "$B"/*.sh; then echo "STOP: a placeholder is left"; exit 3; fi
for f in "$B"/*.sh; do bash -n "$f"; done
L=$(shasum -a 256 "$B/oofvc_launch.sh" | cut -d' ' -f1)
cat <<PINS | tee "$B/PINS.txt"
tool commit      $full
oofvc_dump.sh    $D
oofvc_units.sh   $U
oofvc_post.sh    $P
oofvc_launch.sh  $L
PINS
