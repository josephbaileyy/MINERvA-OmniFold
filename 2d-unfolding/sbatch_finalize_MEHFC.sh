#!/bin/bash
#SBATCH --job-name=finalize_MEHFC
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=finalize_MEHFC_%j.out
#SBATCH --error=finalize_MEHFC_%j.err

# Final paper comparison and plot regeneration on the patched-binary
# full-MEHFC 5-iter unfold output. Designed to run as an afterok
# dependency of the unfold job.

set -eo pipefail

export PYTHONUNBUFFERED=1

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/2d-unfolding"

OURS=2d_crossSection_omnifold_MEHFC_5iter.root

echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] ours: ${OURS}"

if [[ ! -s "${OURS}" ]]; then
    echo "[sbatch] missing ${OURS}; aborting" >&2
    exit 1
fi

python compare_to_paper_fullcov.py --ours "${OURS}"
python compare_to_paper_interior.py --ours "${OURS}"
python plot_2d_paper_comparison.py --infile "${OURS}" --prefix MEHFC_5iter_xsec_paper
python plot_2d_cross_section.py --infile "${OURS}" --prefix MEHFC_5iter_xsec

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
