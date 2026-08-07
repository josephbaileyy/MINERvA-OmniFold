#!/bin/bash
#SBATCH --job-name=pwcprobe
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=11:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/powered_closure/underfit_probe/logs/pwcprobe_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/powered_closure/underfit_probe/logs/pwcprobe_%j.err
#
# D2 UNDER-FITTING PROBE -- a DIAGNOSTIC, not a gate run. Read this header before reading the code.
#
# WHAT QUESTION THIS ANSWERS. Job 56381674 measured powered-closure recovery 0.5469 at the nominal
# configuration (niter=3, epochs=8). The predeclared bar is 0.80, but the tilt-weighted per-cell
# ceiling is 0.6332 at k=3 (FINDING-20260806-niter4-decision.md 2a/2), so the bar is ~17 pp above
# achievable and NO iteration count reaches it. The open question is therefore NOT the gate: it is
# the 19% shortfall between the measured 0.5469 and that 0.6332 ceiling. Two sessions independently
# guessed UNDER-FITTING and neither tested it. This launcher tests it.
#
# THIS RUN CANNOT PASS GATE-4 AND MUST NOT BE READ AS IF IT COULD. Every arm except the control
# trains at a non-nominal budget, so the driver stamps `is_nominal_configuration: false` and
# `configuration.epochs` records what actually ran. validate_pet_nominal_gate4's
# `powered:nominal_configuration` check compares those five keys against FROZEN["seed_policy"] and
# will FAIL on a probe report -- deliberately. Three further guards keep the two apart: the products
# land in `powered_closure/underfit_probe/` and not in the gate's directory, the report basename is
# POWERED_CLOSURE_PROBE_REPORT and not POWERED_CLOSURE_REPORT, and the sentinel names the arm.
# The gate validator takes an explicit --powered-closure-report path (never a glob), so nothing
# discovers these by accident; the separation is belt-and-braces on top of that.
#
# WHY THE PREFLIGHT STILL RUNS. `gap` and `floor` are deterministic in the dump plus two seeds and do
# not depend on the training budget at all, so the preflight's verdict is known before the run. It
# runs anyway because its POST-RUN CROSS-CHECK is the only thing that proves this probe trained on
# the SAME 2M/2M population the gate run graded. Without that, a probe that moved recovery would be
# indistinguishable from a probe that quietly changed the sample. The cross-check is the control.
#
# ONE FILE, THREE ARMS, ON PURPOSE. The repo convention is one sbatch per campaign step, and 115 such
# names are load-bearing provenance -- but three near-identical copies differing in two integers is
# three files to review and three places for a protocol constant to drift. The arm is therefore an
# ENV parameter that FAILS CLOSED when unset (below), and the arm name is carried into the run id,
# the products and the sentinel, so provenance is recovered from the artifacts rather than the
# filename. Note the distinction the repo cares about: an env var that SKIPS a gate is the vacuous
# pass this campaign keeps finding, and there is none here. An env var that must be SET, is recorded
# in the product, and cannot weaken any check, is a parameter.
#
# THE ARMS. Sized from the run being sized, not from a note about another run (BEN-030): the six
# training histories of 56381674 (weights.slurm-56381674/*.pkl mtimes) give 2.00 min/epoch for step 1
# and 2.79 min/epoch for step 2, so one epoch across all niter=3 x 2 trainings costs 14.4 min, and
# the measured 8-epoch total of 115 min reproduces the job's 1h58m with ~5 min of load and hashing.
#
#   ctl8   epochs=8,  early_stop default -- the CONTROL. Re-runs the baseline configuration exactly.
#          There is NO published run-to-run spread for this closure and `tf.keras.utils.set_random_seed`
#          does not enable op determinism, so without this arm a 1-2 pp move elsewhere is
#          uninterpretable. It doubles as the first independent reproduction of the published 0.5469,
#          AND as the regression test for the --epochs flag this campaign added: 8 equals the policy
#          value, so a correct implementation must stamp `is_nominal_configuration: true` and an empty
#          `configuration_overrides` on this arm's report.   ~2h, 4h wall.
#   ep16   epochs=16, early_stop=1000 -- 2x budget.   ~4h, 7h wall.
#   ep32   epochs=32, early_stop=1000 -- 4x budget.   ~8h, 11h wall.
#
# A three-point LADDER (8/16/32) under ONE selection rule, not two points and a mechanism change. A
# flat curve across three budgets is a trend; two points that agree are a coincidence you have to
# argue about. `early_stop=1000` on the probe arms guarantees the full budget is actually spent, so
# the ladder varies exactly one thing.
#
# WHY THERE IS NO SEPARATE EARLY-STOPPING ARM, having nearly built one. The obvious fourth arm is
# "epochs=32 at the default patience=10, so restore_best_weights can finally operate" -- the baseline
# provably could NOT restore best weights, because patience 10 cannot fire inside 8 epochs, while its
# val-loss argmin sat at epoch {5,5,7,1,6,5} of 8. Two things killed it. (1) Keras 2.15's
# EarlyStopping restores the best weights ONLY inside the `wait >= patience` stop branch --
# `on_train_end` merely prints -- so an arm that never triggers silently becomes a second, redundant
# copy of ep32 at a cost of ~8 GPU-hours. With a val curve this flat and noisy, a fresh minimum by
# chance every few epochs makes never-triggering the likely outcome. (2) The question is answerable
# for FREE from ep32's own history pickles: if the 32-epoch val curve is flat with an early argmin,
# best-versus-last selection is provably inside the validation noise and no arm was needed. Reading
# what a training already persisted, instead of buying another one, is BEN-037 -- which this campaign
# filed after two sessions queued a GPU probe without opening the six histories the FIRST run wrote.
#
# ReduceLROnPlateau is configured at patience=1000 (omnifold.py:263-265) and get_optimizer returns a bare
# Adam at a flat LR (omnifold.py:376-380, num_steps accepted and unused), so LR is pinned at 1e-4 for
# every arm and "more budget" here means strictly more steps at fixed LR. That is a real limitation
# of what this probe can conclude and it is stated in the finding rather than hidden here.
#
# set -u intentionally omitted (module/conda hooks abort under nounset -- AGENTS.md).
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DRIVER="${REPO}/nd-unfolding/pet/closure_powered_truth_reweight.py"
PREFLIGHT="${REPO}/nd-unfolding/pet/preflight_powered_closure.py"
INPUTS="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
PRODUCER="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12_RECEIPT.json"

