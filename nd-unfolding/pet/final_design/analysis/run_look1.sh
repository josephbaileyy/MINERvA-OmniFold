#!/bin/bash
# Look-1 decision chain (after UNBLIND; local): evidence from the scored FB rows, the look-1 decision, and the
# provisional ranking that orders coverage (Amendment 3a item 5). Nothing here trains or reads raw FB arrays.
#   usage: bash run_look1.sh <dir with scored FB *.design_scores.json> <FB cost json> <out dir>
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); STUDY=$(dirname "$HERE")
SC=$1; COST=$2; OUT=$3; mkdir -p "$OUT"
DECL=$STUDY/freeze/EVIDENCE_DECLARATION-20260927.json
SEEDS=$STUDY/results/s3n
python3 "$HERE/build_evidence.py" --declaration "$DECL" --scores "$SC" \
  --seed-runs "H2S1T24K5=$SEEDS/S3P-H2S1T24K5-DEV*" "L128S1T24K4=$SEEDS/S3P-L128S1T24K5-DEV*" \
  --cost "$COST" --look 1 --out "$OUT/evidence_look1.json"
python3 "$HERE/decide.py" --evidence "$OUT/evidence_look1.json" --out "$OUT/decision_look1.json"
python3 "$HERE/build_evidence.py" --declaration "$DECL" --scores "$SC" \
  --seed-runs "H2S1T24K5=$SEEDS/S3P-H2S1T24K5-DEV*" "L128S1T24K4=$SEEDS/S3P-L128S1T24K5-DEV*" \
  --cost "$COST" --look 1 --provisional --out "$OUT/evidence_look1_provisional.json"
python3 "$HERE/decide.py" --evidence "$OUT/evidence_look1_provisional.json" --provisional \
  --out "$OUT/decision_look1_provisional.json"
python3 - "$OUT" <<'EOF'
import json, sys
o = sys.argv[1]
for f in ("decision_look1.json", "decision_look1_provisional.json"):
    d = json.load(open(f"{o}/{f}"))
    print(f, "->", d["ranking"].get("outcome"), {n: e["status"] for n, e in d["eligibility"].items()})
EOF
