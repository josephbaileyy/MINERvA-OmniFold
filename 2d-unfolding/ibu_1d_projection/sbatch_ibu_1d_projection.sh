#!/bin/bash
#SBATCH --job-name=ibu_1d_proj
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --time=00:45:00
#SBATCH --output=ibu_1d_proj_%j.out
#SBATCH --error=ibu_1d_proj_%j.err

# 1D IBU on the 2D OmniFold inputs (advisor's cross-check).
# Pipeline (no event-looping or 2D re-unfolding):
#   1. build_1d_ibu_inputs.py: project the 2D OmniFold TTrees
#      (data, mc_signal_reco, mc_background) onto paper p_T and p_||
#      edges and write MnvH1D/MnvH2D inputs for ExtractCrossSection.
#   2. ExtractCrossSection 5 ...: D'Agostini IBU at 5 iterations.
#      Writes pTmu_crossSection.root and pZmu_crossSection.root.
#   3. plot_ibu_1d_proj_vs_omnifold.py: 3-way comparison
#      (IBU on 2D-projection vs OmniFold-2D 1D-projection vs paper-2D
#      1D projection).
# Walltime: projection ~5-10 min on 24M signal events, IBU + plot ~seconds.

set -eo pipefail
export PYTHONUNBUFFERED=1

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"

WORKDIR="${REPO}/2d-unfolding/ibu_1d_projection"
cd "${WORKDIR}"

# 1. Build the IBU-shaped 1D projections.
python3 build_1d_ibu_inputs.py \
  --omnifile ../runEventLoopOmniFold_MEHFC.root \
  --flux ../baseline_flux/runEventLoopMC_MEHFC.root \
  --xsec-2d ../2d_crossSection_omnifold_MEHFC_5iter_postfix.root \
  --out-data runEventLoop_proj_data.root \
  --out-mc runEventLoop_proj_mc.root \
  --verbose

# 2. D'Agostini IBU at 5 iterations.
# ExtractCrossSection auto-detects prefixes from *_data keys, so it runs
# both pTmu and pZmu in a single invocation and writes
# pTmu_crossSection.root + pZmu_crossSection.root in cwd.
# It segfaults at process-exit during the libMAT cleanup; the unfolded
# outputs are flushed beforehand, so check for them explicitly instead
# of trusting the exit code.
rm -f pTmu_crossSection.root pZmu_crossSection.root
ExtractCrossSection 5 runEventLoop_proj_data.root runEventLoop_proj_mc.root || true
test -s pTmu_crossSection.root || { echo "[FAIL] pTmu_crossSection.root not written"; exit 1; }
test -s pZmu_crossSection.root || { echo "[FAIL] pZmu_crossSection.root not written"; exit 1; }

# 3. 3-way comparison plot per axis.
python3 plot_ibu_1d_proj_vs_omnifold.py \
  --ibu-pt pTmu_crossSection.root \
  --ibu-pz pZmu_crossSection.root \
  --omnifold-2d ../2d_crossSection_omnifold_MEHFC_5iter_postfix.root \
  --paper-2d ../minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root \
  --out-pt MEHFC_5iter_ibu_1d_proj_pt.png \
  --out-pz MEHFC_5iter_ibu_1d_proj_pz.png
