#!/bin/bash
#SBATCH --job-name=pet_bkgsub_in
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=128G --time=03:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=pet/pet_bkgsub_in_%j.out --error=pet/pet_bkgsub_in_%j.err
# Phase 1 of the corrected PET UQ campaign: build the background-subtracted 5D
# point-cloud input with a strict event-by-event alignment gate.
#   pet/build_bkgsub_pointcloud_input.py reads the DATA reco scalars from the
#   full-cloud source ROOT (measured_pc row order), proves alignment vs
#   of_inputs_5d, attaches the 5D bkgsub purity weights, and writes
#   of_inputs_pc_fullcloud_bkgsub_5d.npz + a provenance JSON.
# NOTE: reads the 51 GB source ROOT `data` tree only (no cloud vectors); the
# heavy step is savez_compressed of ~13 GB of cloud tensors -> 128 GB is ample.
# Does NOT touch the unsubtracted of_inputs_pc_fullcloud.npz.
set -eo pipefail
export HOME=/global/homes/j/josephrb          # school-account HOME fix (see INCIDENT 2026-07-11)
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"

OUT="of_inputs_pc_fullcloud_bkgsub_5d.npz"
FORCE_REBUILD="${FORCE_REBUILD:-0}"
MODE_ARGS=""
if [[ -s "${OUT}" && "${FORCE_REBUILD}" != "1" ]]; then
  echo "[bkgsub] ${OUT} already present; re-running gates only (--check-only). Set FORCE_REBUILD=1 to rebuild."
  MODE_ARGS="--check-only"
fi

echo "[bkgsub] python: $(command -v python3)"
python3 -c "import ROOT, numpy; print('ROOT', ROOT.__version__, 'numpy', numpy.__version__)"

echo "[bkgsub] test gate (PET Phase-1 unit tests, fatal) $(date -u +%FT%TZ)"
python3 -m unittest tests.test_pet_bkgsub_input -v
echo "[bkgsub] remediation suite (informational)"
python3 -m unittest tests.test_uq_remediation -v || echo "[WARN] remediation suite had failures/errors (informational, does not block Phase-1 build)"

echo "[bkgsub] start $(date -u +%FT%TZ)"
python3 pet/build_bkgsub_pointcloud_input.py ${MODE_ARGS}
echo "[bkgsub] done $(date -u +%FT%TZ)"
ls -lh "${OUT}" 2>/dev/null || echo "[bkgsub] (check-only: no npz built this run)"
ls -lh products/pet/bkgsub/ 2>/dev/null || true
