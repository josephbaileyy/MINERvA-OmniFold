#!/bin/bash
# Copy every scored run's scores.json and receipt.json of a stage from Perlmutter into
# results/<stage>/<run>.{scores,receipt}.json (then run analyze_confirm.py).
#   harvest.sh <stage> [<remote stage dir>]
set -euo pipefail
ST=$1; R=${2:-/pscratch/sd/j/josephrb/pet-improvement-20260922/confirm/$ST}
HERE=$(cd "$(dirname "$0")" && pwd); L="$HERE/results/$ST"; mkdir -p "$L"
TMP=$(mktemp -d)
ssh -o ConnectTimeout=20 perlmutter.nersc.gov "cd $R && tar cf - \$(ls -d */scores.json */receipt.json */run_identity.json submissions.txt 2>/dev/null)" | tar xf - -C "$TMP"
for d in "$TMP"/*/; do
  n=$(basename "$d"); [[ -f "$d/scores.json" ]] || continue
  cp "$d/scores.json" "$L/$n.scores.json"; cp "$d/receipt.json" "$L/$n.receipt.json"
done
[[ -f "$TMP/submissions.txt" ]] && cp "$TMP/submissions.txt" "$L/submissions.txt"
rm -rf "$TMP"; ls "$L" | grep -c scores.json
