#!/bin/bash
# Node-partitioned packed boot5d loop for a MULTI-NODE interactive GPU salloc
# (run via salloc + srun --ntasks-per-node=1, 2026-07-13). gpu_interactive is
# salloc-only. Each srun task (one per node) picks a DISJOINT round-robin slice of
# seeds via SLURM_PROCID/SLURM_NTASKS, runs CONC concurrent bootstrap replicas
# (CONC=5: LightGBM over-spawns ~26 threads/worker regardless of OMP, so 5x ~= the
# 128 logical cores; 16 thrashed to load 424). skip-if-exists shares progress with
# the gpu_shared array + across nodes. School-acct HOME/ROOT fix inline. NO set -u
# (breaks conda activate).
set -o pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
source "$REPO/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=12 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
       NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
cd "$REPO/nd-unfolding"; mkdir -p boot_nd_5d
PROCID=${SLURM_PROCID:-0}; NPROC=${SLURM_NTASKS:-1}; CONC=5
echo "[boot5dI proc ${PROCID}/${NPROC}] start $(date -u +%T) on $(hostname); banked=$(ls boot_nd_5d/res_boot_*.npz 2>/dev/null|wc -l)/100"
for s in $(seq 100 -1 1); do
  (( (s-1) % NPROC == PROCID )) || continue          # this node's disjoint slice
  out=boot_nd_5d/res_boot_${s}.npz
  [[ -s "$out" ]] && continue
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 10; done
  python3 bootstrap_nd.py --npz of_inputs_5d.npz --seed ${s} --iters 5 --out "$out" \
    > boot_nd_5d/iboot_${s}.log 2>&1 &
done
wait
echo "[boot5dI proc ${PROCID}] done $(date -u +%T); banked=$(ls boot_nd_5d/res_boot_*.npz 2>/dev/null|wc -l)/100"