# ---- immutable bound footing -------------------------------------------------------------------
# Same discipline as sbatch_powered_closure.sh: the driver and gate shas are pinned AT SUBMISSION, so
# editing either between sbatch and dispatch kills the job instead of silently running other code.
# Both are written in the one-line `[[ "$(sha_of "$VAR")" == "$EXPECTED_..." ]]` idiom because that is
# the only form docs/orchestration/verify_hash_bindings.py's collect_shell can discover; these two
# pins are why SHELL_PIN_FLOOR moves 13 -> 15 in the same commit that adds this file.
EXPECTED_DRIVER_SHA="a45fae7c3f978c34bf73f35ab56aac668439c5784a3968b4f09799ee6090fd48"
EXPECTED_PREFLIGHT_SHA="dee9aa20a49a89eb5553a4f75672cfde5e9ce05df8f4c9ae00095c549e5ce9bb"
EXPECTED_INPUTS_SHA="fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
EXPECTED_INPUTS_SIZE="9897374636"
EXPECTED_PRODUCER_SHA="d466a0c18deaafa2ae645002c8dbc9b9879476adb45a40a85c0bae9e0129d25e"

# Kept in the two-line, deliberately NON-discoverable form, exactly as the gate launcher explains:
# making a 9.9 GB pin verifier-visible adds a second full-file sha256 to every verify_hash_bindings.py
# run and therefore to every `pytest test_hash_bindings.py`. The identical digest is already walked
# from run_gate2_target_validator.sh's EXPECTED_INPUT_SHA.

PREFLIGHT_XCHECK_RTOL="1e-4"

# ---- arm parameters: must be SET, are recorded, and can weaken nothing --------------------------
fail() { echo "[probe][FAIL] $*" >&2; exit 1; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }

[[ -n "${SLURM_JOB_ID:-}" ]] || fail "must run under sbatch (SLURM_JOB_ID unset)"
[[ -n "${PROBE_ARM:-}" ]] || fail "PROBE_ARM is unset; an unlabelled probe product is one nobody can attribute"
[[ -n "${PROBE_EPOCHS:-}" ]] || fail "PROBE_EPOCHS is unset; this launcher exists to vary the training budget explicitly"
[[ "$PROBE_ARM" =~ ^[A-Za-z0-9_]+$ ]] || fail "PROBE_ARM must be [A-Za-z0-9_]+ (it becomes a filename): '${PROBE_ARM}'"
[[ "$PROBE_EPOCHS" =~ ^[0-9]+$ && "$PROBE_EPOCHS" -ge 1 ]] || fail "PROBE_EPOCHS must be a positive integer: '${PROBE_EPOCHS}'"
if [[ -n "${PROBE_EARLY_STOP:-}" ]]; then
  [[ "$PROBE_EARLY_STOP" =~ ^[0-9]+$ && "$PROBE_EARLY_STOP" -ge 1 ]] || \
    fail "PROBE_EARLY_STOP must be a positive integer when set: '${PROBE_EARLY_STOP}'"
