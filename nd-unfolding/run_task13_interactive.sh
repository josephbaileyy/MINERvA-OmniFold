#!/bin/bash
# Task 13 chain via the shared interactive allocation (sbatch queue was backlogged).
# merge 12 5D _universes_full omnifiles -> (E_avail,W) frozen-reweighter covariance.
# Orchestrated INSIDE the allocation (alloc_run -> srun --overlap); monitor by the log file.
set -uo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
cd "$REPO"
export ALLOC_CPUS=64

OUT="runEventLoopOmniFold_5D_MEFHC_universes_full.root"
echo "[t13] === MERGE start $(date -u '+%F %T UTC') ==="
if [[ ! -s "nd-unfolding/${OUT}" ]]; then
  ./alloc_run.sh "cd nd-unfolding && python3 ../2d-unfolding/uq/hadd_universes_full.py ${OUT} runEventLoopOmniFold_5D_1?_universes_full.root"
else
  echo "[t13] merged file already present, skipping merge"
fi
if [[ ! -s "nd-unfolding/${OUT}" ]]; then
  echo "[t13] FAIL: merge did not produce ${OUT}" >&2; exit 2
fi
echo "[t13] === MERGE done $(date -u '+%F %T UTC'); size: ==="
ls -lh "nd-unfolding/${OUT}"

echo "[t13] === COV start $(date -u '+%F %T UTC') ==="
./alloc_run.sh "cd nd-unfolding && OMP_NUM_THREADS=64 python3 eavailW_covariance.py --omnifile ${OUT} --out products/5d/eavailW_covariance.root"
echo "[t13] === COV done $(date -u '+%F %T UTC') ==="
ls -lh "nd-unfolding/products/5d/eavailW_covariance.root"
echo "[t13] === ALL DONE $(date -u '+%F %T UTC') ==="
