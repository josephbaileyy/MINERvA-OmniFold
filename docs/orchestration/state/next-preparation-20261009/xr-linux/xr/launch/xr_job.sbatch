#!/bin/bash
# XR: one run, one attempt. Submitted only by xr_submit.sh, which sets every #SBATCH value from the
# frozen runs.json kind on the command line:  xr_job.sbatch ADMISSION RUN ATTEMPT
#
# Order: the allocation is checked against the frozen caps (exit 3 on QOS, CPUs, AllocTRES billing
# or time limit; the raw scontrol line is kept as <attempt>/scontrol-job.txt); the admission is
# re-verified (binding, clean HEAD, and the environment setup and every script it sources at their
# admitted digests; exit 3); the setup is sourced, and the wrapper runs under the OI-136 guard on the
# admitted checkout. For the preflight, two controls run first and are read by the wrapper: this
# allocation checked against another kind's caps (must refuse), and a guarded child that reaches
# ldconfig through threadpoolctl (must be refused by the guard). No `set -u` before sourcing: conda
# activation aborts under it. Both helper scripts run under the system /usr/bin/python3.
set -eo pipefail
ADM="$1"; RUN="$2"; ATT="$3"
[ -n "$ADM" ] && [ -n "$RUN" ] && [ -n "$ATT" ] || { echo "[xr-job] usage: ADMISSION RUN ATTEMPT" >&2; exit 2; }
PY=/usr/bin/python3
field() { "$PY" -c 'import json,sys
d=json.load(open(sys.argv[1]))
for k in sys.argv[2].split("."): d=d[k]
print(d)' "$ADM" "$1"; }
CHECKOUT=$(field checkout)
P="$CHECKOUT/docs/orchestration/state/next-preparation-20261009/xr-linux/xr"
OUTROOT=$(field outroot)
SETUP=$(field setup.path)
KIND=$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["runs"][sys.argv[2]]["kind"])' "$P/manifest/runs.json" "$RUN")
DIR="$OUTROOT/$RUN/a$ATT"
echo "[xr-job] run=$RUN kind=$KIND attempt=$ATT job=$SLURM_JOB_ID node=$(hostname) start=$(date -u +%FT%TZ)"
OMP=$("$PY" "$P/xr_admit.py" jobcheck --admission "$ADM" --run "$RUN" --record "$DIR/scontrol-job.txt") \
    || { echo "[xr-job] REFUSED: allocation" >&2; exit 3; }
"$PY" "$P/xr_admit.py" verify --admission "$ADM" || { echo "[xr-job] REFUSED: admission" >&2; exit 3; }
source "$SETUP" >/dev/null 2>&1
export OMP_NUM_THREADS="$OMP" MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
# joblib's count must come from the allocation (xr_run.py thread_plan); off Linux (the tests only) the
# variable stands in for the affinity, which macOS lacks.
if [ "$(uname -s)" = Linux ]; then unset LOKY_MAX_CPU_COUNT; fi
cd "$CHECKOUT/2d-unfolding"
set +e
if [ "$KIND" = preflight ]; then
    mkdir "$DIR/controls" || exit 3
    "$PY" "$P/xr_admit.py" jobcheck --admission "$ADM" --run L0 \
        > "$DIR/controls/jobcheck_other_kind.out" 2> "$DIR/controls/jobcheck_other_kind.err"
    echo $? > "$DIR/controls/jobcheck_other_kind.rc"
    python "$CHECKOUT/nd-unfolding/mnv_guarded_run.py" --expect-root "$CHECKOUT" \
        --inventory "$DIR/controls/inventory-guard-control.jsonl" --label "XR-$RUN-a$ATT-guard-control" -- \
        "$P/xr_guard_control.py" > "$DIR/controls/guard_refuses_launch.out" 2> "$DIR/controls/guard_refuses_launch.err"
    echo $? > "$DIR/controls/guard_refuses_launch.rc"
    echo "[xr-job] controls: jobcheck_other_kind rc=$(cat "$DIR/controls/jobcheck_other_kind.rc") guard_refuses_launch rc=$(cat "$DIR/controls/guard_refuses_launch.rc")"
fi
python "$CHECKOUT/nd-unfolding/mnv_guarded_run.py" --expect-root "$CHECKOUT" \
    --inventory "$DIR/inventory.jsonl" --label "XR-$RUN-a$ATT" -- \
    "$P/xr_run.py" --run "$RUN" --attempt "$ATT" --admission "$ADM" --require-provenance
rc=$?
echo "[xr-job] end=$(date -u +%FT%TZ) rc=$rc"
exit $rc
