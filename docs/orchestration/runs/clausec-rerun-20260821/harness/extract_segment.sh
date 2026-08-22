#!/bin/bash
# Extract the launcher's adopt segment BY CONTENT, never by retyping it, and never by a line number.
#
# WHY BY CONTENT. The adopt block has moved three times (the previous clause (c) run recorded
# 320 -> 332) and the two adopt calls' line numbers have moved twice more. A line-anchored extraction
# would silently cut the wrong bytes after the next edit.
#
# WHY THE `set` LINE IS RE-INSERTED. `set -eo pipefail` is at the TOP of the launcher, ABOVE the
# extraction point. The previous run's first extraction lost it, and the fragment then EXITED 0 while
# both wrapper invocations had REFUSED -- a harness that reports the launcher swallowing a refusal the
# launcher does not swallow. It is taken from the launcher by content, so it is the launcher's own line.
set -euo pipefail
LAUNCHER="$1"
OUT="$2"

SETLINE="$(grep -m1 -n '^set -eo pipefail' "$LAUNCHER" | cut -d: -f1)"
START="$(grep -m1 -n 'adopt (mean-centered)' "$LAUNCHER" | cut -d: -f1)"
if [[ -z "$SETLINE" || -z "$START" ]]; then
  echo "[FAIL] could not locate the set line ($SETLINE) or the adopt anchor ($START) in $LAUNCHER" >&2
  exit 1
fi

{
  echo '#!/bin/bash'
  echo "# EXTRACTED BY CONTENT from $(basename "$LAUNCHER"); set line :$SETLINE, adopt anchor :$START"
  sed -n "${SETLINE}p" "$LAUNCHER"
  sed -n "${START},\$p" "$LAUNCHER"
} > "$OUT"
chmod +x "$OUT"

echo "[segment] set line   :$SETLINE  -> $(sed -n "${SETLINE}p" "$LAUNCHER")"
echo "[segment] adopt from :$START to EOF"
echo "[segment] sha256 $(sha256sum "$OUT" | cut -d' ' -f1)  $OUT"
echo "[segment] the two adopt invocations it carries:"
grep -n 'mii_adopt_unified_5d_stamped.py' "$OUT" | sed 's/^/[segment]   /'
