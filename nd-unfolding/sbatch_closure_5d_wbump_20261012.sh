#!/bin/bash
#SBATCH --job-name=wclos5d
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=96G
#SBATCH --time=06:00:00
#SBATCH --output=/pscratch/sd/j/josephrb/wclosure_5d_20261012/logs/wclos5d_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/wclosure_5d_20261012/logs/wclos5d_%j.err

# Corrected 5D injected-W-shape closure. Plan (predeclared, committed and pushed before
# submission): docs/orchestration/PREREG-20261012-5d-injected-w-closure.md.
#   arm I: production 5D flags + --closure --closure-reweight-axis W, bump A=0.3 at W=1.23 GeV,
#          sigma 0.15 GeV (the June 2026 run 54062313 used the default centre 0.3 GeV, below
#          physical W, and injected nothing).
#   arm N: the same command without the bump (plain closure); its reference is nominal truth.
#   score: closure_5d_w_bottom_line.py (bottom_line_test.bottom_line_ratio on the W marginal).
#
# Paths are ABSOLUTE on purpose: sbatch executes a COPY of this script, so BASH_SOURCE/$0 do not
# name the checkout. WT is the dedicated worktree pinned to the plan's commit; DATA is the
# canonical tree holding the untracked input ROOT files, read-only here.
set -eo pipefail
WT=/pscratch/sd/j/josephrb/MINERvA-OmniFold-wclosure-20261012
DATA=/pscratch/sd/j/josephrb/MINERvA-OmniFold
OUT=/pscratch/sd/j/josephrb/wclosure_5d_20261012
OMNI5D="${DATA}/nd-unfolding/runEventLoopOmniFold_5D_MEFHC.root"
FLUX_MC="${DATA}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"

source "${DATA}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-32}
export OPENBLAS_NUM_THREADS=${OMP_NUM_THREADS}

echo "[sbatch] job=${SLURM_JOB_ID} node=$(hostname) start=$(date -u '+%F %T UTC')"
echo "[sbatch] worktree HEAD=$(git -C "${WT}" rev-parse HEAD)"
cd "${WT}/nd-unfolding"

COMMON=(--omnifile "${OMNI5D}" --mcfile "${FLUX_MC}" --axes eavail,q3,W --iters 5
        --use-weights --estimator lgbm --seed 42 --bkg-mode purity --closure --verbose)

guard() {  # label, then the entrypoint and its arguments
  local label="$1"; shift
  python3 "${WT}/nd-unfolding/mnv_guarded_run.py" --expect-root "${WT}" \
      --inventory "${OUT}/${label}.oi136-inventory.jsonl" --label "${label}" -- "$@"
}

echo "[sbatch] arm I (W bump at 1.23 GeV) $(date -u +%T)"
guard wclos-I "${WT}/nd-unfolding/unfold_nd_omnifold_unbinned.py" "${COMMON[@]}" \
    --closure-reweight-axis W --closure-amplitude 0.3 --closure-center 1.23 --closure-sigma 0.15 \
    --out "${OUT}/closure_5d_Wbump_c1p23.root" > "${OUT}/closure_5d_Wbump_c1p23.log" 2>&1

echo "[sbatch] arm N (plain closure) $(date -u +%T)"
guard wclos-N "${WT}/nd-unfolding/unfold_nd_omnifold_unbinned.py" "${COMMON[@]}" \
    --out "${OUT}/closure_5d_null.root" > "${OUT}/closure_5d_null.log" 2>&1

echo "[sbatch] score $(date -u +%T)"
guard wclos-score "${WT}/nd-unfolding/closure_5d_w_bottom_line.py" \
    --injected "${OUT}/closure_5d_Wbump_c1p23.root" \
    --injected-log "${OUT}/closure_5d_Wbump_c1p23.log" \
    --null "${OUT}/closure_5d_null.root" \
    --out "${OUT}/closure_5d_w_bottom_line.json"

sha256sum "${OMNI5D}" "${FLUX_MC}" "${OUT}/closure_5d_Wbump_c1p23.root" "${OUT}/closure_5d_null.root" \
    "${OUT}/closure_5d_w_bottom_line.json" > "${OUT}/SHA256SUMS"
cat "${OUT}/SHA256SUMS"
echo "[sbatch] done=$(date -u '+%F %T UTC')"
