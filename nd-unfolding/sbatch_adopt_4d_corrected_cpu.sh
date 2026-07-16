#!/bin/bash
#SBATCH --job-name=adopt4dCc
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=01:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/adopt4dCc_%j.out --error=uq_4d/corrected/logs/adopt4dCc_%j.err
# P6-4D CANDIDATE adoption (mean-centered + CV-centered inflation-transfer). Transfers the
# unified-throw per-bin variance inflation onto the SWEEP vertical block (PSD by
# construction); leaves lateral + stat + ML untouched. The lateral here is the
# SUPPORT-LIMITED sweep lateral -> this is a CANDIDATE. FINAL adoption swaps Agent A's
# selection-complete standard lateral block (dependency gate; not done here). uq_4d/corrected/.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
cd "${REPO}/nd-unfolding"
COMB=uq_4d/corrected/universe_stage2_4d/uq_universe_4d_covariance_combined.root
UT=uq_4d/corrected/unified_throw_cov_4d.root
PROD=products/4d/xsec_4d_MEFHC_5iter_lgbm.root
echo "[adopt4dCc] mean-centered $(date -u '+%F %T')"
python3 adopt_unified_4d.py --uthrow "$UT" --combined "$COMB" --prod "$PROD" \
  --out uq_4d/corrected/universe_stage2_4d/uq_universe_4d_covariance_combined_uthrow.root
echo "[adopt4dCc] CV-centered (F7 conservative variant) $(date -u '+%F %T')"
python3 adopt_unified_4d.py --cv-centered --uthrow "$UT" --combined "$COMB" --prod "$PROD" \
  --out uq_4d/corrected/universe_stage2_4d/uq_universe_4d_covariance_combined_uthrow_cvcentered.root
echo "[adopt4dCc] DONE $(date -u '+%F %T')"
