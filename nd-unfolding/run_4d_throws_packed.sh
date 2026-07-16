#!/bin/bash
# P6-4D: inside-salloc packed orchestrator for the corrected unified-throw producers.
# 40 throw-slab tasks (4 throws each -> 160, seed 1000) + 26 block tasks (12 knob
# endpoints as 6 pairs + 100 flux as 20 chunks of 5 -> 124 units). Dispatched as CONC
# concurrent srun --overlap steps on the GPU node host cores. Per-slab skip-if-exists
# -> resumable across interactive-wall deaths. Writes ONLY to uq_4d/corrected/.
# Launch (login-side orchestrator; NO outer srun):
#   salloc -A m3246_g -q interactive -C gpu -N1 -G4 -t 04:00:00 -J p6_4d_thr \
#     bash run_4d_throws_packed.sh
set -o pipefail
export HOME=/global/homes/j/josephrb
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"
mkdir -p uq_4d/corrected/uthrow_slabs_4d uq_4d/corrected/logs
BANK=uq_4d/corrected/bank_uthrow_4d
SL=uq_4d/corrected/uthrow_slabs_4d
CONC=${CONC:-4}                        # CONC x CPT = 128 (1:1 threads:cores; no oversubscription)
CPT=$(( 128 / CONC ))
export OMP_NUM_THREADS=$CPT             # cap LightGBM/OpenMP to per-worker cores (avoid thrash)
export MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
echo "[thr-packed] start $(date -u '+%F %T') CONC=$CONC CPT=$CPT OMP=$OMP_NUM_THREADS node=$(hostname)"

KNOBS=("2p2h,CCQEPauliSupViaKF" "FrAbs_pi,FrElas_N" "HighQ2,LowQ2" "MaCCQE,MaRES" "MFP_N,MvRES" "Rvn2pi,Rvp2pi")

run_throw() {   # $1 = task id 0..39
  local T=$1 off=$(( $1 * 4 )) out="$SL/uthrow4d_slab_$1.npz" log="uq_4d/corrected/logs/pk_thr_$1.log"
  [ -s "$out" ] && { echo "[skip] throw $T"; return 0; }
  srun --overlap --exact -n1 -c"$CPT" --gres=none \
    python3 unified_throw_cov.py --throws 4 --throw-offset "$off" --seed 1000 \
      --bank "$BANK" --iters 5 --invalid-ratio neutral --out "$out" > "$log" 2>&1
  echo "[done] throw $T rc=$?"
}
run_block() {   # $1 = block task id 0..25
  local T=$1 out="$SL/block4d_$1.npz" log="uq_4d/corrected/logs/pk_blk_$1.log"
  [ -s "$out" ] && { echo "[skip] block $T"; return 0; }
  local common=(--blockunits --bank "$BANK" --iters 5 --seed 1000 --invalid-ratio neutral --out "$out")
  if [ "$T" -lt 6 ]; then
    srun --overlap --exact -n1 -c"$CPT" --gres=none \
      python3 unified_throw_cov.py "${common[@]}" --block-knobs "${KNOBS[$T]}" > "$log" 2>&1
  else
    local lo=$(( (T-6)*5 )) hi=$(( (T-6)*5 + 4 ))
    srun --overlap --exact -n1 -c"$CPT" --gres=none \
      python3 unified_throw_cov.py "${common[@]}" --block-knobs none --block-flux "${lo}-${hi}" > "$log" 2>&1
  fi
  echo "[done] block $T rc=$?"
}

active=0
# blocks first (they are the block-sum comparator; also unblocks nothing but are cheap),
# then throws. Interleaving is fine; both are independent.
for T in $(seq 0 25); do
  run_block "$T" & active=$((active+1)); [ "$active" -ge "$CONC" ] && { wait -n; active=$((active-1)); }
done
for T in $(seq 0 39); do
  run_throw "$T" & active=$((active+1)); [ "$active" -ge "$CONC" ] && { wait -n; active=$((active-1)); }
done
wait
echo "[thr-packed] ALL DONE $(date -u '+%F %T') throws=$(ls $SL/uthrow4d_slab_*.npz 2>/dev/null|wc -l) blocks=$(ls $SL/block4d_*.npz 2>/dev/null|wc -l)"
