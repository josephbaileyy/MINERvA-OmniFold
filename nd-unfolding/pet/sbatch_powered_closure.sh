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
# THE --output DIRECTORY MUST EXIST BEFORE sbatch. slurmstepd opens the batch stdout/stderr paths
# before it execs this script, and SLURM does not create their parent directories -- so the
# `mkdir -p "$LOG_DIR"` below is far too late to help. Job 56355818 was submitted with
# powered_closure/logs/ absent: it would have held its queue slot for hours and then died at
# dispatch with nothing written anywhere. The directory is therefore TRACKED in git (via
# powered_closure/logs/.gitkeep) so that it exists in every checkout and this cannot recur; the
# mkdir stays as the belt to that braces, for a checkout where the marker was pruned.
#
# Batch and not interactive on purpose: the run outlasts the 4h interactive ceiling AND it must
# outlive the submitting session. An sshproxy certificate is good for 24h; a job that depends on a
# live ssh dies with the certificate, a job that writes its own receipt does not.
#
# Protocol comes from closure_powered_truth_reweight.py's module constants (amplitude 0.35, clip
# z=3, split seed 7, half size 2,000,000) and from train_fullevent_nominal.NOMINAL_SEED_POLICY
# (epochs 8, seeds 42/0, batch 512). NOTHING is overridden here -- no --half-size, no
# --amplitude, no --max-events. Passing any of those would move the goalposts the gate checks.
#
# `niter` is DELIBERATELY NOT RESTATED HERE. It is read at runtime from NOMINAL_SEED_POLICY
# (closure_powered_truth_reweight.py:265), and this comment used to assert "niter 2" alongside the
# other constants. That became false the moment 2b2e5f1 switched the policy 2 -> 3 on 2026-08-06;
# the launcher's BEHAVIOUR stayed correct (it overrides nothing) but its documentation did not, and
# a stale protocol comment in a launcher is exactly what gets cited later as evidence of what a run
# actually used. Job 56381674 ran at niter=3 under this file while the comment still said 2.
# Read the configuration out of the report's `configuration.niter`, never out of this header.
#
# 1 GPU deliberately: batch_size=512 is part of the pinned nominal configuration, and a multi-GPU
# Horovod run makes the EFFECTIVE batch 512*N. One GPU keeps the configuration literally nominal.
#
# set -u intentionally omitted (module/conda hooks abort under nounset -- AGENTS.md).
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DRIVER="${REPO}/nd-unfolding/pet/closure_powered_truth_reweight.py"
PREFLIGHT="${REPO}/nd-unfolding/pet/preflight_powered_closure.py"
INPUTS="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
PRODUCER="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12_RECEIPT.json"

# ---- immutable bound footing ------------------------------------------------------------------
# The driver sha is pinned AT SUBMISSION. If the file is edited between sbatch and dispatch, this
# job dies instead of silently running different code than was reviewed -- the same near-miss that
# almost invalidated the Gate-2 r2 receipt.
#
# The two CODE pins below are written in the one-line `[[ "$(sha_of "$VAR")" == "$EXPECTED_..." ]]`
# idiom because that is the only form docs/orchestration/verify_hash_bindings.py can discover:
# collect_shell pairs a pin to a file by reading a SINGLE line that mentions exactly one
# `sha_of "$VAR"` and exactly one `$EXPECTED_*_SHA`. This launcher previously split the driver check
# across an assignment and a comparison, which enforced the pin at runtime but left it invisible to
# the repo-wide verifier -- so a later edit to the driver would have gone on satisfying the verifier
# while this pin was already stale. That is the pin cascade with the alarm disconnected.
EXPECTED_DRIVER_SHA="69bec69697f099fcc4b4760be7d807ae0ebe385f8bf04f5dbf0a889ba8d84a75"
EXPECTED_PREFLIGHT_SHA="dee9aa20a49a89eb5553a4f75672cfde5e9ce05df8f4c9ae00095c549e5ce9bb"
EXPECTED_INPUTS_SHA="fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
EXPECTED_INPUTS_SIZE="9897374636"
EXPECTED_PRODUCER_SHA="d466a0c18deaafa2ae645002c8dbc9b9879476adb45a40a85c0bae9e0129d25e"

# Relative tolerance for the post-run cross-check of the preflight against the driver's own numbers.
# NOT an equality: the preflight reads w_truth as float64, while the engine's copy is float32 by
# contract (DataLoader normalize=True scales it by one float32 constant), so the two agree only to
# float32 round-off, ~1e-6 relative on a unit-normalized 285-cell L1. 1e-4 is two decades above that
# and still two decades below the percent-level shift a wrong subsample or a wrong tilt would cause.
PREFLIGHT_XCHECK_RTOL="1e-4"

