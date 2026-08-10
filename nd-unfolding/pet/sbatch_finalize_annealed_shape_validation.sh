#!/bin/bash
#SBATCH --job-name=ann_shape_fin
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/annealed_shape_validation/logs/ann_shape_finalize_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/annealed_shape_validation/logs/ann_shape_finalize_%j.err
#
# CPU-only independent finalization of source training job 56552326.  Reuses its report/artifact;
# does not train and cannot edit or promote the shared engine.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PET="${REPO}/nd-unfolding/pet"
OUT="${PET}/annealed_shape_validation"
SOURCE_JOB="56552326"
JOB="${SLURM_JOB_ID:-nojob}"
PY="/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3"

REPORT="${OUT}/NONQUOTABLE-DIAGNOSTIC.POWERED_CLOSURE_ANNEALED.slurm-${SOURCE_JOB}.json"
ARTIFACT="${OUT}/NONQUOTABLE-DIAGNOSTIC.POWERED_CLOSURE_ANNEALED.slurm-${SOURCE_JOB}.npz"
PREFLIGHT="${OUT}/NONQUOTABLE-DIAGNOSTIC.PREFLIGHT.slurm-${SOURCE_JOB}.json"
MANIFEST="${OUT}/NONQUOTABLE-DIAGNOSTIC.manifest.slurm-${SOURCE_JOB}.json"
RECEIPT="${OUT}/NONQUOTABLE-DIAGNOSTIC.INDEPENDENT_VALIDATION.slurm-${JOB}.json"
LOCK="${OUT}/.finalize-source-${SOURCE_JOB}.lock"
INPUTS="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
GATE2="${REPO}/nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json"
NOMINAL_WEIGHTS="${PET}/fullevent_nominal/pet_fullevent_nominal_weights.npz"
FINALIZER="${PET}/finalize_annealed_shape_validation.py"

[[ -x "$PY" ]] || { echo "[ann-finalize] FATAL: missing Python $PY" >&2; exit 2; }
for path in "$REPORT" "$ARTIFACT" "$PREFLIGHT" "$INPUTS" "$GATE2" "$NOMINAL_WEIGHTS" "$FINALIZER"; do
  [[ -s "$path" ]] || { echo "[ann-finalize] FATAL: missing $path" >&2; exit 3; }
done
[[ -s "$MANIFEST" ]] || { echo "[ann-finalize] FATAL: missing committed manifest" >&2; exit 4; }
[[ ! -e "$RECEIPT" && ! -e "$LOCK" ]] || {
  echo "[ann-finalize] FATAL: collision in finalizer receipt/lock" >&2
  exit 4
}

export MNV_REPO="$REPO"
export PYTHONPATH="${REPO}/nd-unfolding:${PET}${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONUNBUFFERED=1
cd "$REPO"

"$PY" -u "$FINALIZER" \
  --report "$REPORT" \
  --artifact "$ARTIFACT" \
  --preflight "$PREFLIGHT" \
  --inputs "$INPUTS" \
  --gate2-receipt "$GATE2" \
  --nominal-weights "$NOMINAL_WEIGHTS" \
  --manifest "$MANIFEST" \
  --receipt "$RECEIPT" \
  --lock "$LOCK" \
  --source-job "$SOURCE_JOB" \
  --expected report:"$REPORT":f7f764594f384ea5dcb0f68809d6e1e185bb405992faaf87a013928daee9c015 \
  --expected artifact:"$ARTIFACT":1c5a8fef4683b2114a27272b6d7652129c9d3d22aed7dae68d54c0ddaa780202 \
  --expected preflight:"$PREFLIGHT":8411c2bddbe8c6de286c43cf39e6d936a5ba69da978f0d97f5937175d068bc01 \
  --expected manifest:"$MANIFEST":d21b87ba308b88d8b3f6994db7e8da79aeb5503e0708c9df8f69544faed5b4d7 \
  --expected inputs:"$INPUTS":fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625 \
  --expected gate2-receipt:"$GATE2":336e8e27fc8afce813f3ee743c6466ea047243c6e4f457e1d040868d5800792f \
  --expected nominal-weights:"$NOMINAL_WEIGHTS":58f664cdef266d09cbae22a55698f6ff0059ecde4bef80681df9f907f2f51084 \
  --expected finalizer:"$FINALIZER":aa9533ce623736de2335577d48fa48a9d8bfe5b9db0984a57946b064ef7718e6 \
  --expected validator:"${PET}/validate_pet_nominal_gate4.py":024e718d97efb3fc80d23d333a5126a789b9e5f48411907e823b9ec2149a20f9 \
  --expected quarantine:"${PET}/pet_diagnostic_quarantine.py":62cec59b3072c10a276e0ab85d76b95bdfa0c96ae2e35d545cb066d4e5e4a641 \
  --expected source-wrapper:"${PET}/closure_powered_annealed_lr.py":ce9f11f4872dd611932705e36f4ecfb651f8ee8eed796cca98be598d92fbb911 \
  --expected source-driver:"${PET}/closure_powered_truth_reweight.py":a45fae7c3f978c34bf73f35ab56aac668439c5784a3968b4f09799ee6090fd48 \
  --expected source-launcher:"${PET}/sbatch_annealed_shape_validation.sh":fb6b3219f3ff2dbc682ff2987b3f71b56a2a59a53c34779c26e986b2f7fe071f \
  --expected source-engine:"${REPO}/omnifold_nn/omnifold/omnifold.py":3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa

echo "[ann-finalize] DONE source_job=${SOURCE_JOB} finalizer_job=${JOB} receipt=${RECEIPT}"
