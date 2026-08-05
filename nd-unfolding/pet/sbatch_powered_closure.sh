#!/bin/bash
#SBATCH --job-name=pwclosure
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=12:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/powered_closure/logs/pwclosure_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/powered_closure/logs/pwclosure_%j.err
#
# D2 POWERED TRUTH-REWEIGHT CLOSURE -- full predeclared protocol, batch route.
#
# Batch and not interactive on purpose: the run outlasts the 4h interactive ceiling AND it must
# outlive the submitting session. An sshproxy certificate is good for 24h; a job that depends on a
# live ssh dies with the certificate, a job that writes its own receipt does not.
#
# Protocol comes from closure_powered_truth_reweight.py's module constants (amplitude 0.35, clip
# z=3, split seed 7, half size 2,000,000) and from train_fullevent_nominal.NOMINAL_SEED_POLICY
# (niter 2, epochs 8, seeds 42/0, batch 512). NOTHING is overridden here -- no --half-size, no
# --amplitude, no --max-events. Passing any of those would move the goalposts the gate checks.
#
# 1 GPU deliberately: batch_size=512 is part of the pinned nominal configuration, and a multi-GPU
# Horovod run makes the EFFECTIVE batch 512*N. One GPU keeps the configuration literally nominal.
#
# set -u intentionally omitted (module/conda hooks abort under nounset -- AGENTS.md).
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DRIVER="${REPO}/nd-unfolding/pet/closure_powered_truth_reweight.py"
INPUTS="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
PRODUCER="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12_RECEIPT.json"

# ---- immutable bound footing ------------------------------------------------------------------
# The driver sha is pinned AT SUBMISSION. If the file is edited between sbatch and dispatch, this
# job dies instead of silently running different code than was reviewed -- the same near-miss that
# almost invalidated the Gate-2 r2 receipt.
EXPECTED_DRIVER_SHA="69bec69697f099fcc4b4760be7d807ae0ebe385f8bf04f5dbf0a889ba8d84a75"
EXPECTED_INPUTS_SHA="fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
EXPECTED_INPUTS_SIZE="9897374636"
EXPECTED_PRODUCER_SHA="d466a0c18deaafa2ae645002c8dbc9b9879476adb45a40a85c0bae9e0129d25e"

OUTDIR="${REPO}/nd-unfolding/pet/powered_closure"
LOG_DIR="${OUTDIR}/logs"
RUN_ID="${POWERED_RUN_ID:-slurm-${SLURM_JOB_ID}}"
REPORT="${OUTDIR}/POWERED_CLOSURE_REPORT.${RUN_ID}.json"
ARTIFACT="${OUTDIR}/POWERED_CLOSURE_ARTIFACT.${RUN_ID}.npz"
WEIGHTS="${OUTDIR}/weights.${RUN_ID}"

mkdir -p "$LOG_DIR" "$WEIGHTS"

fail() { echo "[powered][FAIL] $*" >&2; exit 1; }

# No auto-submit / no login-node execution: a 4M-row PET training must never land on a login node.
[[ -n "${SLURM_JOB_ID:-}" ]] || fail "must run under sbatch (SLURM_JOB_ID unset)"

[[ -f "$DRIVER" ]] || fail "driver missing: $DRIVER"
got="$(sha256sum "$DRIVER" | awk '{print $1}')"
[[ "$got" == "$EXPECTED_DRIVER_SHA" ]] || \
  fail "driver changed after submission: want $EXPECTED_DRIVER_SHA got $got"

[[ -f "$INPUTS" ]] || fail "inputs missing: $INPUTS"
sz="$(stat -c %s "$INPUTS")"
[[ "$sz" == "$EXPECTED_INPUTS_SIZE" ]] || fail "inputs size drift: want $EXPECTED_INPUTS_SIZE got $sz"

# The driver hashes --inputs and --producer-receipt itself and writes both digests into the report;
# these two checks are the SUBMISSION-side copy so a substituted dump fails before 4M rows are read
# rather than after. Cheap relative to the run, and it fails closed.
echo "[powered] hashing inputs (9.9 GB, ~1 min) ..."
gs="$(sha256sum "$INPUTS" | awk '{print $1}')"
[[ "$gs" == "$EXPECTED_INPUTS_SHA" ]] || fail "inputs sha drift: want $EXPECTED_INPUTS_SHA got $gs"
gp="$(sha256sum "$PRODUCER" | awk '{print $1}')"
[[ "$gp" == "$EXPECTED_PRODUCER_SHA" ]] || fail "producer sha drift: want $EXPECTED_PRODUCER_SHA got $gp"

module load tensorflow/2.15.0

cd "$REPO"
echo "[powered] route=batch run_id=${RUN_ID} host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[powered] driver=${EXPECTED_DRIVER_SHA} inputs=${EXPECTED_INPUTS_SHA}"
echo "[powered] HEAD=$(git rev-parse --short HEAD) dirty=$(git status --porcelain --untracked-files=no | wc -l)"

set +e
srun -n 1 -c 32 --gpus=1 python3 "$DRIVER" \
  --inputs "$INPUTS" \
  --producer-receipt "$PRODUCER" \
  --json "$REPORT" \
  --artifact "$ARTIFACT" \
  --weights-folder "$WEIGHTS"
rc=$?
set -e

echo "[powered] driver exit=${rc} end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# The sentinel records the OUTCOME, not merely that the job ran. A collector reading only "the job
# completed" is the vacuous-pass defect; it must be able to distinguish PASS from FAIL from crash.
if [[ $rc -eq 0 && -f "$REPORT" ]]; then
  verdict="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("verdict","<none>"))' "$REPORT")"
else
  verdict="NO_REPORT_rc=${rc}"
fi
{
  echo "run_id=${RUN_ID}"
  echo "job=${SLURM_JOB_ID}"
  echo "rc=${rc}"
  echo "verdict=${verdict}"
  echo "report=${REPORT}"
  echo "artifact=${ARTIFACT}"
  [[ -f "$REPORT" ]] && echo "report_sha256=$(sha256sum "$REPORT" | awk '{print $1}')"
  [[ -f "$ARTIFACT" ]] && echo "artifact_sha256=$(sha256sum "$ARTIFACT" | awk '{print $1}')"
  echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${OUTDIR}/DONE.${RUN_ID}.txt"

echo "[powered] ${verdict} sentinel=${OUTDIR}/DONE.${RUN_ID}.txt"
exit $rc
