#!/bin/bash
# RE-2 J0 readout on a login node, pinned, after both J0 jobs end:  re2_j0_readout.sh <deploy> <declared sha> <J0a id> <J0b id>
# Writes $O/readout/{k1.json,steps.psv,j0_ledger.tsv,units.json}; nothing else. Refuses until both jobs have ended. The verdicts are re2_k1.py's and re2_units.py's.
set -eo pipefail
C=$(cd "$1" && pwd); RE2_SHA=$2; JA=$3; JB=$4
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2_env.sh"
[ "$(git -C "$C" rev-parse HEAD)" = "$RE2_SHA" ] && [ -z "$(git -C "$C" status --porcelain)" ] || { echo "deploy not clean at $RE2_SHA"; exit 2; }
source "$A/setup_salloc_env.sh" >/dev/null 2>&1
set -u
export TMPDIR=$B/tmp
for j in "$JA" "$JB"; do
    st=$(sacct -X -n -P -j "$j" -o State | head -1)
    case "$st" in COMPLETED|FAILED|TIMEOUT|CANCELLED*|OUT_OF_MEMORY|NODE_FAIL|DEADLINE|PREEMPTED|BOOT_FAIL) ;;
        *) echo "job $j is not in a terminal state ($st)"; exit 2 ;; esac
done
R=$O/readout; mkdir -p "$R"
for f in k1.json steps.psv j0_ledger.tsv units.json; do [ ! -e "$R/$f" ] || { echo "$R/$f exists"; exit 3; }; done
EU=$A/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root
g() { local label=$1; shift; taskset -c 8-11 python "$C/nd-unfolding/mnv_guarded_run.py" --expect-root "$C" --label "$label" \
        --inventory "$O/inventory/$label.jsonl" -- "$@"; }
g re2_k1 "$C/2d-unfolding/re2/re2_k1.py" --runs "$RUNS" --checks "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/j0_checks.tsv" \
    --out-dir "$O/out" --eu "$EU" --expect-eu-sha256 4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c \
    --result "$R/k1.json" > "$R/k1.log" 2>&1 || echo "[re2] K1 readout rc=$? (a FAIL verdict exits 1)"
sacct -j "$JA,$JB" -n -P -o JobID,JobName,ElapsedRaw,AllocCPUS,State > "$R/steps.psv"
bash "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2_ledger.sh" "$JA" "$JB" > "$R/j0_ledger.tsv"
g re2_units "$C/2d-unfolding/re2/re2_units.py" --runs "$RUNS" --steps "$R/steps.psv" --ledger "$R/j0_ledger.tsv"     --result "$R/units.json" > "$R/units.log" 2>&1
tail -1 "$R/k1.log"; tail -1 "$R/units.log"
(cd "$R" && sha256sum k1.json steps.psv j0_ledger.tsv units.json)