fi
# niter is NOT varied by this campaign -- FINDING-20260806-niter4-decision.md settles it at 3 and the
# ceiling analysis already covers every k. The knob exists so the driver's default path is exercised
# and so a future k-probe does not need a fourth launcher; leaving it unset uses the policy value.
if [[ -n "${PROBE_NITER:-}" ]]; then
  [[ "$PROBE_NITER" =~ ^[0-9]+$ && "$PROBE_NITER" -ge 1 ]] || \
    fail "PROBE_NITER must be a positive integer when set: '${PROBE_NITER}'"
fi

OUTDIR="${REPO}/nd-unfolding/pet/powered_closure/underfit_probe"
LOG_DIR="${OUTDIR}/logs"
RUN_ID="${PROBE_RUN_ID:-probe-${PROBE_ARM}-slurm-${SLURM_JOB_ID}}"
REPORT="${OUTDIR}/POWERED_CLOSURE_PROBE_REPORT.${RUN_ID}.json"
ARTIFACT="${OUTDIR}/POWERED_CLOSURE_PROBE_ARTIFACT.${RUN_ID}.npz"
PREFLIGHT_RECEIPT="${OUTDIR}/POWERED_PROBE_PREFLIGHT.${RUN_ID}.json"
WEIGHTS="${OUTDIR}/weights.${RUN_ID}"

mkdir -p "$LOG_DIR" "$WEIGHTS"

