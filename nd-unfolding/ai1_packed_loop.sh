#!/bin/bash
# AI1 estimator-only scan on a single interactive GPU node (2026-07-14): gpu_shared
# was saturated (priority-competitive AI1 never won a slot), PET idle -> run the 12
# replicas here. Fixed data+MC draw (--fixed-data-seed 0), estimator seed = replica id.
# CONC=6 (LightGBM over-spawns; matches boot5d). skip-if-exists shares the 2 already
# done. HOME/ROOT fix inline; NO set -u (breaks conda activate).
set -o pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
source "$REPO/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=12 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
       NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
cd "$REPO/nd-unfolding"; mkdir -p boot_nd_5d_ai1
CONC=6
echo "[ai1-i] start $(date -u +%T) on $(hostname); done=$(ls boot_nd_5d_ai1/res_ai1_*.npz 2>/dev/null|wc -l)/12"
for s in $(seq 1 12); do
  out="boot_nd_5d_ai1/res_ai1_${s}.npz"
  [[ -s "$out" ]] && continue
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 10; done
  python3 bootstrap_nd.py --npz of_inputs_5d.npz --seed ${s} --fixed-data-seed 0 --iters 5 \
    --out "$out" > boot_nd_5d_ai1/iai1_${s}.log 2>&1 &
done
wait
echo "[ai1-i] done $(date -u +%T); done=$(ls boot_nd_5d_ai1/res_ai1_*.npz 2>/dev/null|wc -l)/12"
