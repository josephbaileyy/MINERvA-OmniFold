#!/bin/bash
#SBATCH --job-name=frank_arms
#SBATCH --account=bhvk-delta-gpu
#SBATCH --partition=gpuA100x4
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64g
#SBATCH --time=03:00:00
#SBATCH --output=frank_arms_%j.out
#SBATCH --error=frank_arms_%j.err
# ============================================================================
# Event-feature ranking arms (B-3 evidence): does the event-feature channel
# saturate at the adopted {pT, p‖}?
#
# WHY THIS EXISTS: the only quantitative feature comparison on the books is
# CLM-006, whose own caveat voids it -- its two arms differed in niter (5 vs 2)
# AND train size (40M vs 2M) AND representation, so "4.25%" mixes three effects.
# Every arm here is MATCHED on niter/epochs/rows/split so ONLY the feature block
# varies. See feature_rank_arms.py for the full argument.
#
# WHY eavail/q3: fullevent_fps_dataloader.SCALAR_COLS already carries
# {"pt":0,"pparallel":1,"eavail":2,"q3":3} on BOTH the reco and truth legs, so
# these two extra event features cost no C++ dump, no FPS-CV regeneration, and
# no bound-file edit (`feature_names` is a plumbed parameter).
#
# WHY horovodrun AND NOT PLAIN python3: omnifold/__init__.py finds horovod in
# this container and calls hvd.init(); the container's OMPI was not built with
# SLURM PMI, so a direct `srun python3` dies at
#   OPAL ERROR: Unreachable in file pmix3x_client.c at line 112
# before reaching any physics. (Established by the B-6 stress closure,
# 2026-07-30.) `horovodrun -np 1` inside apptainer starts its own launcher and
# works. Scripts that only import the dataloader module never execute the
# package init, which is why sbatch_fullevent_dryrun_delta.sh needs no horovod.
#
# WHAT THIS RUN IS NOT: real data. `measured_scalars` is absent from the xps2 pc
# npz (CLM-007) and the sidecar of_inputs_5d_fps_xps2.npz is not on Delta, so
# pseudo-data is an independent MC half carrying a KNOWN truth-pT tilt. That
# yields the matched positive control, the retraining floor, and the variance
# inflation -- all prerequisites for reading any real-data arm. The real-data
# arm unblocks when /pscratch returns (2026-08-03 22:00 PT).
# ============================================================================
set -eo pipefail

REPO="${REPO:-$HOME/MINERvA-OmniFold}"
SIF="${SIF:-$HOME/tf215.sif}"
CACHE="${CACHE:-$REPO/nd-unfolding/feature_rank_cache_400k.npz}"
OUTDIR="${OUTDIR:-$REPO/nd-unfolding/products/pet/feature_rank}"
WORKDIR="${WORKDIR:-/work/nvme/bhvk/$USER/frank}"
ARMS="${ARMS:-base,eavail,q3,both}"
# niter 2 / epochs 8 = the PRODUCTION config (FULL_EVENT_FEATURE_CONTRACT.md:36). Measured cost
# from the 2026-07-30 single-arm smoke: 554 reco / 781 gen steps, 198s at 2 epochs, so ~12 min
# per arm at 8 and ~1.8h for the default 9-run seed plan -- inside the 3h wall below. Training to
# the production setting on purpose: a reduced-epoch run would leave "the arms were simply
# under-trained" as a live alternative explanation for any null.
NITER="${NITER:-2}"; EPOCHS="${EPOCHS:-8}"; AMPL="${AMPL:-0.35}"

cd "${REPO}/nd-unfolding"
mkdir -p "${WORKDIR}" "${OUTDIR}"

echo "[frank] $(date -u +%FT%TZ) start on $(hostname)"
echo "[frank] git HEAD $(git -C "${REPO}" rev-parse HEAD)"
echo "[frank] sha256(driver) $(sha256sum pet/feature_rank_arms.py | cut -d' ' -f1)"
echo "[frank] sha256(cache)  $(sha256sum "${CACHE}" | cut -d' ' -f1)"

apptainer exec --nv --bind "${REPO}","${WORKDIR}" \
    --env PYTHONPATH="${REPO}/omnifold_nn" "${SIF}" \
    horovodrun -np 1 python3 pet/feature_rank_arms.py \
        --cache "${CACHE}" --outdir "${OUTDIR}" --workdir "${WORKDIR}" \
        --arms "${ARMS}" --niter "${NITER}" --epochs "${EPOCHS}" --amplitude "${AMPL}"

echo "[frank] done $(date -u +%FT%TZ)"
