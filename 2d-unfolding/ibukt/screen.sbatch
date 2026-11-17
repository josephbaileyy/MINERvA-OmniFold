#!/bin/bash
#SBATCH --job-name=ibukt-screen
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=64
#SBATCH --time=05:00:00
set -euo pipefail
# Submission and environment setup belong to the separately approved connect.
: "${IBUKT_DEPLOY:?}" "${IBUKT_STAGE:?}" "${IBUKT_PREPARE:?}" "${IBUKT_PRODUCTS:?}"
: "${IBUKT_PYTHON:?}" "${IBUKT_DEPLOY_SHA:?}"
"$IBUKT_PYTHON" -B - <<'CHECK_PATHS'
import os
from pathlib import Path

for key in ("IBUKT_DEPLOY", "IBUKT_STAGE", "IBUKT_PREPARE", "IBUKT_PRODUCTS"):
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
pids=()
for truth in nominal genie_mec nuwro bump tilt within_plus within_minus; do
  for trial in 0 1 2 3 4; do
    srun --exclusive --nodes=1 --ntasks=1 --cpus-per-task=64 \
      "$IBUKT_PYTHON" -B nd-unfolding/mnv_guarded_run.py \
      --expect-root "$IBUKT_DEPLOY" \
      --inventory "$IBUKT_PRODUCTS/$truth-$trial.imports.jsonl" \
      --label "ibukt-$truth-$trial" -- 2d-unfolding/ibukt/run_ibukt.py pair \
      --stage "$IBUKT_STAGE" --out "$IBUKT_PRODUCTS/$truth-$trial" \
      --bank "$IBUKT_PREPARE/bank.npz" --identity "$IBUKT_PREPARE/identity.json" \
      --truth "$truth" --trial "$trial" \
      >"$IBUKT_PRODUCTS/$truth-$trial.log" 2>&1 &
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
