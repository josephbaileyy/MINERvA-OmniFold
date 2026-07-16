#!/bin/bash
#SBATCH --job-name=budget4dC
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=01:30:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/budget4dC_%j.out --error=uq_4d/corrected/logs/budget4dC_%j.err
# P6-4D corrected budget (non-lateral trunk): build C_stat + C_ML from the
# regenerated corrected replicas (exact-ID manifest), then the combined block-sum
# systematic (reused 187-file universe sweep; #13 confirmed background-CV is a
# <0.3% null-effect) + norm + C_stat + C_ML. ALL outputs -> uq_4d/corrected/.
# The support-limited lateral bands (Muon reconstruction category) are INCLUDED in
# the sweep block-sum and remain labeled support-limited pending Agent A's
# selection-complete standard lateral replacement (final adoption gate).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
mkdir -p uq_4d/corrected/universe_stage2_4d
CV="products/4d/xsec_4d_MEFHC_5iter_lgbm.root"

echo "[budget4dC] C_ML split (expect 24) $(date -u '+%F %T')"
python3 combine_cov_nd.py --glob 'uq_4d/corrected/seedscan_split_4d/res_split_*.npz' \
  --expected-ids 1-24 --cv "$CV" --tag mlsplit4d --out uq_4d/corrected/uq_cov_mlsplit_4d.root
echo "[budget4dC] C_stat bootstrap (expect 100) $(date -u '+%F %T')"
python3 combine_cov_nd.py --glob 'uq_4d/corrected/boot_nd_4d/res_boot_*.npz' \
  --expected-ids 1-100 --cv "$CV" --tag stat4d --out uq_4d/corrected/uq_cov_stat_4d.root
echo "[budget4dC] combined (sweep + norm + stat + ML) $(date -u '+%F %T')"
python3 analyze_universes_nd.py \
  --cv "$CV" \
  --glob 'uq_4d/universe_sweep/4d_xsec_*_uni_full_*.root' \
  --add-norm 0.014 \
  --bootstrap-cov uq_4d/corrected/uq_cov_stat_4d.root:hCov_stat4d_reported \
                  uq_4d/corrected/uq_cov_mlsplit_4d.root:hCov_mlsplit4d_reported \
  --outdir uq_4d/corrected/universe_stage2_4d/ --out-root uq_universe_4d_covariance_combined.root
echo "[budget4dC] DONE $(date -u '+%F %T')"
