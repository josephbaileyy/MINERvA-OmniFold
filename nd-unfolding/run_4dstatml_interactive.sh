#!/bin/bash
# Runs INSIDE an salloc: remaining 4D bootstrap + ML-split replicas, ~10 concurrent
# srun --overlap. Skips replicas whose output npz already exists (resumable).
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND="${REPO}/nd-unfolding"
echo "[4dstatml] SLURM_JOB_ID=$SLURM_JOB_ID node=$(hostname) start $(date -u +%H:%M:%S)"
MAX=10
launch(){ # kind seed
  local kind=$1 s=$2 cmd
  if [ "$kind" = boot ]; then
    [ -s "${ND}/boot_nd_4d/res_boot_${s}.npz" ] && return
    cmd="python3 bootstrap_nd.py --npz of_inputs_4d.npz --seed ${s} --iters 5 --out boot_nd_4d/res_boot_${s}.npz"
  else
    [ -s "${ND}/seedscan_split_4d/res_split_${s}.npz" ] && return
    cmd="python3 seedscan_split.py --npz of_inputs_4d.npz --split-seed ${s} --train-frac 0.8 --iters 5 --out seedscan_split_4d/res_split_${s}.npz"
  fi
  while [ "$(jobs -rp|wc -l)" -ge "$MAX" ]; do sleep 5; done
  srun --overlap --exact -n1 -c12 bash -lc \
    "source '${REPO}/setup_salloc_env.sh' >/dev/null 2>&1; export OMP_NUM_THREADS=12; cd '${ND}' && ${cmd} >/dev/null 2>&1 && echo '[done] ${kind} ${s}'" &
}
for s in $(seq 1 100); do launch boot $s; done
for s in $(seq 1 24);  do launch split $s; done
wait
echo "[4dstatml] window done $(date -u +%H:%M:%S); boot=$(ls ${ND}/boot_nd_4d/*.npz 2>/dev/null|wc -l)/100 split=$(ls ${ND}/seedscan_split_4d/*.npz 2>/dev/null|wc -l)/24"