OUTDIR="${REPO}/nd-unfolding/pet/powered_closure"
LOG_DIR="${OUTDIR}/logs"
RUN_ID="${POWERED_RUN_ID:-slurm-${SLURM_JOB_ID}}"
REPORT="${OUTDIR}/POWERED_CLOSURE_REPORT.${RUN_ID}.json"
ARTIFACT="${OUTDIR}/POWERED_CLOSURE_ARTIFACT.${RUN_ID}.npz"
PREFLIGHT_RECEIPT="${OUTDIR}/POWERED_PREFLIGHT.${RUN_ID}.json"
WEIGHTS="${OUTDIR}/weights.${RUN_ID}"

mkdir -p "$LOG_DIR" "$WEIGHTS"

fail() { echo "[powered][FAIL] $*" >&2; exit 1; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }

# The sentinel records the OUTCOME, not merely that the job ran. A collector reading only "the job
# completed" is the vacuous-pass defect; it must be able to distinguish PASS from FAIL from crash.
# A function, not a trailing block, because the preflight-abort path below must write one too -- a
# gate that stops the run and leaves no sentinel is indistinguishable from a job that never started.
write_sentinel() {   # $1 = rc, $2 = verdict
  {
    echo "run_id=${RUN_ID}"
    echo "job=${SLURM_JOB_ID}"
    echo "rc=$1"
    echo "verdict=$2"
    echo "preflight_verdict=${pf_verdict:-<not-reached>}"
    echo "preflight_xcheck=${xcheck:-<not-reached>}"
    echo "preflight_receipt=${PREFLIGHT_RECEIPT}"
    echo "report=${REPORT}"
    echo "artifact=${ARTIFACT}"
    [[ -f "$PREFLIGHT_RECEIPT" ]] && echo "preflight_receipt_sha256=$(sha_of "$PREFLIGHT_RECEIPT")"
    [[ -f "$REPORT" ]] && echo "report_sha256=$(sha_of "$REPORT")"
    [[ -f "$ARTIFACT" ]] && echo "artifact_sha256=$(sha_of "$ARTIFACT")"
    echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "${OUTDIR}/DONE.${RUN_ID}.txt"
  echo "[powered] $2 sentinel=${OUTDIR}/DONE.${RUN_ID}.txt"
}

# No auto-submit / no login-node execution: a 4M-row PET training must never land on a login node.
[[ -n "${SLURM_JOB_ID:-}" ]] || fail "must run under sbatch (SLURM_JOB_ID unset)"

[[ -f "$DRIVER" ]] || fail "driver missing: $DRIVER"
[[ "$(sha_of "$DRIVER")" == "$EXPECTED_DRIVER_SHA" ]] || \
  fail "driver changed after submission (want $EXPECTED_DRIVER_SHA)"

[[ -f "$PREFLIGHT" ]] || fail "preflight gate missing: $PREFLIGHT"
[[ "$(sha_of "$PREFLIGHT")" == "$EXPECTED_PREFLIGHT_SHA" ]] || \
  fail "preflight gate changed after submission (want $EXPECTED_PREFLIGHT_SHA)"

[[ -f "$INPUTS" ]] || fail "inputs missing: $INPUTS"
sz="$(stat -c %s "$INPUTS")"
[[ "$sz" == "$EXPECTED_INPUTS_SIZE" ]] || fail "inputs size drift: want $EXPECTED_INPUTS_SIZE got $sz"

# The driver hashes --inputs and --producer-receipt itself and writes both digests into the report;
# these two checks are the SUBMISSION-side copy so a substituted dump fails before 4M rows are read
# rather than after. Cheap relative to the run, and it fails closed.
#
# Left in the two-line form deliberately, unlike the code pins above: making a 9.9 GB pin
# verifier-discoverable would add a second full-file sha256 to every verify_hash_bindings.py run
# (it memoizes nothing) and therefore to every `pytest test_hash_bindings.py`. The identical digest
# is already walked, from run_gate2_target_validator.sh's EXPECTED_INPUT_SHA.
echo "[powered] hashing inputs (9.9 GB, ~1 min) ..."
gs="$(sha_of "$INPUTS")"
[[ "$gs" == "$EXPECTED_INPUTS_SHA" ]] || fail "inputs sha drift: want $EXPECTED_INPUTS_SHA got $gs"
gp="$(sha_of "$PRODUCER")"
[[ "$gp" == "$EXPECTED_PRODUCER_SHA" ]] || fail "producer sha drift: want $EXPECTED_PRODUCER_SHA got $gp"

module load tensorflow/2.15.0

cd "$REPO"
echo "[powered] route=batch run_id=${RUN_ID} host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[powered] driver=${EXPECTED_DRIVER_SHA} inputs=${EXPECTED_INPUTS_SHA}"
echo "[powered] preflight=${EXPECTED_PREFLIGHT_SHA}"
echo "[powered] HEAD=$(git rev-parse --short HEAD) dirty=$(git status --porcelain --untracked-files=no | wc -l)"

# ---- submission-side gate: the criteria the GPU cannot influence -------------------------------
# `gap` and `floor/gap` are deterministic in the dump plus two seeds; only `residual` needs the
# ~8-GPU-hour MultiFold run. So evaluate them FIRST, in ~12 s on the allocated node, and refuse to
# train when they already decide the verdict. There is no override switch on purpose: an env var
# that skips a gate is the vacuous pass this file spends its comments avoiding.
#
# Deliberately NOT under srun: it is a 12-second single-core numpy job that reads three .npy members
# (~1 GB) and never touches part_reco/part_gen, and it must not be charged a task slot or load the
# engine. It runs under the SAME python as the driver, from the same `module load` above, so the
# `default_rng(subsample_seed)` stream that picks the 4M rows is the driver's stream and not another
# numpy's.
echo "[powered] preflight: training-independent criteria at the predeclared configuration ..."
set +e
python3 "$PREFLIGHT" --inputs "$INPUTS" --json "$PREFLIGHT_RECEIPT" --inputs-sha256 "$gs"
pf_rc=$?
set -e
if [[ -f "$PREFLIGHT_RECEIPT" ]]; then
  pf_verdict="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("verdict","<none>"))' "$PREFLIGHT_RECEIPT")"
else
  pf_verdict="NO_RECEIPT_rc=${pf_rc}"
fi
if [[ $pf_rc -ne 0 ]]; then
  write_sentinel "$pf_rc" "PREFLIGHT_${pf_verdict}"
  # Exits with the GATE's code, not fail()'s hardcoded 1, so the job's exit status and the rc= line
  # in the sentinel are the same number. 3 = criteria decided against the run, 1 = gate could not be
  # evaluated; collapsing both to 1 would destroy exactly the distinction the sentinel exists for.
  echo "[powered][FAIL] preflight rc=${pf_rc} (${pf_verdict}); the predeclared criteria are already" \
       "decided and no amount of training moves them -- not spending the GPU hours." \
       "Receipt: ${PREFLIGHT_RECEIPT}" >&2
  exit $pf_rc
fi
echo "[powered] preflight PASS -- allocating the training"

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

# ---- post-run cross-check: keep the gate honest -----------------------------------------------
# The preflight reproduces two lines of build_fullevent_loaders (the seeded `imc` draw) rather than
# calling it, because calling it costs TensorFlow and both decompressed point clouds -- the whole
# cost the gate exists to avoid -- and it cannot be factored into a shared helper either, since
# fullevent_fps_dataloader.py is hash-pinned by the Gate-2 runtime receipt. An unavoidable
# duplication has to be MEASURED, so: the driver computed gap and floor over the rows it actually
# trained on, and those two numbers must agree with the gate's. If they do not, the gate was
# grading a different sample than the run used, and its PASS meant nothing.
xcheck="not-run"
if [[ -f "$REPORT" && -f "$PREFLIGHT_RECEIPT" ]]; then
  set +e
  python3 - "$PREFLIGHT_RECEIPT" "$REPORT" "$PREFLIGHT_XCHECK_RTOL" <<'PY'
import json, sys
pf, rep, rtol = json.load(open(sys.argv[1])), json.load(open(sys.argv[2])), float(sys.argv[3])
bad = []
for k in ("gap", "floor"):
    a, b = pf["metrics"].get(k), rep.get("metrics", {}).get(k)
    if a is None or b is None:
        bad.append(f"{k}: preflight={a!r} report={b!r} (missing)")
        continue
    d = abs(a - b) / max(abs(b), 1e-30)
    print(f"[xcheck] {k}: preflight={a:.8f} driver={b:.8f} rel={d:.2e} "
          f"{'ok' if d <= rtol else 'DIVERGED'}")
    if d > rtol:
        bad.append(f"{k}: rel {d:.2e} > rtol {rtol:.0e}")
if bad:
    print("[xcheck][FAIL] the preflight graded a different sample than the run trained on: "
          + "; ".join(bad), file=sys.stderr)
    raise SystemExit(4)
print("[xcheck] preflight and driver agree; the gate measured the run that happened")
PY
  xrc=$?
  set -e
  xcheck=$([[ $xrc -eq 0 ]] && echo "AGREE" || echo "DIVERGED")
  # A divergence invalidates the gate, not just the cross-check, so it must not be reported as a
  # clean PASS. It overrides rc only when the driver itself did not already fail.
  if [[ $xrc -ne 0 && $rc -eq 0 ]]; then
    rc=$xrc
  fi
fi

if [[ -f "$REPORT" ]]; then
  verdict="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("verdict","<none>"))' "$REPORT")"
  [[ "$xcheck" == "DIVERGED" ]] && verdict="${verdict}_XCHECK_DIVERGED"
else
  verdict="NO_REPORT_rc=${rc}"
fi
write_sentinel "$rc" "$verdict"
exit $rc
