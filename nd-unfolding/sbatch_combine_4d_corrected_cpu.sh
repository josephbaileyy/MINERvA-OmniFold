#!/bin/bash
#SBATCH --job-name=budget4dCc
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=02:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/budget4dCc_%j.out --error=uq_4d/corrected/logs/budget4dCc_%j.err
# P6-4D corrected budget on CPU: C_stat (100) + C_ML (24) exact-id manifests, then the
# combined block-sum systematic (reused 187-file sweep; #13 null) + norm + stat + ML.
# Support-limited lateral bands INCLUDED in the sweep (labeled); final lateral swap
# GATED on Agent A. ALL outputs -> uq_4d/corrected/.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=16 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
cd "${REPO}/nd-unfolding"; mkdir -p uq_4d/corrected/universe_stage2_4d
CV="products/4d/xsec_4d_MEFHC_5iter_lgbm.root"
echo "[budget4dCc] C_ML split (24) $(date -u '+%F %T')"
python3 combine_cov_nd.py --glob 'uq_4d/corrected/seedscan_split_4d/res_split_*.npz' \
  --expected-ids 1-24 --cv "$CV" --tag mlsplit4d --out uq_4d/corrected/uq_cov_mlsplit_4d.root
echo "[budget4dCc] C_stat bootstrap (100) $(date -u '+%F %T')"
python3 combine_cov_nd.py --glob 'uq_4d/corrected/boot_nd_4d/res_boot_*.npz' \
  --expected-ids 1-100 --cv "$CV" --tag stat4d --out uq_4d/corrected/uq_cov_stat_4d.root
echo "[budget4dCc] combined (sweep + norm + stat + ML) $(date -u '+%F %T')"
python3 analyze_universes_nd.py --cv "$CV" \
  --glob 'uq_4d/universe_sweep/4d_xsec_*_uni_full_*.root' --add-norm 0.014 \
  --bootstrap-cov uq_4d/corrected/uq_cov_stat_4d.root:hCov_stat4d_reported \
                  uq_4d/corrected/uq_cov_mlsplit_4d.root:hCov_mlsplit4d_reported \
  --outdir uq_4d/corrected/universe_stage2_4d/ --out-root uq_universe_4d_covariance_combined.root
echo "[budget4dCc] DONE $(date -u '+%F %T')"
