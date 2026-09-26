#!/bin/bash
# Harvest committed evidence for one study stage from Perlmutter: per COMPLETE run directory its
# receipt.json, scores.json (predecessor scorer, run in the job), run_identity.json and the post-hoc
# diagnostics JSON (study posthoc/<stage>/). Incomplete runs are listed, not copied.
#   usage: bash harvest.sh <stage> [<stage> ...]     (run from this directory; needs ssh saul.nersc.gov)
set -euo pipefail
B=/pscratch/sd/j/josephrb/pet-final-design-20260925
HERE=$(cd "$(dirname "$0")" && pwd)
PROTO="$HERE/../PROTOCOL-20260925.md"
for S in "$@"; do
  # blinded until an UNBLIND amendment (Amendments 2, 2c): receipts carry FB-derived statistics
  if [[ "$S" =~ ^s[45] ]] && ! grep -qE '^### Amendment [^ ]+ .*\bUNBLIND\b' "$PROTO"; then
    echo "refusing to harvest final-bank stage $S before an UNBLIND amendment" >&2; exit 2
  fi
  mkdir -p "$HERE/$S"
  ssh -o BatchMode=yes saul.nersc.gov "cd $B/$S && for d in */; do d=\${d%/}; [ -f \$d/status.txt ] || continue; \
    if [ \"\$(cat \$d/status.txt)\" = COMPLETE ]; then echo C \$d; else echo I \$d; fi; done" > "$HERE/$S/.status"
  grep '^I ' "$HERE/$S/.status" | cut -c3- > "$HERE/$S/INCOMPLETE.txt" || true
  for d in $(grep '^C ' "$HERE/$S/.status" | cut -c3-); do
    for f in receipt.json scores.json run_identity.json; do
      rsync -a "saul.nersc.gov:$B/$S/$d/$f" "$HERE/$S/$d.$f" 2>/dev/null || echo "missing $S/$d/$f"
    done
    rsync -a "saul.nersc.gov:$B/posthoc/$S/$d.posthoc.json" "$HERE/$S/" 2>/dev/null || echo "no posthoc $S/$d"
  done
  rm -f "$HERE/$S/.status"
  echo "$S: $(ls "$HERE/$S"/*.receipt.json 2>/dev/null | wc -l) runs harvested; $(wc -l < "$HERE/$S/INCOMPLETE.txt") incomplete"
done
