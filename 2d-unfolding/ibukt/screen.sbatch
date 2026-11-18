#!/bin/bash
#SBATCH --job-name=ibukt-screen
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=64
#SBATCH --time=05:15:00
#SBATCH --no-requeue
set -euo pipefail
SECONDS=0
# Submission and environment setup belong to the separately approved connect.
: "${IBUKT_DEPLOY:?}" "${IBUKT_STAGE:?}" "${IBUKT_PREPARE:?}" "${IBUKT_PRODUCTS:?}"
: "${IBUKT_PYTHON:?}" "${IBUKT_DEPLOY_SHA:?}" "${IBUKT_ADMISSION:?}"
"$IBUKT_PYTHON" -B - <<'CHECK_PATHS'
import os
from pathlib import Path

for key in ("IBUKT_DEPLOY", "IBUKT_STAGE", "IBUKT_PREPARE", "IBUKT_PRODUCTS", "IBUKT_ADMISSION"):
    if not Path(os.environ[key]).resolve().is_relative_to(Path("/pscratch")):
        raise SystemExit(f"{key} must resolve under /pscratch")
CHECK_PATHS
cd "$IBUKT_DEPLOY"
[[ "$(git rev-parse HEAD)" == "$IBUKT_DEPLOY_SHA" ]]
[[ -z "$(git status --porcelain)" ]]
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
[[ ! -e "$IBUKT_PRODUCTS" ]]
mkdir "$IBUKT_PRODUCTS"

"$IBUKT_PYTHON" -B nd-unfolding/mnv_guarded_run.py \
  --expect-root "$IBUKT_DEPLOY" \
  --inventory "$IBUKT_PRODUCTS/admission.imports.jsonl" \
  --label ibukt-admission -- 2d-unfolding/ibukt/jobs.py screen-admission \
  --admission "$IBUKT_ADMISSION" >"$IBUKT_PRODUCTS/admission.json"

run_pair() {
  local label="$1" truth="$2" trial="$3"
  shift 3
  srun -n1 -c 64 --exact --mem=121920M --mem-bind=local \
    "$IBUKT_PYTHON" -B nd-unfolding/mnv_guarded_run.py \
    --expect-root "$IBUKT_DEPLOY" \
    --inventory "$IBUKT_PRODUCTS/$label.imports.jsonl" \
    --label "ibukt-$label" -- 2d-unfolding/ibukt/run_ibukt.py pair \
    --stage "$IBUKT_STAGE" --out "$IBUKT_PRODUCTS/$label" \
    --bank "$IBUKT_PREPARE/bank.npz" --identity "$IBUKT_PREPARE/identity.json" \
    --truth "$truth" --trial "$trial" "$@" \
    >"$IBUKT_PRODUCTS/$label.log" 2>&1 < /dev/null
}

# Both controls finish before the remaining 34 fits can start.
run_pair nominal-control nominal 0 --noise-free
control="$IBUKT_PRODUCTS/nominal-control/pair.json"
preflight_start=$SECONDS
run_pair nominal-0 nominal 0 --control "$control"
measured_seconds=$((SECONDS - preflight_start + 1))
"$IBUKT_PYTHON" -B nd-unfolding/mnv_guarded_run.py \
  --expect-root "$IBUKT_DEPLOY" \
  --inventory "$IBUKT_PRODUCTS/forecast.imports.jsonl" \
  --label ibukt-forecast -- 2d-unfolding/ibukt/jobs.py forecast \
  --admission "$IBUKT_ADMISSION" --measured-seconds "$measured_seconds" \
  --elapsed-seconds "$((SECONDS + 1))" >"$IBUKT_PRODUCTS/forecast.json"

pids=()
for truth in nominal genie_mec nuwro bump tilt within_plus within_minus; do
  for trial in 0 1 2 3 4; do
    [[ "$truth-$trial" != nominal-0 ]] || continue
    run_pair "$truth-$trial" "$truth" "$trial" --control "$control" &
    pids+=("$!")
    if [[ ${#pids[@]} -eq 2 ]]; then
      failed=0
      for pid in "${pids[@]}"; do wait "$pid" || failed=1; done
      [[ "$failed" == 0 ]] || exit 4
      pids=()
    fi
  done
done
for pid in "${pids[@]}"; do wait "$pid"; done
