#!/bin/bash
#SBATCH --job-name=pet_csyst_prelim
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=05:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=pet/pet_csyst_prelim_%j.out --error=pet/pet_csyst_prelim_%j.err
# PHASE 6 (preliminary vertical): corrected PET C_syst on the bkgsub nominal
# push weights + pre-fix bank_uthrow_5d. 124 x 32.8M 5D re-binnings (12 knobs x
# 2 endpoints + 100 flux). PRELIMINARY / support-limited (KNOWN_ISSUES #13/#16);
# FINAL needs the GBDT background-aware rebank. CPU + PyROOT (no GPU).
set -eo pipefail
export HOME=/global/homes/j/josephrb
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"
python3 -c "import ROOT, numpy; print('ROOT', ROOT.__version__, 'numpy', numpy.__version__)"
echo "[csyst] start $(date -u +%FT%TZ)"
python3 pet/build_csyst_prelim_bkgsub.py --invalid-ratio neutral
echo "[csyst] done $(date -u +%FT%TZ)"
ls -lh products/pet/bkgsub/pet_csyst_prelim_bkgsub_5d.npz products/pet/bkgsub/pet_csyst_prelim_bkgsub_5d.summary.json 2>/dev/null || true
