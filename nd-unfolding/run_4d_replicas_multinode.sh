#!/bin/bash
# P6-4D node-partitioned packed replica loop for a MULTI-NODE interactive GPU salloc.
# Adapted from the proven boot5d_packed_loop.sh. gpu_interactive is salloc-only.
# Launch: salloc -A m3246_g -q interactive -C gpu -N4 -G16 -t 04:00:00 -J p6_4d_mn \
#           srun --ntasks-per-node=1 --gres=none bash run_4d_replicas_multinode.sh
# Each srun task (ONE per node) takes a DISJOINT round-robin slice via SLURM_PROCID/
# SLURM_NTASKS and runs CONC concurrent replicas as plain `python &` (NO nested srun ->
# avoids the rc=192 trap). This unfold is MEMORY-BANDWIDTH-bound (~4-6 useful/node), so
# throughput scales with NODES, not with per-node CONC. skip-if-exists shares progress
# with the CPU batch arrays + across nodes. School-acct HOME/ROOT inline; NO set -u.
set -o pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
source "$REPO/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=12 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
       NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
cd "$REPO/nd-unfolding"
mkdir -p uq_4d/corrected/boot_nd_4d uq_4d/corrected/seedscan_split_4d uq_4d/corrected/logs
PROCID=${SLURM_PROCID:-0}; NPROC=${SLURM_NTASKS:-1}; CONC=${CONC:-5}
echo "[mn proc ${PROCID}/${NPROC}] start $(date -u +%T) on $(hostname) CONC=$CONC"

declare -a WORK
for i in $(seq 1 24); do WORK+=("ssp $i"); done      # ML split (24)
for i in $(seq 1 100); do WORK+=("boot $i"); done     # stat bootstrap (100)
idx=0
for w in "${WORK[@]}"; do
  if (( idx % NPROC == PROCID )); then
    set -- $w; kind=$1; id=$2
    if [ "$kind" = ssp ]; then
      out=uq_4d/corrected/seedscan_split_4d/res_split_${id}.npz
      if [[ ! -s "$out" ]]; then
        while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 8; done
        python3 seedscan_split.py --npz of_inputs_4d.npz --split-seed ${id} \
          --estimator-seed 42 --train-frac 0.8 --iters 5 --out "$out" \
          > uq_4d/corrected/logs/mn_ssp_${id}.log 2>&1 &
      fi
    else
      out=uq_4d/corrected/boot_nd_4d/res_boot_${id}.npz
      if [[ ! -s "$out" ]]; then
        while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 8; done
        python3 bootstrap_nd.py --npz of_inputs_4d.npz --seed ${id} \
          --estimator-seed 42 --iters 5 --out "$out" \
          > uq_4d/corrected/logs/mn_boot_${id}.log 2>&1 &
      fi
    fi
  fi
  idx=$((idx + 1))
done
wait
echo "[mn proc ${PROCID}] done $(date -u +%T) boot=$(ls uq_4d/corrected/boot_nd_4d/*.npz 2>/dev/null|wc -l) ssp=$(ls uq_4d/corrected/seedscan_split_4d/*.npz 2>/dev/null|wc -l)"
