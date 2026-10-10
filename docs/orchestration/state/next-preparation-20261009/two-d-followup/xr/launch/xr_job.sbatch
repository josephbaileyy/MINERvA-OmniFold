#!/bin/bash
# XR: one run, one attempt. Submitted only by xr_submit.sh, which sets every #SBATCH value from the
# frozen runs.json kind on the command line:  xr_job.sbatch ADMISSION RUN ATTEMPT
#
# Order: the allocation is checked against the frozen caps (exit 3 on QOS, CPUs, billing or time
# limit); the admission is re-verified (binding, clean HEAD, and the environment setup and every
# script it sources at their admitted digests; exit 3); the setup is sourced, and the wrapper runs
# under the OI-136 guard on the admitted checkout, where it refuses (exit 6, before any fit) an
# interpreter, ROOT or package version other than the frozen one. No `set -u` before sourcing:
# conda activation aborts under it. Both helper scripts run under the system /usr/bin/python3.
set -eo pipefail
ADM="$1"; RUN="$2"; ATT="$3"
[ -n "$ADM" ] && [ -n "$RUN" ] && [ -n "$ATT" ] || { echo "[xr-job] usage: ADMISSION RUN ATTEMPT" >&2; exit 2; }
PY=/usr/bin/python3
field() { "$PY" -c 'import json,sys
d=json.load(open(sys.argv[1]))
for k in sys.argv[2].split("."): d=d[k]
print(d)' "$ADM" "$1"; }
CHECKOUT=$(field checkout)
P="$CHECKOUT/docs/orchestration/state/next-preparation-20261009/two-d-followup/xr"
OUTROOT=$(field outroot)
SETUP=$(field setup.path)
echo "[xr-job] run=$RUN attempt=$ATT job=$SLURM_JOB_ID node=$(hostname) start=$(date -u +%FT%TZ)"
OMP=$("$PY" "$P/xr_admit.py" jobcheck --admission "$ADM" --run "$RUN") || { echo "[xr-job] REFUSED: allocation" >&2; exit 3; }
"$PY" "$P/xr_admit.py" verify --admission "$ADM" || { echo "[xr-job] REFUSED: admission" >&2; exit 3; }
source "$SETUP" >/dev/null 2>&1
export OMP_NUM_THREADS="$OMP" MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
cd "$CHECKOUT/2d-unfolding"
set +e
python "$CHECKOUT/nd-unfolding/mnv_guarded_run.py" --expect-root "$CHECKOUT" \
    --inventory "$OUTROOT/$RUN/a$ATT/inventory.jsonl" --label "XR-$RUN-a$ATT" -- \
    "$P/xr_run.py" --run "$RUN" --attempt "$ATT" --admission "$ADM" --require-provenance
rc=$?
echo "[xr-job] end=$(date -u +%FT%TZ) rc=$rc"
exit $rc
