#!/bin/bash
# Merge the 12 bkg-aware per-playlist 5D omnifiles into one MEFHC file via the
# SetMaxTreeSize Python merger (NOT bare hadd - universe trees exceed ROOT's 100GB
# rollover). Interactive-GPU CPU fallback (2026-07-13). HOME/ROOT fix; NO set -u.
set -o pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
source "$REPO/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "$REPO/nd-unfolding"
OUT="runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root"
INPUTS=""
for PL in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
  F="runEventLoopOmniFold_5D_${PL}_universes_full_bkgaware.root"
  [[ -s "$F" ]] || { echo "[merge-bkg] FAIL missing $F" >&2; exit 2; }
  INPUTS="${INPUTS} ${F}"
done
echo "[merge-bkg] start $(date -u +%T) on $(hostname)"
python3 ../2d-unfolding/uq/hadd_universes_full.py "${OUT}" ${INPUTS}
echo "[merge-bkg] done $(date -u +%T)"; ls -la "${OUT}"
