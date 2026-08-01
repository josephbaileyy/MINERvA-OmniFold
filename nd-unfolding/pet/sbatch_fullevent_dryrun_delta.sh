#!/bin/bash
#SBATCH --job-name=fe_dryrun
#SBATCH --account=bhvk-delta-cpu
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64g
#SBATCH --time=01:30:00
#SBATCH --output=fe_dryrun_%j.out
#SBATCH --error=fe_dryrun_%j.err
# ============================================================================
# Full-event (Gate-4 / P5A) CODE-PATH DRY RUN on a SYNTHETIC fixture.
#
# WHY: build_fullevent_loaders fail-closes on anything that is not a
# `g2-fullevent-v1` NPZ, and the only such file is G2_FPS_MEFHC_P12.npz on
# Perlmutter /pscratch -- unreachable during the 2026-07-22..08-03 maintenance.
# Without a synthetic stand-in, NOTHING on Delta can reach the full-event code
# path, and every latent launch bug waits until the restore to surface.
#
# WHAT THIS PROVES: the schema/manifest/alignment/identity gates, the CLM-007
# data-scalar path, the negweight-refined target construction, the cloud +
# event-feature assembly, and the ordinary closure all execute.
#
# WHAT THIS DOES NOT PROVE: anything physical. The fixture is random numbers.
# It also cannot exercise the CANONICAL Stay-Positive refiner: that lives in
# unfold_2d_omnifold_unbinned, which imports ROOT, and the NGC container has no
# ROOT (verified 2026-07-25). Stage 2 below therefore injects the
# algorithm-identical sklearn refinement the login-safe tests use, and the
# resulting telemetry is stamped refinement_is_learned_production=False.
# CPU partition on purpose: keeps the GPU allocation for real training.
# ============================================================================
set -eo pipefail

REPO="${REPO:-$HOME/MINERvA-OmniFold}"
source "${REPO}/lib/resume_guard.sh"   # BEN-023: resume on a completion marker, not on size
SIF="${SIF:-$HOME/tf215.sif}"
SYNTH_DIR="${SYNTH_DIR:-/work/nvme/bhvk/$USER/synth}"
FIXTURE="${FIXTURE:-$SYNTH_DIR/G2_SYNTH_P12.npz}"
N_SIG="${N_SIG:-60000}"; N_DATA="${N_DATA:-12000}"; N_BKG="${N_BKG:-4000}"; TOKENS="${TOKENS:-40}"
MAXEV="${MAXEV:-6000}"; NITER="${NITER:-1}"; EPOCHS="${EPOCHS:-1}"

cd "${REPO}/nd-unfolding/pet"
mkdir -p "${SYNTH_DIR}"
RUN="apptainer exec --bind ${REPO},${SYNTH_DIR} --env PYTHONPATH=${REPO}/omnifold_nn ${SIF}"

echo "[dryrun] $(date -u +%FT%TZ) start on $(hostname)"

# ---- stage 1: fixture (idempotent) ----------------------------------------
if rg_is_complete "${FIXTURE}"; then
    echo "[dryrun] stage 1 SKIP -- fixture exists: ${FIXTURE}"
else
    echo "[dryrun] stage 1 -- generating synthetic g2-fullevent-v1 fixture"
    rg_run "${FIXTURE}" ${RUN} python3 make_synthetic_g2_fullevent.py --out "${FIXTURE}" \
        --n-sig "${N_SIG}" --n-data "${N_DATA}" --n-bkg "${N_BKG}" --tokens "${TOKENS}" \
        --seed 0 --receipt "${FIXTURE%.npz}_RECEIPT.json"
fi

# ---- stage 2: negweight-refined target construction (sklearn refiner) ------
echo "[dryrun] stage 2 -- negweight-refined loader build (sklearn-injected refiner)"
${RUN} python3 - "${FIXTURE}" <<'PY'
import sys, json
sys.path[:0] = ['.', '..', '../tests']
import numpy as np
import fullevent_fps_dataloader as fe
from test_fullevent_gate2 import sklearn_refine     # algorithm-identical, ROOT-free

data, mc, imc, cr, cg, meta = fe.build_fullevent_loaders(
    sys.argv[1], max_events=6000, seed=0, bkg_mode="negweight-refined",
    refine_fn=sklearn_refine)
t = meta["target"]
print("[stage2] fingerprint       ", meta["estimator_fingerprint"])
print("[stage2] data_scalar_source", meta["data_scalar_source"])
print("[stage2] identities        ", {k: v[:12] for k, v in meta["input_identity_hashes"].items()})
for k in sorted(t):
    if k not in ("input_identity_hashes",):
        print("[stage2]   target.%-28s %s" % (k, t[k]))
print("[stage2] mc reco", np.asarray(mc.reco).shape, "gen", np.asarray(mc.gen).shape,
      "coord", cr, cg)
print("[stage2] measured rows", np.asarray(data.reco).shape[0])
assert t["refinement_is_learned_production"] is False, "sklearn shim must not claim production"
assert t["n_measured_rows"] == t["n_data_rows"] + t["n_bkg_rows"]
print("[stage2] OK")
PY

# ---- stage 3: ordinary closure (purity control; needs no ROOT) -------------
echo "[dryrun] stage 3 -- ordinary self-consistency closure (purity control)"
${RUN} python3 closure_fullevent_fps.py --inputs "${FIXTURE}" --bkg-mode purity \
    --max-events "${MAXEV}" --niter "${NITER}" --epochs "${EPOCHS}" \
    --weights-folder "${SYNTH_DIR}/fe_closure_w" || echo "[dryrun] stage 3 exit=$?"

echo "[dryrun] done $(date -u +%FT%TZ)"
