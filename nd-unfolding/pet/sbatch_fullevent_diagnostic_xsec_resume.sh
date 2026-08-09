#!/bin/bash
#SBATCH --job-name=fe_diag_xsec
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_diagnostic_nonquotable/logs/fe_diag_xsec_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_diagnostic_nonquotable/logs/fe_diag_xsec_%j.err
#
# CPU-only continuation of a NON-QUOTABLE diagnostic extraction whose expensive GPU push stage
# completed before the original job failed to import ROOT. This script deliberately runs only the
# ROOT-dependent xsec stage and never overwrites or recomputes the preserved push artifact.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PET="${REPO}/nd-unfolding/pet"
OUTDIR="${PET}/fullevent_diagnostic_nonquotable"
MARK="NONQUOTABLE-DIAGNOSTIC"

INPUTS="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
EXPECTED_INPUTS_SHA="fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
WEIGHTS="${PET}/fullevent_nominal/pet_fullevent_nominal_weights.npz"

: "${DIAG_PUSH_JOB_ID:?submit with DIAG_PUSH_JOB_ID=<completed GPU push job id>}"
[[ "${DIAG_PUSH_JOB_ID}" =~ ^[0-9]+$ ]] || {
  echo "[diag-xsec] FATAL: DIAG_PUSH_JOB_ID must be numeric" >&2
  exit 2
}

JOB="${SLURM_JOB_ID:-nojob}"
PUSH_OUT="${OUTDIR}/${MARK}.push.slurm-${DIAG_PUSH_JOB_ID}.npz"
PUSH_DONE="${PUSH_OUT}.done"
XSEC_OUT="${OUTDIR}/${MARK}.xsec.slurm-${JOB}.npz"
SUMMARY="${OUTDIR}/${MARK}.xsec.slurm-${JOB}.summary.json"
MANIFEST="${OUTDIR}/${MARK}.manifest.slurm-${JOB}.json"
RUNLOG="${OUTDIR}/logs/extract_xsec_${JOB}.log"

mkdir -p "${OUTDIR}/logs"
echo "[diag-xsec] job=${JOB} reuses push_job=${DIAG_PUSH_JOB_ID} host=$(hostname)"
echo "[diag-xsec] THIS PRODUCT IS NOT QUOTABLE. No numerical result will be reported here."

for f in "$INPUTS" "$WEIGHTS" "$PUSH_OUT" "$PUSH_DONE"; do
  [[ -s "$f" ]] || { echo "[diag-xsec] FATAL: missing $f" >&2; exit 3; }
done
for f in "$XSEC_OUT" "$SUMMARY" "$MANIFEST"; do
  [[ ! -e "$f" ]] || { echo "[diag-xsec] FATAL: collision at $f" >&2; exit 4; }
done

# This stage imports PyROOT. Assert that contract before reading the 49M-row input; never run it in
# the TensorFlow module environment that caused job 56525297 to fail after its push was complete.
source "${REPO}/setup_salloc_env.sh"
ROOT628_PREFIX="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}"
ROOT_PY="${ROOT628_PREFIX}/bin/python3"
[[ -x "$ROOT_PY" ]] || { echo "[diag-xsec] FATAL: no executable $ROOT_PY" >&2; exit 5; }
"$ROOT_PY" -c 'import ROOT, numpy; assert ROOT.gROOT'

GOT_SHA="$("$ROOT_PY" -c "
import hashlib
h=hashlib.sha256()
with open('${INPUTS}','rb') as fh:
    for c in iter(lambda: fh.read(1<<22), b''): h.update(c)
print(h.hexdigest())")"
[[ "$GOT_SHA" == "$EXPECTED_INPUTS_SHA" ]] || {
  echo "[diag-xsec] FATAL: inputs sha mismatch: $GOT_SHA" >&2
  exit 6
}

export MNV_REPO="$REPO"
export PYTHONUNBUFFERED=1
cd "$PET"

# Full stream is retained; the orchestrator reads the terminal artifact, never a filtered write.
"$ROOT_PY" -u extract_fullevent_fps.py \
  --stage xsec \
  --inputs "$INPUTS" \
  --push-out "$PUSH_OUT" \
  --out "$XSEC_OUT" \
  --summary "$SUMMARY" \
  >>"$RUNLOG" 2>&1

"$ROOT_PY" -u - <<PY >>"$RUNLOG" 2>&1
import sys
sys.path.insert(0, "${PET}")
import pet_diagnostic_quarantine as q
m = q.build_diagnostic_manifest(
    weights_npz="${WEIGHTS}",
    xsec_npz="${XSEC_OUT}",
    push_npz="${PUSH_OUT}",
    xsec_summary="${SUMMARY}",
    inputs_npz="${INPUTS}",
    out_path="${MANIFEST}",
    job_id="${JOB}",
    extra={"launcher": "sbatch_fullevent_diagnostic_xsec_resume.sh",
           "recovery_of_job": "${DIAG_PUSH_JOB_ID}",
           "push_job_id": "${DIAG_PUSH_JOB_ID}",
           "reused_push_without_recompute": True,
           "authorized": "Joseph, 2026-08-09: non-quotable diagnostic"})
assert m.get("publication_gate_rejects_this") is True
assert m.get("publication_gate_rejects_this_on_physics_alone") is True
PY

"$ROOT_PY" - <<PY
import json
with open("${MANIFEST}") as fh:
    m = json.load(fh)
assert m.get("publication_gate_rejects_this") is True
assert m.get("publication_gate_rejects_this_on_physics_alone") is True
print("[diag-xsec] quarantine proof PASS: both publication rejection flags are true")
print("[diag-xsec] manifest=${MANIFEST}")
print("[diag-xsec] DONE. Product is deliberately unquotable; no numerical result reported.")
PY
