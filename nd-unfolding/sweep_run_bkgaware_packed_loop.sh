#!/bin/bash
# Node-partitioned packed VERTICAL sweep-run loop for a MULTI-NODE interactive GPU
# salloc (2026-07-14, B5' #13). Escalation path when gpu_shared is fairshare-throttled
# and PET is idle: run the 169 vertical universes (bank-based, ~14min, ~15GB each) off
# bank_sweep_5d_bkgaware. Each srun task (one/node) takes a disjoint round-robin slice
# via SLURM_PROCID/SLURM_NTASKS, CONC=6 concurrent (LightGBM over-spawns ~26 threads/
# worker regardless of OMP, so 6x ~= 128 logical cores; matches boot5d CONC=5). Reads
# the bank (already dumped) -> NO omnifile read. skip-if-exists shares progress with the
# gpu_shared run 55892343 + across nodes. School-acct HOME/ROOT fix inline. NO set -u.
set -o pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
source "$REPO/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=12 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
       NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
cd "$REPO/nd-unfolding"
BANKDIR="$REPO/nd-unfolding/bank_sweep_5d_bkgaware"
OUTDIR="$REPO/nd-unfolding/uq_5d/universe_sweep_bkgaware"; mkdir -p "$OUTDIR"
LIST="$REPO/nd-unfolding/uq_4d/vertical_run_bkgaware.txt"
PROCID=${SLURM_PROCID:-0}; NPROC=${SLURM_NTASKS:-1}; CONC=6
mapfile -t UNIS < "$LIST"
echo "[sweeprunI proc ${PROCID}/${NPROC}] start $(date -u +%T) on $(hostname); ${#UNIS[@]} universes; done=$(ls $OUTDIR/*uni_full_*.root 2>/dev/null|wc -l)"
for i in "${!UNIS[@]}"; do
  (( i % NPROC == PROCID )) || continue               # this node's disjoint slice
  U="${UNIS[$i]}"; [[ -z "$U" ]] && continue
  TAG="${U%:*}_${U#*:}"
  out="$OUTDIR/5d_xsec_MEFHC_5iter_lgbm_uni_full_${TAG}.root"
  [[ -s "$out" ]] && continue
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 10; done
  python3 sweep_bank_5d.py --run --universe "$U" --bankdir "$BANKDIR" \
    --outdir "$OUTDIR" --iters 5 > "$OUTDIR/isweeprun_${TAG}.log" 2>&1 &
done
wait
echo "[sweeprunI proc ${PROCID}] done $(date -u +%T); done=$(ls $OUTDIR/*uni_full_*.root 2>/dev/null|wc -l)"
