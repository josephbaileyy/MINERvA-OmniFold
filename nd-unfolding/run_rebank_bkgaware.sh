#!/bin/bash
# Rebuild the 5D unified-throw bank from the BKG-AWARE merged omnifile (#13),
# NON-DESTRUCTIVE -> DISTINCT bank_uthrow_5d_bkgaware (never touches bank_uthrow_5d).
# Mirrors sbatch_uthrow_dump_5d.sh (unified_throw.py --dump, 8 groups, --axes
# eavail,q3,W). ~110GB/group -> 2 groups/node on a 256GB GPU node. Node-partitioned
# round-robin (g%NPROC==PROCID), CONC=2/node. Group 0 writes cv.npz. HOME/ROOT fix;
# NO set -u.
set -o pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
source "$REPO/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "$REPO/nd-unfolding"
OMNI="$REPO/nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root"
BANKDIR="$REPO/nd-unfolding/bank_uthrow_5d_bkgaware"; mkdir -p "$BANKDIR" uq_5d
PROCID=${SLURM_PROCID:-0}; NPROC=${SLURM_NTASKS:-1}; CONC=2
echo "[rebank-bkg proc ${PROCID}/${NPROC}] start $(date -u +%T) on $(hostname)"
for g in 0 1 2 3 4 5 6 7; do
  (( g % NPROC == PROCID )) || continue
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 10; done
  python3 unified_throw.py --dump --group ${g} --ngroups 8 --omnifile "$OMNI" \
    --axes eavail,q3,W --bankdir "$BANKDIR" \
    > uq_5d/rebank_bkg_g${g}.log 2>&1 && echo "[grp ${g} done] $(date -u +%T)" &
done
wait
echo "[rebank-bkg proc ${PROCID}] done $(date -u +%T)"
