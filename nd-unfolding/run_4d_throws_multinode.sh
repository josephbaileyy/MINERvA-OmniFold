#!/bin/bash
# P6-4D node-partitioned packed THROW+BLOCK loop for a MULTI-NODE interactive GPU salloc.
# Same pattern as run_4d_replicas_multinode.sh. 40 throw slabs (4 throws each -> 160,
# seed 1000) + 26 block tasks (6 knob-pairs + 20 flux-chunks -> 124 units). Round-robin
# across nodes; CONC concurrent `python &` per node (NO nested srun). skip-if-exists
# cooperates with the CPU batch uthr4dCc/blk4dCc arrays. Launch:
#   salloc -A m3246_g -q interactive -C gpu -N4 -G16 -t 04:00:00 -J p6_4d_thrmn \
#     srun --ntasks-per-node=1 --gres=none bash run_4d_throws_multinode.sh
set -o pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
source "$REPO/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=12 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
       NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
cd "$REPO/nd-unfolding"; mkdir -p uq_4d/corrected/uthrow_slabs_4d uq_4d/corrected/logs
BANK=uq_4d/corrected/bank_uthrow_4d; SL=uq_4d/corrected/uthrow_slabs_4d
PROCID=${SLURM_PROCID:-0}; NPROC=${SLURM_NTASKS:-1}; CONC=${CONC:-4}
KNOBS=("2p2h,CCQEPauliSupViaKF" "FrAbs_pi,FrElas_N" "HighQ2,LowQ2" "MaCCQE,MaRES" "MFP_N,MvRES" "Rvn2pi,Rvp2pi")
echo "[thrmn proc ${PROCID}/${NPROC}] start $(date -u +%T) on $(hostname) CONC=$CONC"

declare -a WORK
for t in $(seq 0 25); do WORK+=("block $t"); done     # block units first
for t in $(seq 0 39); do WORK+=("throw $t"); done      # 160 throws
idx=0
for w in "${WORK[@]}"; do
  if (( idx % NPROC == PROCID )); then
    set -- $w; kind=$1; T=$2
    if [ "$kind" = throw ]; then
      out="$SL/uthrow4d_slab_${T}.npz"; off=$(( T * 4 ))
      if [[ ! -s "$out" ]]; then
        while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
        python3 unified_throw_cov.py --throws 4 --throw-offset "$off" --seed 1000 \
          --bank "$BANK" --iters 5 --invalid-ratio neutral --out "$out" \
          > uq_4d/corrected/logs/mn_thr_${T}.log 2>&1 &
      fi
    else
      out="$SL/block4d_${T}.npz"
      if [[ ! -s "$out" ]]; then
        while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
        if [ "$T" -lt 6 ]; then
          python3 unified_throw_cov.py --blockunits --bank "$BANK" --iters 5 --seed 1000 \
            --invalid-ratio neutral --block-knobs "${KNOBS[$T]}" --out "$out" \
            > uq_4d/corrected/logs/mn_blk_${T}.log 2>&1 &
        else
          lo=$(( (T-6)*5 )); hi=$(( lo+4 ))
          python3 unified_throw_cov.py --blockunits --bank "$BANK" --iters 5 --seed 1000 \
            --invalid-ratio neutral --block-knobs none --block-flux "${lo}-${hi}" --out "$out" \
            > uq_4d/corrected/logs/mn_blk_${T}.log 2>&1 &
        fi
      fi
    fi
  fi
  idx=$((idx + 1))
done
wait
echo "[thrmn proc ${PROCID}] done $(date -u +%T) throws=$(ls $SL/uthrow4d_slab_*.npz 2>/dev/null|wc -l) blocks=$(ls $SL/block4d_*.npz 2>/dev/null|wc -l)"
