#!/bin/bash
# The cheap tier's submission lines (state/measurement-paper/5d-community-20261024/FD-CT-3B-DECLARATION.md section 2),
# so the account, QOS, constraint, time limit and arguments of every cheap-tier job are committed, not typed.
#
#   submit_fd_ct.sh 3b <deploy> <pin> <B>   one node, eight lanes of 3b-steps.tsv (13 mismatch closures)
#   submit_fd_ct.sh 5b-inputs <deploy> <pin> <B>    only after the precheck PASSed: stages the period flux on the login
#                                                   node, then one node, four lanes of 5b-inputs-steps.tsv (merges,
#                                                   dumps, checks, ALL unfold)
#   submit_fd_ct.sh 5b-periods <deploy> <pin> <B>   only after the pooled control PASSed: one node, eight lanes of
#                                                   5b-periods-steps.tsv (33 period unfolds)
#
# Every job: account m3246, QOS regular (never premium), constraint cpu, one exclusive node, --no-requeue, no GPU.
set -eo pipefail
STAGE="${1:?stage}"; D="${2:?deploy}"; PIN="${3:?pin}"; B="${4:?B}"
REL=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/3b
COMMON=(--account=m3246 --qos=regular --constraint=cpu --nodes=1 --exclusive --no-requeue
        --output="$B/logs/%x_%j.out")
case "$STAGE" in
  3b)
    # every refusal comes before anything is created; there is no resume: a failed or partial job is a STOP, and a
    # rerun needs the director and a new B in recommitted tables
    TABLE="$D/$REL/tasks-3b.tsv"; STEPS="$D/$REL/3b-steps.tsv"
    [ -f "$TABLE" ] && [ -f "$STEPS" ] || { echo "refusing: $TABLE or $STEPS is missing" >&2; exit 2; }
    [ "$(git -C "$D" rev-parse HEAD)" = "$PIN" ] || { echo "refusing: $D is not at $PIN" >&2; exit 2; }
    [ ! -e "$B/closures" ] && [ ! -e "$B/lanes" ] || { echo "refusing: $B/closures or $B/lanes exists" >&2; exit 2; }
    n=$(grep -v '^#' "$STEPS" | grep -c . || true)
    m=$(grep -v '^#' "$STEPS" | grep -c -F -- "--out	$B/closures/closure_" || true)
    [ "$n" -eq 13 ] && [ "$m" -eq 13 ] || { echo "refusing: $n steps, $m of them writing under $B/closures/" >&2; exit 2; }
    mkdir -p "$B/logs" "$B/closures"
    sbatch "${COMMON[@]}" --time=00:45:00 --job-name=fd_ct_3b \
      "$D/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh" \
      "$D" "$PIN" "$TABLE" "$B/lanes" 32 56G 0 7 none ;;
  5b-inputs|5b-periods)
    # FD-CT-5B-DECLARATION.md section 2. As 3b: every refusal before anything is created, and no resume
    REL5=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b
    [ "$(git -C "$D" rev-parse HEAD)" = "$PIN" ] || { echo "refusing: $D is not at $PIN" >&2; exit 2; }
    # the login-node interpreter of the declaration's section 2; FD_CT_PY replaces it only in the tests' stub
    if [ -n "${FD_CT_PY:-}" ]; then PY=("$FD_CT_PY"); else
      PY=(env -u PYTHONPATH /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 -I -B); fi
    if [ "$STAGE" = 5b-inputs ]; then
      # MP-1's geometry for its dumps and unfolds (32 CPUs; peaks 21.0 and 17.8 GB), so the ALL unfold runs as
      # mp1s1_zero's did (review M3) and four lanes fit the node's allocation (M4)
      TABLE="$D/$REL5/tasks-5b-inputs.tsv"; STEPS="$D/$REL5/5b-inputs-steps.tsv"; N=17; LAST=3; CPT=32; MEM=56G
      TIME=01:00:00; JOB=fd_ct_5b_inputs; LANES="$B/lanes-inputs"; MAKE=(dumps truth inputs)
      for d in flux merged dumps truth inputs unf lanes-inputs; do
        [ ! -e "$B/$d" ] || { echo "refusing: $B/$d exists" >&2; exit 2; }
      done
    else
      TABLE="$D/$REL5/tasks-5b-periods.tsv"; STEPS="$D/$REL5/5b-periods-steps.tsv"; N=33; LAST=7; CPT=32; MEM=56G
      TIME=01:30:00; JOB=fd_ct_5b_periods; LANES="$B/lanes-periods"; MAKE=()
      for d in unf/PA unf/PB unf/PC lanes-periods; do
        [ ! -e "$B/$d" ] || { echo "refusing: $B/$d exists" >&2; exit 2; }
      done
    fi
    [ -f "$TABLE" ] && [ -f "$STEPS" ] || { echo "refusing: $TABLE or $STEPS is missing" >&2; exit 2; }
    n=$(grep -v '^#' "$STEPS" | grep -c . || true)
    m=$(grep -v '^#' "$STEPS" | grep -c -F -- "	$B/" || true)
    [ "$n" -eq "$N" ] && [ "$m" -eq "$N" ] || { echo "refusing: $n steps, $m of them writing under $B/" >&2; exit 2; }
    # job A only after this deploy's precheck PASSed, job B only after its control PASSed (review M5)
    "${PY[@]}" "$D/nd-unfolding/fd_ct_periods.py" gate --stage "${STAGE#5b-}" --b "$B" > "$B/control/gate-${STAGE}.out" 2>&1 \
      || { echo "refusing: the gate did not pass (see $B/control/gate-${STAGE}.out)" >&2; exit 2; }
    mkdir -p "$B/logs"
    for d in "${MAKE[@]}"; do mkdir "$B/$d"; done   # the steps' own output folders (review H1)
    if [ "$STAGE" = 5b-inputs ]; then
      "${PY[@]}" "$D/nd-unfolding/fd_ct_period_inputs.py" stage-flux --out-dir "$B/flux" > "$B/logs/stage-flux.out" 2>&1 \
        || { echo "refusing: the flux staging failed (see $B/logs/stage-flux.out)" >&2; exit 2; }
    fi
    sbatch "${COMMON[@]}" --time="$TIME" --job-name="$JOB" \
      "$D/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh" \
      "$D" "$PIN" "$TABLE" "$LANES" "$CPT" "$MEM" 0 "$LAST" none ;;
  *)
    echo "refusing: unknown stage $STAGE" >&2; exit 2 ;;
esac
