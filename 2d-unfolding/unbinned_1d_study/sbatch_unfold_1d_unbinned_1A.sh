#!/bin/bash
#SBATCH --job-name=unfold_1d_unb_1A
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128
#SBATCH --time=06:00:00
#SBATCH --output=unfold_1d_unb_1A_%j.out
#SBATCH --error=unfold_1d_unb_1A_%j.err

# 1D unbinned OmniFold rerun on playlist 1A, post-MINOS-fix. Produces:
#   - runEventLoopOmniFold.root        (unbinned TTrees for OmniFold)
#   - runEventLoopData.root, runEventLoopMC.root  (binned, for IBU baseline)
#   - pTmu_crossSection_omnifold.root  (patched 1D unbinned OmniFold)
#   - pTmu_crossSection.root           (D'Agostini IBU on the same selection)
#   - ptmu_gaussian_style_unbinned.pdf (comparison plot)
# Walltime: event loops ~3.5h + ~3.5h + unfold ~30m + IBU + plot ~few min.
#
# Note: ExtractCrossSection segfaults in ROOT's TFile::Close() exit handler
# *after* writing all outputs (recoverable file). We disable pipefail around
# that step and gate on file existence instead of exit code.

set -eo pipefail
export PYTHONUNBUFFERED=1

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"

WORKDIR="${REPO}/2d-unfolding/unbinned_1d_study"
MANIFESTS="${REPO}/2d-unfolding/playlist_manifests"
cd "${WORKDIR}"

# 1. Unbinned OmniFold event loop -> runEventLoopOmniFold.root
runEventLoopOmniFold "${MANIFESTS}/1A_Data.txt" "${MANIFESTS}/1A_MC.txt"

# 2. Binned MINERvA-101 event loop -> runEventLoopData.root, runEventLoopMC.root
runEventLoop "${MANIFESTS}/1A_Data.txt" "${MANIFESTS}/1A_MC.txt"

# 3. Unbinned OmniFold extraction (patched script honoring 2D contract)
python3 unfold_ptmu_omnifold_unbinned.py \
  --omnifile runEventLoopOmniFold.root \
  --datafile runEventLoopData.root \
  --datahist pTmu_data \
  --iters 5 --use-weights --verbose \
  --out pTmu_crossSection_omnifold.root

# 4. D'Agostini IBU baseline on the same patched selection
rm -f pTmu_crossSection.root
ExtractCrossSection 5 runEventLoopData.root runEventLoopMC.root || true
test -s pTmu_crossSection.root

# 5. Comparison plot
python3 plot_gaussian_style_ptmu_unbinned.py \
  --omnifold pTmu_crossSection_omnifold.root \
  --ibu pTmu_crossSection.root \
  --outpdf ptmu_gaussian_style_unbinned.pdf \
  --outpng ptmu_gaussian_style_unbinned.png
