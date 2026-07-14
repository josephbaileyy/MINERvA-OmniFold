#!/bin/bash
#SBATCH --job-name=fin5dBKG
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=01:30:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/fin5dBKG_%j.out --error=uq_4d/fin5dBKG_%j.err
# KNOWN_ISSUES #13 finalize (2026-07-14): assemble the bkgaware C_syst budget and
# adopt the unified-throw inflation (both mean- and CV-centered). C_stat/C_ML are
# #13-invariant -> reuse existing uq_cov_stat_5d.root / uq_cov_mlsplit_5d.root; only
# analyze_universes_5d is re-run on the bkgaware vertical sweep. NON-DESTRUCTIVE:
# distinct _bkgaware outputs; the baseline budget stays as the CV-background comparator.
set -eo pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
CV="products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
OUTD="uq_5d/universe_stage2_5d_bkgaware"
COMB="${OUTD}/uq_universe_5d_covariance_combined_bkgaware.root"
mkdir -p "${OUTD}"
echo "[fin-bkg] analyze start $(date -u '+%F %T UTC') on $(hostname)"
python3 analyze_universes_5d.py \
  --cv "${CV}" \
  --glob 'uq_5d/universe_sweep_bkgaware/5d_xsec_*_uni_full_*.root' \
  --add-norm 0.014 \
  --bootstrap-cov uq_cov_stat_5d.root:hCov_stat5d_reported \
                  uq_cov_mlsplit_5d.root:hCov_mlsplit5d_reported \
  --outdir "${OUTD}/" --out-root uq_universe_5d_covariance_combined_bkgaware.root
echo "[fin-bkg] adopt (mean-centered) $(date -u '+%F %T UTC')"
python3 adopt_unified_5d.py \
  --uthrow uq_5d/unified_throw_cov_5d.root \
  --combined "${COMB}" \
  --out "${OUTD}/uq_universe_5d_covariance_combined_bkgaware_uthrow.root"
echo "[fin-bkg] adopt (CV-centered, F7) $(date -u '+%F %T UTC')"
python3 adopt_unified_5d.py \
  --uthrow uq_5d/unified_throw_cov_5d.root \
  --combined "${COMB}" \
  --cv-centered \
  --out "${OUTD}/uq_universe_5d_covariance_combined_bkgaware_uthrow_cvcentered.root"
echo "[fin-bkg] done $(date -u '+%F %T UTC')"
ls -la "${OUTD}"/*.root
