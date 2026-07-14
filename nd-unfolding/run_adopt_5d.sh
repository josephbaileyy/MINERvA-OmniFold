#!/bin/bash
# 5D adopt BOTH variants (F7 decision) via interactive-GPU CPU fallback (2026-07-13).
# Mean-centered = default adopt_unified_5d.py (diag C_unified). CV-centered adds
# per-bin mean_shift^2 (mean_shift 1.654e-38 ~37% of sqrt_tr -> non-negligible).
# Archives any stale adopted first. HOME/ROOT fix inline; NO set -u.
set -o pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
source "$REPO/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "$REPO/nd-unfolding"
ARCH=uq_5d/_archive_prehm_20260713; mkdir -p "$ARCH"
for f in uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root \
         uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow_cvcentered.root \
         gbdt_5d_covariance_adopted.root; do
  [ -f "$f" ] && { mv "$f" "$ARCH/" && echo "[adopt] archived stale $f"; }
done
echo "[adopt] === MEAN-CENTERED === $(date -u +%T)"
python3 adopt_unified_5d.py \
  --out uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root
echo "[adopt] === CV-CENTERED (F7) === $(date -u +%T)"
python3 adopt_unified_5d.py --cv-centered \
  --out uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow_cvcentered.root
echo "[adopt] done $(date -u +%T)"
