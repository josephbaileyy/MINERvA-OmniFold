#!/bin/bash
# Track C iteration test: lgbm at 5 and 10 iters, same seed, only --iters varies.
# Isolates OmniFold iteration regularization as a source of the paper-cov chi^2
# tension. Run sequentially (one 128-thread job at a time) on the allocation.
set -eo pipefail
export PYTHONUNBUFFERED=1
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
source "${REPO}/setup_salloc_env.sh"
cd "${DOCS}"
for IT in 5 10; do
  echo "[iter-test] === lgbm ${IT} iters start: $(date -u '+%H:%M:%S UTC') ==="
  python unfold_2d_omnifold_unbinned.py \
    --omnifile runEventLoopOmniFold_MEFHC.root \
    --mcfile   baseline_flux/runEventLoopMC_MEFHC.root \
    --iters    "${IT}" \
    --estimator lgbm \
    --use-weights \
    --seed      1 \
    --out       "tension_iter/2d_xsec_lgbm_${IT}iter.root"
  echo "[iter-test] === lgbm ${IT} iters done: $(date -u '+%H:%M:%S UTC') ==="
done
echo "[iter-test] ALL DONE: $(date -u '+%H:%M:%S UTC')"