write_sentinel() {   # $1 = rc, $2 = verdict
  {
    echo "run_id=${RUN_ID}"
    echo "job=${SLURM_JOB_ID}"
    echo "arm=${PROBE_ARM}"
    echo "epochs=${PROBE_EPOCHS}"
    echo "early_stop=${PROBE_EARLY_STOP:-<multifold-default>}"
    echo "niter=${PROBE_NITER:-<nominal-policy>}"
    echo "diagnostic_only=true"
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
  echo "[probe] $2 sentinel=${OUTDIR}/DONE.${RUN_ID}.txt"
}

[[ -f "$DRIVER" ]] || fail "driver missing: $DRIVER"
[[ "$(sha_of "$DRIVER")" == "$EXPECTED_DRIVER_SHA" ]] || \
  fail "driver changed after submission (want $EXPECTED_DRIVER_SHA)"

[[ -f "$PREFLIGHT" ]] || fail "preflight gate missing: $PREFLIGHT"
[[ "$(sha_of "$PREFLIGHT")" == "$EXPECTED_PREFLIGHT_SHA" ]] || \
  fail "preflight gate changed after submission (want $EXPECTED_PREFLIGHT_SHA)"

[[ -f "$INPUTS" ]] || fail "inputs missing: $INPUTS"
sz="$(stat -c %s "$INPUTS")"
[[ "$sz" == "$EXPECTED_INPUTS_SIZE" ]] || fail "inputs size drift: want $EXPECTED_INPUTS_SIZE got $sz"

echo "[probe] hashing inputs (9.9 GB, ~1 min) ..."
gs="$(sha_of "$INPUTS")"
[[ "$gs" == "$EXPECTED_INPUTS_SHA" ]] || fail "inputs sha drift: want $EXPECTED_INPUTS_SHA got $gs"
gp="$(sha_of "$PRODUCER")"
[[ "$gp" == "$EXPECTED_PRODUCER_SHA" ]] || fail "producer sha drift: want $EXPECTED_PRODUCER_SHA got $gp"

module load tensorflow/2.15.0

cd "$REPO"
echo "[probe] route=batch DIAGNOSTIC arm=${PROBE_ARM} run_id=${RUN_ID} host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[probe] budget: epochs=${PROBE_EPOCHS} early_stop=${PROBE_EARLY_STOP:-<multifold-default>} niter=${PROBE_NITER:-<nominal-policy>}"
echo "[probe] driver=${EXPECTED_DRIVER_SHA} inputs=${EXPECTED_INPUTS_SHA}"
echo "[probe] preflight=${EXPECTED_PREFLIGHT_SHA}"
echo "[probe] HEAD=$(git rev-parse --short HEAD) dirty=$(git status --porcelain --untracked-files=no | wc -l)"
echo "[probe] THIS IS NOT A GATE RUN. Gate-4's powered:nominal_configuration check fails on it by design."

echo "[probe] preflight: training-independent criteria (gap/floor do not depend on the budget) ..."
set +e
python3 -u "$PREFLIGHT" --inputs "$INPUTS" --json "$PREFLIGHT_RECEIPT" --inputs-sha256 "$gs"
pf_rc=$?
set -e
if [[ -f "$PREFLIGHT_RECEIPT" ]]; then
  pf_verdict="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("verdict","<none>"))' "$PREFLIGHT_RECEIPT")"
else
  pf_verdict="NO_RECEIPT_rc=${pf_rc}"
fi
if [[ $pf_rc -ne 0 ]]; then
  write_sentinel "$pf_rc" "PREFLIGHT_${pf_verdict}"
  echo "[probe][FAIL] preflight rc=${pf_rc} (${pf_verdict}); gap/floor are budget-independent, so a" \
       "preflight failure here means the SAMPLE moved and the probe would be measuring the wrong" \
       "thing. Receipt: ${PREFLIGHT_RECEIPT}" >&2
  exit $pf_rc
fi
echo "[probe] preflight PASS -- allocating the training"

# python3 -u: BEN-026 + BEN-028. st_blksize on this Lustre is 4 MiB, so a buffered driver emits its
# per-epoch lines only at exit and a 8-hour arm looks dead for 8 hours. Unbuffered is the whole point
# for an arm whose per-epoch progress is the measurement.
BUDGET_ARGS=(--epochs "$PROBE_EPOCHS")
[[ -n "${PROBE_EARLY_STOP:-}" ]] && BUDGET_ARGS+=(--early-stop "$PROBE_EARLY_STOP")
[[ -n "${PROBE_NITER:-}" ]] && BUDGET_ARGS+=(--niter "$PROBE_NITER")

set +e
srun -n 1 -c 32 --gpus=1 python3 -u "$DRIVER" \
  --inputs "$INPUTS" \
  --producer-receipt "$PRODUCER" \
  --json "$REPORT" \
  --artifact "$ARTIFACT" \
  --weights-folder "$WEIGHTS" \
  "${BUDGET_ARGS[@]}"
rc=$?
set -e

echo "[probe] driver exit=${rc} end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# The cross-check is load-bearing HERE in a way it is not in the gate launcher: it is the evidence
# that this arm and job 56381674 graded the same 2M/2M population, which is the premise of comparing
# their recoveries at all.
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
    print("[xcheck][FAIL] the probe trained on a different sample than the gate run graded: "
          + "; ".join(bad), file=sys.stderr)
    raise SystemExit(4)
print("[xcheck] preflight and driver agree; this arm and 56381674 measured the same population")
PY
  xrc=$?
  set -e
  xcheck=$([[ $xrc -eq 0 ]] && echo "AGREE" || echo "DIVERGED")
  if [[ $xrc -ne 0 && $rc -eq 0 ]]; then
    rc=$xrc
  fi
fi

# The driver returns 3 on a FAIL verdict, and EVERY arm here is expected to return 3: the 0.80 bar is
# ~17 pp above the 0.6332 achievable ceiling, so a PASS would be the surprising outcome and a
# non-event is the predicted one. The sentinel therefore records the RECOVERY, which is the actual
# measurement, alongside the verdict -- reading rc alone would throw away the entire result.
if [[ -f "$REPORT" ]]; then
  verdict="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("verdict","<none>"))' "$REPORT")"
  recovery="$(python3 -c 'import json,sys;m=json.load(open(sys.argv[1])).get("metrics",{});print(m.get("recovery"))' "$REPORT")"
  echo "[probe] arm=${PROBE_ARM} epochs=${PROBE_EPOCHS} recovery=${recovery} verdict=${verdict}"
  [[ "$xcheck" == "DIVERGED" ]] && verdict="${verdict}_XCHECK_DIVERGED"
  verdict="${verdict}_recovery=${recovery}"
else
  verdict="NO_REPORT_rc=${rc}"
fi
write_sentinel "$rc" "$verdict"

# Exit 0 when the measurement succeeded. This is the one place this launcher deliberately differs
# from the gate launcher: there, rc=3 means "the predeclared criterion was not met" and must
# propagate. Here rc=3 is the EXPECTED outcome of a diagnostic whose job was to produce a number, so
# propagating it would mark a successful measurement as a failed job and make `afterok` chaining
# impossible. A missing report, a preflight failure or a diverged cross-check still exit non-zero.
if [[ ! -f "$REPORT" ]]; then exit "${rc:-1}"; fi
if [[ "$xcheck" == "DIVERGED" ]]; then exit 4; fi
if [[ $rc -ne 0 && $rc -ne 3 ]]; then exit $rc; fi
exit 0
