#!/bin/bash
# RE-2 part B readout on a login node, pinned, after every submitted part-B job has ended:
#     bash re2b_readout.sh <deploy> <declared sha>
# Writes $O/readout/{steps.psv,ledger.tsv,k1_core.json,k1_j7.json} (k1_j7.json only if J7 was submitted); nothing
# else. Refuses while any attempt is not in a terminal state, and refuses to overwrite a readout. The verdicts are
# re2_k1.py's, one per set: the core (J1-J4, J6, J8) and the gated diagnostic J7 (RE2-DECLARATION-B.md §5.2).
set -eo pipefail
C=$(cd "$1" && pwd); RE2_SHA=$2
L=$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch
[ "$(git -C "$C" rev-parse HEAD)" = "$RE2_SHA" ] && [ -z "$(git -C "$C" status --porcelain)" ] \
    || { echo "deploy not clean at $RE2_SHA"; exit 2; }
source "$L/re2b_env.sh"
source "$A/setup_salloc_env.sh" >/dev/null 2>&1
set -u
export TMPDIR=$B/tmp
R=$O/readout; mkdir -p "$R"
for f in steps.psv ledger.tsv k1_core.json k1_j7.json; do [ ! -e "$R/$f" ] || { echo "$R/$f exists"; exit 3; }; done
names=$(awk -F'\t' 'NR > 1 {printf "%sre2b-%s", (n++ ? "," : ""), $1}' "$JOBS")
# -S is local time (PDT), as in re2b_submit.sh
rows=$(sacct -X -n -P -S 2026-10-23 --name="$names" -o JobID,JobName,State)
[ -n "$rows" ] || { echo "no part-B job in sacct"; exit 2; }
while IFS='|' read -r id name st; do
    case "${st%% *}" in COMPLETED|FAILED|TIMEOUT|CANCELLED|OUT_OF_MEMORY|NODE_FAIL|DEADLINE|PREEMPTED|BOOT_FAIL) ;;
        *) echo "job $id ($name) is not in a terminal state ($st)"; exit 2 ;; esac
done <<< "$rows"
ids=$(cut -d'|' -f1 <<< "$rows" | paste -sd, -)
sacct -j "$ids" -n -P -o JobID,JobName,ElapsedRaw,AllocCPUS,State > "$R/steps.psv"
bash "$L/re2_ledger.sh" $(tr ',' ' ' <<< "$ids") > "$R/ledger.tsv"
EU=$A/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root
k1() {  # k1 <classes> <result>
    taskset -c 8-11 python "$C/nd-unfolding/mnv_guarded_run.py" --expect-root "$C" --label "re2b_k1_$2" \
        --inventory "$O/inventory/re2b_k1_$2.jsonl" -- "$C/2d-unfolding/re2/re2_k1.py" --runs "$RUNS" \
        --checks "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_checks.tsv" \
        --out-dir "$O/out" --eu "$EU" --expect-eu-sha256 4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c \
        --sums-glob 'SHA256SUMS.J[1-8]*' --classes "$1" --sums-cover-runs --check-argv --result "$R/k1_$2.json" \
        > "$R/k1_$2.log" 2>&1 || echo "[re2b] k1 $2 rc=$? (a FAIL verdict exits 1)"
    tail -1 "$R/k1_$2.log"
}
k1 J1,J2,J3,J4,J6,J8 core
if grep -q '|re2b-J7|' <<< "$rows"; then k1 J7 j7; else echo "[re2b] J7 not submitted"; fi
(cd "$R" && sha256sum steps.psv ledger.tsv k1_*.json)
