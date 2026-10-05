#!/bin/bash
# Coverage and terminal decision chain (local; after each coverage group's UNBLIND amendment and scoring):
# coverage_spec.py -> coverage.py (C1-C4 from the development tilt; C5 from D4c up when its scores are given) ->
# build_evidence.py with the coverage file -> decide.py. With the D4c scores absent, C5 stays incomplete and the
# outcome cannot be SELECTED (decide.py: no selection while a decision-set member is pending).
#   usage: bash run_final.sh <look-1 scores dir> <FB cost json> <dev-tilt scores dir> <D4c scores dir | -> <out dir>
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); STUDY=$(dirname "$HERE")
SC=$1; COST=$2; DEVS=$3; D4CS=$4; OUT=$5; mkdir -p "$OUT"
CAND=H2S1T24K5; R=$STUDY/runs
DECL=$STUDY/freeze/EVIDENCE_DECLARATION-20260927.json
SEEDS=$STUDY/results/s3n
args=(--candidate "$CAND" --dev "$R/s5c_a5_H2S1T24.tsv" "$DEVS")
[[ "$D4CS" != - ]] && args+=(--d4c "$R/s5d_a5_H2S1T24.tsv" "$D4CS")
python3 "$HERE/coverage_spec.py" "${args[@]}" --out "$OUT/coverage_spec.json"
python3 "$HERE/coverage.py" --spec "$OUT/coverage_spec.json" --out "$OUT/coverage_$CAND.json"
python3 "$HERE/build_evidence.py" --declaration "$DECL" --scores "$SC" \
  --seed-runs "H2S1T24K5=$SEEDS/S3P-H2S1T24K5-DEV*" "L128S1T24K4=$SEEDS/S3P-L128S1T24K5-DEV*" \
  --cost "$COST" --coverage "$CAND=$OUT/coverage_$CAND.json" --look 1 --out "$OUT/evidence_final.json"
python3 "$HERE/decide.py" --evidence "$OUT/evidence_final.json" --out "$OUT/decision_final.json"
python3 - "$OUT" <<'EOF'
import json, sys
o = sys.argv[1]
d = json.load(open(f"{o}/decision_final.json"))
print("decision_final.json ->", d["ranking"].get("outcome"), {n: e["status"] for n, e in d["eligibility"].items()})
for n, e in d["eligibility"].items():
    print(" ", n, {r: v["verdict"] for r, v in e["verdicts"].items() if r.startswith("C")})
EOF
