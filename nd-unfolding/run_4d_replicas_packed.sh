#!/bin/bash
# P6-4D: inside-salloc packed orchestrator for the corrected C_stat/C_ML replicas.
# Runs 100 boot + 24 ml-split as CONC concurrent srun --overlap steps on the
# allocated GPU node's HOST CORES (LightGBM is CPU code). skip-if-exists -> safe to
# relaunch across interactive-wall deaths (resumes). Writes ONLY to uq_4d/corrected/.
# Launch:  salloc -A m3246_g -q interactive -C gpu -N1 -G4 -t 04:00:00 \
#            --export=ALL,HOME=/global/homes/j/josephrb \
#            srun --ntasks=1 --gres=none bash run_4d_replicas_packed.sh
set -o pipefail
export HOME=/global/homes/j/josephrb      # school-acct conda-by-prefix trap (salloc has no --export)
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"
mkdir -p uq_4d/corrected/boot_nd_4d uq_4d/corrected/seedscan_split_4d uq_4d/corrected/logs

CONC=${CONC:-6}                        # CONC=16 THRASHED (mem-bandwidth, OOM on boot phase, 4h/12 ssp).
CPT=$(( 128 / CONC ))                   # 6x21 = full node, 1:1 threads:cores, ~60GB (<216) -> reliable
# CRITICAL: cap LightGBM/OpenMP + BLAS threads to the per-worker core count. Unpinned,
# LightGBM over-spawned ~76 threads on a small cpuset -> thrash (43-min crawls, 0 done).
export OMP_NUM_THREADS=$CPT
export MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
echo "[packed] start $(date -u '+%F %T') CONC=$CONC CPT=$CPT OMP=$OMP_NUM_THREADS node=$(hostname)"

run_one() {
  local kind=$1 id=$2 out log
  if [ "$kind" = boot ]; then
    out="uq_4d/corrected/boot_nd_4d/res_boot_${id}.npz"
    log="uq_4d/corrected/logs/pk_boot_${id}.log"
    [ -s "$out" ] && { echo "[skip] boot $id"; return 0; }
    srun --overlap --exact -n1 -c"$CPT" --gres=none \
      python3 bootstrap_nd.py --npz of_inputs_4d.npz --seed "$id" \
        --estimator-seed 42 --iters 5 --out "$out" > "$log" 2>&1
  else
    out="uq_4d/corrected/seedscan_split_4d/res_split_${id}.npz"
    log="uq_4d/corrected/logs/pk_ssp_${id}.log"
    [ -s "$out" ] && { echo "[skip] ssp $id"; return 0; }
    srun --overlap --exact -n1 -c"$CPT" --gres=none \
      python3 seedscan_split.py --npz of_inputs_4d.npz --split-seed "$id" \
        --estimator-seed 42 --train-frac 0.8 --iters 5 --out "$out" > "$log" 2>&1
  fi
  echo "[done] $kind $id rc=$?"
}

declare -a WORK
for i in $(seq 1 24); do WORK+=("ssp $i"); done      # ML first (only 24; unblocks nothing else but cheap)
for i in $(seq 1 100); do WORK+=("boot $i"); done
active=0
for w in "${WORK[@]}"; do
  run_one $w &
  active=$((active+1))
  if [ "$active" -ge "$CONC" ]; then wait -n; active=$((active-1)); fi
done
wait
echo "[packed] ALL DONE $(date -u '+%F %T')  boot=$(ls uq_4d/corrected/boot_nd_4d/*.npz 2>/dev/null|wc -l) ssp=$(ls uq_4d/corrected/seedscan_split_4d/*.npz 2>/dev/null|wc -l)"
