#!/bin/bash
#SBATCH --job-name=excess_eW
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=excess_eW_%j.out
#SBATCH --error=excess_eW_%j.err

# Localize the high-E_avail excess (open question 6) in W: unfolded data vs the GENIE CV
# prediction in the (E_avail, W) plane. Single I/O-bound pass over the 4.5 GB 5D omnifile's
# mc_truth_denom tree (shared QoS per the I/O-bound lesson), reusing the frozen unfold
# normalization. Reads -> products/5d/{excess_eavail_W.root,.png}.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"

echo "[excess] start $(date -u '+%F %T UTC')"
python3 excess_eavail_W.py \
    --omnifile runEventLoopOmniFold_5D_MEFHC.root \
    --xsec5d products/5d/xsec_5d_MEFHC_5iter_lgbm.root \
    --axes eavail,q3,W \
    --out products/5d/excess_eavail_W.root \
    --png products/5d/excess_eavail_W.png
echo "[excess] done $(date -u '+%F %T UTC')"
