#!/bin/bash
#SBATCH --job-name=cdeltaC
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=03:00:00 --nice=20000
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq/cdeltaCg_%A.out --error=uq/cdeltaCg_%A.err
# WS3 (Agent C): paired OmniFold-vs-IBU method-difference covariance C_delta on the 2D grid.
# Own allocation (no FPS/claude-hold contention). Loads the 2.1GB event file once (RDataFrame+MT),
# nominal + R paired bootstrap replicas through RooUnfoldBayes(IBU) AND RooUnfoldOmnifold on the
# SAME response/measured draw -> C_delta + method-difference statistic. Non-destructive JSON output.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
export ROOT628_PREFIX="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/2d-unfolding"
python3 ibu_omnifold_paired_cdelta.py \
    --omnifile runEventLoopOmniFold_MEFHC.root --niter 5 \
    --replicas "${REPLICAS:-100}" --seed 20260716 --streams both \
    --out uq/ibu_omnifold_cdelta
