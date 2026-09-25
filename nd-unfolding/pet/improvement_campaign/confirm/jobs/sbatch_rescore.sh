#!/bin/bash
# CPU job: re-score COMPLETE runs into a separate directory and compare with their scores.json.
# Written for review round 2 finding 4: before the scoring lock, two chains could score one run at
# once through the scorer's fixed scores.json.tmp. The scorer is deterministic, so an intact
# scores.json is reproduced exactly (the run path aside); any other difference is reported.
#   env: MINE (a clean checkout, at the commit that scored the runs) MINE_COMMIT MANIFEST OUT
#        RUNS (space-separated run names) DEST
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --time=00:20:00
#SBATCH --job-name=pv1-rescore
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${MANIFEST:?}" ; : "${OUT:?}" ; : "${RUNS:?}" ; : "${DEST:?}"
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]]
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
source "$MINE/nd-unfolding/pet/improvement_campaign/confirm/jobs/confirm_lib.sh"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
module load tensorflow/2.15.0
mkdir -p "$DEST"
for name in $RUNS; do
  ROW=$(manifest_rows | awk -F'\t' -v n="$name" '$1 == n')
  [[ -n "$ROW" ]] || { echo "$name: not in $MANIFEST" >> "$DEST/rescore.txt"; continue; }
  IFS=$'\t' read -r _ cfg hash selection distortion ref extra <<< "$ROW"
  ARGS=()
  if [[ "$selection" != historical ]]; then
    T=$(target_path "${selection%%:*}" "$distortion"); [[ -s "$T" ]] && ARGS+=(--population-target "$T")
  fi
  [[ "$ref" != "-" ]] && ARGS+=(--reference-run "$ref")
  python "$GUARD" --expect-root "$MINE" --inventory "$DEST/guard-$name.json" --label "V1-rescore-$name" -- \
    "$V/score_replicate.py" --run "$OUT/$name" --output "$DEST/$name.scores.json" "${ARGS[@]}" \
    > "$DEST/$name.log" 2>&1 || { echo "$name: rescore exit $?" >> "$DEST/rescore.txt"; continue; }
  python - "$OUT/$name/scores.json" "$DEST/$name.scores.json" "$name" >> "$DEST/rescore.txt" <<'EOF'
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
# `seconds` is wall time; everything else (provenance included) is compared, named to the subkey
diff = sorted(k for k in set(a) | set(b) - {"seconds"} if a.get(k) != b.get(k) and k != "seconds")
sub = [f"provenance.{k}" for k in sorted(set(a.get("provenance", {})) | set(b.get("provenance", {})))
       if a.get("provenance", {}).get(k) != b.get("provenance", {}).get(k)]
print(f"{sys.argv[3]}: " + ("IDENTICAL (except wall time)" if not diff
                           else "DIFFERS in " + ", ".join([d for d in diff if d != "provenance"] + sub)))
EOF
done
