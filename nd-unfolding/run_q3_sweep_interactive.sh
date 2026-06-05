#!/bin/bash
# Runs INSIDE an salloc: q3 vertical bank-unfolds, max ~10 concurrent srun --overlap.
# sweep_bank --run has skip-if-exists, so it only does the remaining universes and is
# safe to re-run across salloc windows.
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
echo "[q3-inside] SLURM_JOB_ID=$SLURM_JOB_ID node=$(hostname) start $(date -u +%H:%M:%S)"
MAX=10
while read U; do
  [ -z "$U" ] && continue
  TAG="${U/:/_}"
  [ -s "${REPO}/nd-unfolding/uq_4d/universe_sweep/4d_xsec_MEFHC_5iter_lgbm_uni_full_${TAG}.root" ] && continue
  while [ "$(jobs -rp | wc -l)" -ge "$MAX" ]; do sleep 5; done
  srun --overlap --exact -n1 -c12 bash -lc \
    "source '${REPO}/setup_salloc_env.sh' >/dev/null 2>&1; export OMP_NUM_THREADS=12; cd '${REPO}/nd-unfolding' && python3 sweep_bank.py --run --universe '$U' --bankdir bank_sweep --iters 5 >/dev/null 2>&1 && echo '[done] $U'" &
done < "${REPO}/nd-unfolding/uq_4d/vertical_universes.txt"
wait
echo "[q3-inside] window done $(date -u +%H:%M:%S); produced=$(ls ${REPO}/nd-unfolding/uq_4d/universe_sweep/*.root 2>/dev/null|wc -l)/187"
