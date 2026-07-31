#!/bin/bash
#SBATCH --job-name=cphi_sweep
#SBATCH --account=bhvk-delta-gpu
#SBATCH --partition=gpuA100x4
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64g
#SBATCH --time=03:00:00
#SBATCH --output=cphi_sweep_%j.out
#SBATCH --error=cphi_sweep_%j.err
# ============================================================================
# Coupled-phi sweep: convert the unread-variable UPPER BOUND into a curve.
#
# WHY: job 20600383 measured extended-minus-base = +0.8752 with phi drawn
# INDEPENDENT of the muon block. Independence maximizes the baseline's
# blindness, so that number bounds the capability gain rather than estimating
# it. Real muon phi couples to (pT,p‖) through MINOS matching and the
# detector's non-azimuthally-symmetric acceptance. This sweeps an
# acceptance-induced coupling and reports gain vs corr(cos phi, pT), so the
# real coupling measured after /pscratch returns (2026-08-03 22:00 PT) can be
# read off the curve instead of guessed.
#
# THE LAMBDA GRID was calibrated locally (numpy only, --calibrate-only,
# 2026-07-30, n=40000):
#   lambda  0.0   0.4   0.6   0.9   1.6   2.2
#   corr    0.007 0.139 0.196 0.305 0.491 0.622
#   accept  100%  68%   57%   43%   25%   16%
# Density is deliberately highest below corr 0.3, the range a real acceptance
# coupling most plausibly lives in; the two high points exist to establish the
# trend, not because that coupling is expected.
#
# N IS HELD FIXED at --n-events across all points (oversample then truncate).
# Letting the thinned sample shrink would confound "gain falls with coupling"
# with "gain falls with training statistics" -- the CLM-006 failure mode.
#
# TWO SEEDS, TWO JOBS. Every point's gain carries retraining noise, and the
# gain is smallest exactly where the curve matters most. Submit this twice with
# SEED=0 and SEED=7; the seed-to-seed spread at each point is the floor the
# curve's shape has to clear, the same discipline feature_rank_arms.py uses.
#
# WHY horovodrun AND NOT PLAIN python3: omnifold/__init__.py calls hvd.init(),
# and the container's OMPI was not built with SLURM PMI, so `srun python3` dies
# at OPAL ERROR ... pmix3x_client.c:112 before reaching any physics.
#
# CONFIG MATCHES job 20600383 (n 60000 / niter 3 / epochs 8 / amplitude 1.2) so
# the lambda=0 point is directly comparable to the +0.8755 already on the books.
# It is an independent redraw, not a bit-reproduction: the thinning path draws
# candidates in chunks, so lambda=0 gives a second realization of that point --
# which is useful, since agreement there validates the whole fixture rewrite.
# ============================================================================
set -eo pipefail

REPO="${REPO:-$HOME/MINERvA-OmniFold}"
SIF="${SIF:-$HOME/tf215.sif}"
SEED="${SEED:-0}"
WORKDIR="${WORKDIR:-/work/nvme/bhvk/$USER/cphi_s${SEED}}"
OUT="${OUT:-$REPO/nd-unfolding/products/pet/closure_coupled_phi_sweep_s${SEED}.json}"
COUPLINGS="${COUPLINGS:-0.0,0.4,0.6,0.9,1.6,2.2}"
NEVENTS="${NEVENTS:-60000}"; NITER="${NITER:-3}"; EPOCHS="${EPOCHS:-8}"; AMPL="${AMPL:-1.2}"

cd "${REPO}/nd-unfolding"
mkdir -p "${WORKDIR}" "$(dirname "${OUT}")"

echo "[cphi] $(date -u +%FT%TZ) start on $(hostname)  seed=${SEED}"
echo "[cphi] git HEAD $(git -C "${REPO}" rev-parse HEAD)"
echo "[cphi] sha256(driver) $(sha256sum pet/closure_coupled_phi_sweep.py | cut -d' ' -f1)"
echo "[cphi] sha256(base)   $(sha256sum pet/closure_unread_variable_phi.py | cut -d' ' -f1)"

apptainer exec --nv --bind "${REPO}","${WORKDIR}" \
    --env PYTHONPATH="${REPO}/omnifold_nn" "${SIF}" \
    horovodrun -np 1 python3 pet/closure_coupled_phi_sweep.py \
        --couplings "${COUPLINGS}" --n-events "${NEVENTS}" --niter "${NITER}" \
        --epochs "${EPOCHS}" --amplitude "${AMPL}" --seed "${SEED}" \
        --workdir "${WORKDIR}" --out "${OUT}"

echo "[cphi] done $(date -u +%FT%TZ)"
