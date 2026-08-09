#!/bin/bash
#SBATCH --job-name=fe_diag_extract
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_diagnostic_nonquotable/logs/fe_diag_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_diagnostic_nonquotable/logs/fe_diag_%j.err
#
# NON-QUOTABLE DIAGNOSTIC full-event extraction. Authorized 2026-08-09.
#
# WHAT THIS IS. The first run of extract_fullevent_fps.py on real input. It became possible on
# 2026-08-08 when the BEN-043 checkpoint fix made Gate A/B bit-exact and check_subsample_agreement
# stopped failing closed at 0.866. Exercising the extractor is information we need whatever Gate-4
# says: it has never touched real data, so this run tests the extractor at least as much as the
# physics.
#
# WHAT THIS IS NOT. A result. The fold-forward deficit is unrepaired -- the reco-weighted mean of
# push is 0.736746 against R = 1.124080 -- so the cross section produced here is knowingly ~34% LOW.
# Branch C of PREDECLARATION-20260808-gate4-and-d2-fraction.md governs: no product is quoted while
# any leg is red. Every output lands in fullevent_diagnostic_nonquotable/ with NONQUOTABLE-DIAGNOSTIC
# in its filename, and the run ends by writing a manifest that PROVES the publication gate rejects
# it -- including proving that a laundered copy (publication schema, marker stripped) is still
# rejected on the recomputed physics alone. See pet_diagnostic_quarantine.py.
#
# Deliberately NOT reusing sbatch_pet_fullevent_nominal.sh: that script is the Gate-4 publication
# launcher and is hash-pinned. This is a separate, clearly-labelled path.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PET="${REPO}/nd-unfolding/pet"
OUTDIR="${PET}/fullevent_diagnostic_nonquotable"
MARK="NONQUOTABLE-DIAGNOSTIC"

INPUTS="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
EXPECTED_INPUTS_SHA="fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
WEIGHTS="${PET}/fullevent_nominal/pet_fullevent_nominal_weights.npz"

JOB="${SLURM_JOB_ID:-nojob}"
PUSH_OUT="${OUTDIR}/${MARK}.push.slurm-${JOB}.npz"
XSEC_OUT="${OUTDIR}/${MARK}.xsec.slurm-${JOB}.npz"
SUMMARY="${OUTDIR}/${MARK}.xsec.slurm-${JOB}.summary.json"
MANIFEST="${OUTDIR}/${MARK}.manifest.slurm-${JOB}.json"

mkdir -p "${OUTDIR}/logs"

echo "[diag] job=${JOB} host=$(hostname)"
echo "[diag] THIS PRODUCT IS NOT QUOTABLE. fold-forward deficit ~34% is unrepaired."

# ---- footing: the dump must be the one the nominal trained on -----------------------------------
for f in "$INPUTS" "$WEIGHTS"; do
  [[ -s "$f" ]] || { echo "[diag] FATAL: missing $f" >&2; exit 2; }
done
GOT_SHA="$(python3 -c "
import hashlib,sys
h=hashlib.sha256()
with open('${INPUTS}','rb') as fh:
    for c in iter(lambda: fh.read(1<<22), b''): h.update(c)
print(h.hexdigest())")"
if [[ "$GOT_SHA" != "$EXPECTED_INPUTS_SHA" ]]; then
  echo "[diag] FATAL: inputs sha mismatch: $GOT_SHA != $EXPECTED_INPUTS_SHA" >&2
  exit 3
fi
echo "[diag] inputs sha OK ${GOT_SHA:0:16}"

module load tensorflow/2.15.0
export MNV_REPO="$REPO"
cd "$PET"

# The step-2 checkpoint is READ FROM THE ARTIFACT'S OWN inference_contract, never hardcoded. Doing it
# after `module load` because the read needs numpy, and this must run in the same interpreter the
# extraction uses. Hardcoding the path is the BEN-072 defect in miniature -- a launcher naming a
# configuration that may not be the one the artifact was built with. The contract also carries
# checkpoint_semantics, so a pre-BEN-043 artifact (whose file held BEST-epoch weights, not the
# trained model) is DETECTED rather than silently consumed.
CKPT="$(python3 -c "
import numpy as np, sys
with np.load('${WEIGHTS}', allow_pickle=True) as z:
    c = z['inference_contract']
    try: c = c.item()
    except Exception: pass
    sem = str(c.get('checkpoint_semantics', ''))
    if 'BEN-043' not in sem:
        sys.exit('checkpoint_semantics=%r lacks the BEN-043 marker: this artifact predates the '
                 'final-epoch fix and its checkpoint is NOT the trained model' % sem)
    print(c['step2_checkpoint'])")"
[[ -s "$CKPT" ]] || { echo "[diag] FATAL: contract names a missing checkpoint: $CKPT" >&2; exit 4; }
echo "[diag] step2 checkpoint from contract: ${CKPT}"

# ---- stage all: push then xsec. Full stream to a file; never piped through tail (BEN-026). ------
RUNLOG="${OUTDIR}/logs/extract_${JOB}.log"
python3 -u extract_fullevent_fps.py \
  --stage all \
  --weights "$WEIGHTS" \
  --step2-checkpoint "$CKPT" \
  --inputs "$INPUTS" \
  --push-out "$PUSH_OUT" \
  --out "$XSEC_OUT" \
  --summary "$SUMMARY" \
  >>"$RUNLOG" 2>&1
echo "[diag] extraction rc=0; log=${RUNLOG}"

# ---- the quarantine manifest, whose non-quotability is PROVEN not asserted ----------------------
python3 -u - <<PY >>"$RUNLOG" 2>&1
import sys
sys.path.insert(0, "${PET}")
import pet_diagnostic_quarantine as q
q.build_diagnostic_manifest(
    weights_npz="${WEIGHTS}",
    xsec_npz="${XSEC_OUT}",
    push_npz="${PUSH_OUT}",
    xsec_summary="${SUMMARY}",
    inputs_npz="${INPUTS}",
    out_path="${MANIFEST}",
    job_id="${JOB}",
    extra={"launcher": "sbatch_fullevent_diagnostic_extract.sh",
           "step2_checkpoint": "${CKPT}",
           "authorized": "Joseph, 2026-08-09: 'launch it, but as a self-declaring "
                         "non-quotable diagnostic'"})
PY

echo "[diag] manifest=${MANIFEST}"
python3 -c "
import json
m=json.load(open('${MANIFEST}'))
print('[diag] publication_gate_rejects_this =', m['publication_gate_rejects_this'])
print('[diag] on physics alone              =', m['publication_gate_rejects_this_on_physics_alone'])
print('[diag] fold-forward dev              =', round(m['fold_forward']['deviation'],6),
      'tol', m['fold_forward']['tolerance'], '->', round(m['fold_forward']['exceeds_tolerance_by'],1),'x')
print('[diag] total sigma (NOT QUOTABLE)    =', json.load(open('${SUMMARY}'))['total_sigma_cm2_per_nucleon'])
"
echo "[diag] DONE. Product is deliberately unquotable."
