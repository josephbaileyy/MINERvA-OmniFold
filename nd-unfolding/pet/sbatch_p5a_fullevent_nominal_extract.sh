#!/bin/bash
#SBATCH --job-name=p5a_ann_extract
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_nominal_annealed_extraction_unpromoted/logs/p5a_ann_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_nominal_annealed_extraction_unpromoted/logs/p5a_ann_%j.err
#
# P5A NOMINAL EXTRACTION ON THE ANNEALED ARM.  Authorized 2026-08-14, Joseph verbatim
# "Yes I authorize it", relayed by the mediator; sequencing and the two conditions below are the
# mediator's.  Lane C (PET).
#
# WRITTEN FRESH, NOT COPIED.  sbatch_fullevent_diagnostic_extract.sh:42 hardcodes
#   WEIGHTS="${PET}/fullevent_nominal/pet_fullevent_nominal_weights.npz"
# which is the PRE-ANNEAL directory, and its weights are gated on EXISTENCE only (:56-57) while its
# INPUTS are gated on IDENTITY (:41, :65-66).  The promoted artifact has an IDENTICAL FILENAME in a
# SIBLING directory and both are on disk, so an extraction against the retired arm is fully
# self-consistent and passes every gate there.  Copying that launcher is precisely how :42
# propagates, so this file was authored rather than derived.  leg_mismatch.py:30 is a third instance
# of the same hardcoded path.  Mechanism credited to the assistant lane.
#
# CONDITION 1 -- THE OUTPUT IS NOT THE CANONICAL P5A CENTRAL AND CANNOT BECOME IT SILENTLY.
# Extraction is authorized; promoting its product to the frozen central vector and reported-bin
# mask that RUNBOOK:213 binds every P5B component to is a SEPARATE step and a SEPARATE decision.
# Enforced three ways, not asserted once:
#   * outputs land in fullevent_nominal_annealed_extraction_unpromoted/, never in the artifact's own
#     directory, and this script REFUSES to write into fullevent_nominal_annealed/ (G5);
#   * every filename carries MARK=P5A-ANNEALED-UNPROMOTED;
#   * the run ends by writing NOT_CANONICAL.json stating what promotion would require.
# A later promotion act may adopt these products.  Nothing here performs it.
#
# WHY THIS RUN IS BETTER FOUNDED THAN THE DIAGNOSTIC, stated so the two are not confused.  The
# diagnostic's own header records a reco-weighted push mean of 0.736746 against R = 1.124080 -- a
# ~34% low cross section.  The annealed production arm sits at push 1.0840529523112135, i.e.
# abs_dev 0.035609 against the frozen fold_forward_ratio_dev_max of 0.05
# (state/annealed-nominal-complete-56563761.json).  That is inside tolerance rather than 34% out.
#
# WHAT THAT NUMBER STRUCTURALLY CANNOT EXPRESS -- read this before quoting it.  0.035609 is an
# INTEGRATED SCALAR.  pet_diagnostic_quarantine.py:104-120 forms it as
#   dev = |(fold_forward_sum_w_push_reco / fold_forward_sum_w_reco) / R - 1|
# from two sums already taken over the WHOLE reco leg, so the shape information is integrated away
# BEFORE the ratio exists.  A quantity of that construction cannot distinguish a uniform scale
# offset from a shape distortion with the same integral -- which is why lane D had to decompose
# per-event pieces to answer the question at all (D, 2026-08-14, f4267b4).  D's arithmetic
# reproduces exactly and is about the PRE-ANNEAL nominal run -- SCOPE CORRECTION below.  0.035609
# still bounds only the integral and says nothing about the grid.  This is not a label asking to
# be honoured -- it is what the arithmetic can and cannot support.
#
# SCOPE, CORRECTED 2026-08-15.  THE PHYSICS GROUND IS MIS-TARGETED, NOT FALSIFIED, and the fault
# is in the RECORD: the closure's own quarantine manifest carries job_id 56552326 while its
# weights_path/weights_sha256 name the PRE-ANNEAL fullevent_nominal/ file, and computes its
# fold_forward block and rejection_reason from it -- so D read exactly the artifact the manifest
# names as the source of its own rejection.  The "ONE of FOUR quotability grounds, other three
# hygiene and unexamined" scope note was a COUNT WITH NO MEMBERS -- do not repeat it; there are
# three, two are one ground, G1-G3 are determined and only G4 remains.  Grounds:
# FINDING-20260815-the-quarantine-measured-a-different-run.md.  Operands:
# state/RECEIPT-vl100-shape-corrected-foldforward-20260815.json.  BEN-310/311/312/313.
#
# ---------------------------------------------------------------------------------------------
# REPAIR 2026-08-14 AFTER JOB 56978466 FAILED 6:0 AT 00:12:57.  Recorded here because the failure
# was NOT a physics or identity failure and the next reader must not go looking for one.
#
# ALL SIX GUARDS G0-G5 PASSED: right arm, right weights sha, right inputs sha.  The expensive work
# also SUCCEEDED -- the full-inventory reweight ran to 100% over 49,152,885 rows, wrote its push
# payload, and its subsample-agreement check passed at max_rel_dev 2.554037696012494e-05 against a
# tolerance of 1e-3.  The run then died, from the .err:
#
#   extract_fullevent_fps.py:463   import unfold_2d_omnifold_unbinned as u2d
#   2d-unfolding/unfold_2d_omnifold_unbinned.py:21   import ROOT
#   ModuleNotFoundError: No module named 'ROOT'
#
# THE CAUSE IS AN INTERPRETER CHOICE, and this file's own driver already documents it.
# extract_fullevent_fps.py:16-19 states the two stages need DIFFERENT interpreters -- `push` "needs
# TensorFlow, wants a GPU", `xsec` "needs ROOT and numpy, no TensorFlow, no GPU" -- and :21-23 says
# they are split "because the push pass costs GPU time that must not be re-spent".  This launcher
# ran `--stage all` under `module load tensorflow/2.15.0`, which carries no ROOT, so it spent the
# GPU time and THEN discovered it could not finish.  There is a standing decision in this repo that
# no combined ROOT/TF environment exists, so the split is the only available shape.
#
# THE REPAIR IS THE TWO-ENVIRONMENT SPLIT PROVEN AT 50/50 by sbatch_gate5_replica_extract_array.sh
# (read as a template only; that file is hash-bound by an active receipt and is NOT edited here):
# TF python for `--stage push`, the root_6_28 prefix python for `--stage xsec`, and a ROOT import
# preflight before any long work.  Two things this file adds beyond that template, both because
# 56978466 taught them:
#
#   * THE PREFLIGHT RUNS BEFORE THE PUSH STAGE, NOT BETWEEN THE STAGES (G7).  Ordering it after the
#     reweight is what made this a 13-minute failure instead of a 5-second one.  That is the whole
#     generalisable lesson and it is a guard, not a comment.
#   * `$ROOT_PY -c 'import ROOT'` IS NOT SUFFICIENT ON ITS OWN.  Measured 2026-08-14 on a login
#     node: invoking that interpreter directly SEGFAULTS (rc=139, cling "cannot extract standard
#     library include paths") unless setup_salloc_env.sh has activated the env by full prefix
#     first.  A preflight written the naive way would pass in an salloc and crash in batch, or vice
#     versa.  So the preflight runs through the SAME env helper the real xsec stage uses, which is
#     what makes it a test of the real thing rather than a lookalike.
#
# THE PUSH PAYLOAD IS REUSED, NOT RECOMPUTED (G6).  13 minutes of A100 is already on disk and the
# payload has been re-validated independently.  Reuse is gated on identity, never on existence --
# see G6 for why that distinction is load-bearing here.
#
# USAGE
#   bash sbatch_p5a_fullevent_nominal_extract.sh --check-only   # run G0..G7 and exit; no job, no GPU
#   sbatch sbatch_p5a_fullevent_nominal_extract.sh              # full run: push on GPU, then xsec
#
#   # consume 56978466's surviving push payload instead of re-spending the GPU:
#   P5A_PUSH_REUSE=<path to the .push npz> sbatch sbatch_p5a_fullevent_nominal_extract.sh
#   # ...which needs no GPU at all, so that submission should also override the resource request.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PET="${REPO}/nd-unfolding/pet"

MARK="P5A-ANNEALED-UNPROMOTED"
ARM_DIR="${PET}/fullevent_nominal_annealed"
OUTDIR="${PET}/fullevent_nominal_annealed_extraction_unpromoted"

INPUTS="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
EXPECTED_INPUTS_SHA="fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"

WEIGHTS="${ARM_DIR}/pet_fullevent_nominal_weights.npz"
# Computed 2026-08-14 on two independent instruments (sha256sum, and python hashlib over 1 MiB
# blocks) from the promoted artifact itself.  NOT copied from any other launcher:
# sbatch_finalize_annealed_shape_validation.sh:69 pins 58f664cd..., which is CORRECT there because
# that script validates the annealed candidate AGAINST the pre-anneal baseline -- a correct line
# that is dangerous to copy out of context.
EXPECTED_WEIGHTS_SHA="559a1020570929169a83e26dd9eea937bb34d6f4ecb230e332b792165ef6eb3e"

# Explicit DATA-root flux ROOT.  Never rely on the driver's default: an immutable code worktree must
# not be mistakable for the off-repo data root (the Gate-5 r1 failure was exactly this binding).
MCFILE="${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
FLUX_HIST="pTmu_reweightedflux_integrated"

CHECK_ONLY=0
[[ "${1:-}" == "--check-only" ]] && CHECK_ONLY=1

die() { echo "[p5a] FATAL: $*" >&2; exit "${2:-2}"; }

mkdir -p "${OUTDIR}/logs"

# ---------------------------------------------------------------------------------------------
# G0  existence.  Necessary, and on its own worth nothing -- it is what the diagnostic launcher
#     applies to its weights, and it is why a wrong-arm run there is invisible.
# ---------------------------------------------------------------------------------------------
for f in "$INPUTS" "$WEIGHTS" "$MCFILE"; do
  [[ -s "$f" ]] || die "missing or empty: $f" 2
done

# ---------------------------------------------------------------------------------------------
# G1  THE PRIMARY GUARD -- ARM IDENTITY BY SCHEMA, not by path and not by digest.
#     The pre-anneal artifact has NO lr_policy key at all, so this fails LOUDLY on the wrong arm
#     rather than comparing two unequal values.  It catches a wrong arm whatever the path, and it
#     survives a legitimate digest change, which the sha pin does not.  Leads deliberately.
# ---------------------------------------------------------------------------------------------
echo "[p5a] G1 arm-schema assertion on $(basename "$WEIGHTS")"
module load tensorflow/2.15.0 >/dev/null 2>&1 || module load python >/dev/null 2>&1 || true
python3 - "$WEIGHTS" "$ARM_DIR" <<'PY' || die "G1/G2 arm assertion failed" 3
import json, os, sys
import numpy as np

weights, arm_dir = sys.argv[1], os.path.realpath(sys.argv[2])
with np.load(weights, allow_pickle=True) as z:
    if "seed_policy" not in z.files:
        sys.exit("[p5a] G1: artifact carries no seed_policy at all -- not a nominal weights npz")
    sp = np.asarray(z["seed_policy"], dtype=object).item()
    ic = np.asarray(z["inference_contract"], dtype=object).item() \
        if "inference_contract" in z.files else {}

# G1 -- the schema discriminator.
lr = sp.get("lr_policy")
if lr is None:
    sys.exit("[p5a] G1: seed_policy has NO lr_policy key. This is the PRE-ANNEAL arm. "
             "The promoted arm is fullevent_nominal_annealed/. Refusing.")
got = lr.get("schedule")
want = "fit-time-anneal-after-iteration-0"
if got != want:
    sys.exit(f"[p5a] G1: lr_policy.schedule is {got!r}, expected {want!r}. Refusing.")
print(f"[p5a] G1 PASS  lr_policy.schedule = {got}")
print(f"[p5a] G1 also  base_lr={lr.get('base_lr')} annealed_lr={lr.get('annealed_lr')} "
      f"applies_from_iteration={lr.get('applies_from_iteration')}")

# G2 -- the contract's checkpoint must resolve UNDER the promoted arm's directory.  realpath on
# both sides so a symlink or a .. cannot walk out of the arm while still passing a prefix test.
ckpt = ic.get("step2_checkpoint")
if not ckpt:
    sys.exit("[p5a] G2: inference_contract names no step2_checkpoint")
real = os.path.realpath(ckpt)
if not (real == arm_dir or real.startswith(arm_dir + os.sep)):
    sys.exit(f"[p5a] G2: step2_checkpoint resolves OUTSIDE the promoted arm.\n"
             f"        checkpoint: {real}\n        arm dir   : {arm_dir}\nRefusing.")
if not os.path.isfile(real):
    sys.exit(f"[p5a] G2: step2_checkpoint does not exist: {real}")
print(f"[p5a] G2 PASS  step2_checkpoint resolves under the promoted arm")
PY

# ---------------------------------------------------------------------------------------------
# G3  weights IDENTITY, gated the way INPUTS already are.  This is the asymmetry the diagnostic
#     launcher leaves open, closed here without touching extract_fullevent_fps.py -- which has no
#     --expected argument of any kind (the name:path:sha interface lives only in
#     finalize_annealed_shape_validation.py:115).
# ---------------------------------------------------------------------------------------------
GOT_W="$(sha256sum "$WEIGHTS" | awk '{print $1}')"
[[ "$GOT_W" == "$EXPECTED_WEIGHTS_SHA" ]] \
  || die "weights sha mismatch: $GOT_W != $EXPECTED_WEIGHTS_SHA" 3
echo "[p5a] G3 PASS  weights sha256 = $GOT_W"

# ---------------------------------------------------------------------------------------------
# G4  inputs identity.  Unchanged from the diagnostic launcher, which had this half right.
# ---------------------------------------------------------------------------------------------
GOT_I="$(sha256sum "$INPUTS" | awk '{print $1}')"
[[ "$GOT_I" == "$EXPECTED_INPUTS_SHA" ]] \
  || die "inputs sha mismatch: $GOT_I != $EXPECTED_INPUTS_SHA" 3
echo "[p5a] G4 PASS  inputs sha256 = $GOT_I"

# ---------------------------------------------------------------------------------------------
# G5  CONDITION 1, enforced rather than documented: refuse to write into the artifact's own
#     directory, so this run cannot be mistaken for -- or quietly become -- the canonical P5A
#     central and mask.
# ---------------------------------------------------------------------------------------------
case "$(realpath -m "$OUTDIR")" in
  "$(realpath -m "$ARM_DIR")"|"$(realpath -m "$ARM_DIR")"/*)
    die "OUTDIR is inside the promoted arm's directory; promotion must be a separate act" 5 ;;
esac
echo "[p5a] G5 PASS  outputs are outside the promoted arm: ${OUTDIR}"

# =============================================================================================
# G6 and G7 are the 56978466 repair.  They are APPENDED, deliberately: G0-G5 are unchanged, in
# their original order, with their original numbering and text.  They all passed and none of them
# is what failed, so none of them is touched.
# =============================================================================================

# ---------------------------------------------------------------------------------------------
# G6  PUSH REUSE BY IDENTITY, NEVER BY EXISTENCE.  56978466's push stage completed and its payload
#     survives on disk, so the GPU reweight is reusable.  But adopting a push by PATH is exactly
#     the failure BEN-023 records -- `[[ -s $OUT ]] && skip` let 7 partial slabs permanently block
#     their own repair -- and a push payload is worse than a slab, because a partial or wrong-arm
#     one produces a complete-looking cross section with nothing downstream able to notice.
#
#     So reuse is gated on FOUR independent facts, not on the file being there:
#       * a regular non-empty file, not a symlink;
#       * a non-empty `.done` marker beside it (atomic_write's completeness signal -- absence of
#         the marker means PARTIAL, which is the case existence-testing cannot see);
#       * a sha256 PIN, so a different payload cannot be substituted silently;
#       * the driver's own schema, fingerprint, inputs-identity and coverage validators (the driver
#         re-validates coverage itself when it reads the payload, so this is a second independent
#         instrument rather than a replacement for one).
#
#     Reuse is EXPLICIT and opt-in.  The push filename embeds the Slurm JOB id, so a fresh job
#     cannot discover a previous job's payload by accident -- which is a property worth keeping.
# ---------------------------------------------------------------------------------------------
PUSH_REUSE="${P5A_PUSH_REUSE:-}"
# sha256 of 56978466's surviving payload, measured 2026-08-14 on the file itself (sha256sum, and
# re-derived through numpy by loading it and recomputing w_push min/max/mean against the telemetry
# the run printed).  Override only with a payload whose provenance you have established the same way.
EXPECTED_PUSH_SHA="${P5A_EXPECTED_PUSH_SHA:-a1debdb7105f3e531ec2e6ec5e08192d026238d5bac7eb5fe389e7e8f71bb9c9}"
REUSE_PUSH=0
if [[ -n "$PUSH_REUSE" ]]; then
  [[ -f "$PUSH_REUSE" && ! -L "$PUSH_REUSE" && -s "$PUSH_REUSE" ]] \
    || die "G6: P5A_PUSH_REUSE is missing, empty, or a symlink: $PUSH_REUSE" 7
  [[ -s "${PUSH_REUSE}.done" && ! -L "${PUSH_REUSE}.done" ]] \
    || die "G6: push payload carries no non-empty .done marker, so it must be treated as PARTIAL: ${PUSH_REUSE}.done" 7
  GOT_P="$(sha256sum "$PUSH_REUSE" | awk '{print $1}')"
  [[ "$GOT_P" == "$EXPECTED_PUSH_SHA" ]] \
    || die "G6: push payload sha mismatch: $GOT_P != $EXPECTED_PUSH_SHA" 7
  python3 - "$PUSH_REUSE" "$INPUTS" "$EXPECTED_INPUTS_SHA" "$PET" <<'PY' || die "G6 push payload validation failed" 7
import os, sys
import numpy as np

push, inputs, expected_inputs_sha, pet = sys.argv[1:5]
sys.path.insert(0, pet)
import extract_fullevent_fps as E
with np.load(push, allow_pickle=True) as z:
    schema = str(np.asarray(z["push_schema"]))
    if schema != E.PUSH_SCHEMA:
        sys.exit(f"[p5a] G6: push payload schema is {schema!r}, expected {E.PUSH_SCHEMA!r}")
    fp = str(np.asarray(z["estimator_fingerprint"]))
    if fp != E.ESTIMATOR_FINGERPRINT:
        sys.exit(f"[p5a] G6: estimator fingerprint is {fp!r}, expected {E.ESTIMATOR_FINGERPRINT!r}")
    w = np.asarray(z["w_push"], np.float64)
    mi = np.asarray(z["mc_indices"])
    got_inputs_sha = str(np.asarray(z["inputs_sha256"]))
    src_w = str(np.asarray(z["source_weights"]))
    agree = np.asarray(z["subsample_agreement"], dtype=object).item()

# The payload must have been built from the SAME inputs this run is gated on (G4).  Without this,
# a valid push over a different dump would pass every other test here.
if got_inputs_sha != expected_inputs_sha:
    sys.exit(f"[p5a] G6: push payload was built from inputs {got_inputs_sha}, "
             f"but this run is gated on {expected_inputs_sha}. Refusing.")

# Row count must match the inputs actually on disk, not a remembered number.
with np.load(inputs, allow_pickle=True, mmap_mode="r") as d:
    n = int(np.asarray(d["pass_truth"]).shape[0])
problems = E.validate_push_coverage(w, mi, n)
if problems:
    sys.exit(f"[p5a] G6: push coverage problems: {problems}")
if not np.isfinite(w).all():
    sys.exit("[p5a] G6: push payload carries non-finite weights")

# The reused payload's OWN agreement check must have run and passed.  A vacuous or absent check is
# not a pass -- the driver records `subsample_agreement_is_vacuous` precisely so this is decidable.
if not agree.get("checked"):
    sys.exit(f"[p5a] G6: push payload's subsample agreement was never checked: {agree}")
if not (agree["max_rel_dev"] <= agree["tolerance"]):
    sys.exit(f"[p5a] G6: push payload FAILED its own subsample agreement: {agree}")

print(f"[p5a] G6 PASS  push schema={schema} fingerprint={fp}")
print(f"[p5a] G6 also  n_rows={w.size} coverage=exact-arange finite=True "
      f"w_push min/max/mean={w.min():.16g}/{w.max():.16g}/{w.mean():.16g}")
print(f"[p5a] G6 also  subsample_agreement max_rel_dev={agree['max_rel_dev']:.6g} "
      f"tolerance={agree['tolerance']:.6g} n_shared_rows={agree['n_shared_rows']}")
print(f"[p5a] G6 also  payload source_weights={src_w}")
PY
  echo "[p5a] G6 PASS  push payload sha256 = $GOT_P  (REUSING; the GPU push stage will NOT re-run)"
  REUSE_PUSH=1
else
  GOT_P=""
  echo "[p5a] G6 n/a   P5A_PUSH_REUSE unset: the push stage WILL run and will spend GPU time"
fi

# ---------------------------------------------------------------------------------------------
# G7  THE GUARD THIS SCRIPT DID NOT HAVE, and the only reason 56978466 cost 13 minutes rather than
#     5 seconds.  Prove the ROOT interpreter can import the xsec chain BEFORE any long work.
#
#     `root_env_run` is the single definition of "the ROOT 6.28 environment", used by BOTH this
#     preflight and the real xsec stage below.  That sharing is the point: a preflight that builds
#     its environment differently from the run it guards is a lookalike, and this specific
#     interpreter fails in exactly that gap -- invoked directly it segfaults in cling, and only the
#     full-prefix conda activation in setup_salloc_env.sh makes it work.
#
#     It runs in a SUBSHELL so the conda activation cannot leak into the TensorFlow push stage, and
#     with `set +e` because sourcing that env script is not written to be `-e` clean; the exit
#     status of the subshell is the python call's own, so failures still propagate to `die`.
# ---------------------------------------------------------------------------------------------
ROOT628_PREFIX="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}"
ROOT_PY="${ROOT628_PREFIX}/bin/python3"
[[ -x "$ROOT_PY" ]] || die "G7: ROOT python is unavailable at $ROOT_PY" 8

root_env_run() {
  ( set +e
    source "${REPO}/setup_salloc_env.sh"
    export MNV_REPO="$REPO"
    export PYTHONPATH="${REPO}/omnifold_nn:${REPO}/2d-unfolding:${REPO}/nd-unfolding:${PET}:${PYTHONPATH:-}"
    "$@" )
}

# Preflight the EXACT import that failed, not a proxy for it: ROOT, then the u2d module whose
# module-level `import ROOT` raised at unfold_2d_omnifold_unbinned.py:21, then the driver itself.
root_env_run "$ROOT_PY" -c 'import ROOT, numpy; assert ROOT.gROOT; print("[p5a] G7 ROOT " + ROOT.gROOT.GetVersion() + " numpy " + numpy.__version__)' \
  || die "G7: ROOT/numpy import preflight failed -- refusing to spend GPU time" 8
root_env_run "$ROOT_PY" -c 'import unfold_2d_omnifold_unbinned; print("[p5a] G7 u2d imported (this is the exact chain that failed in 56978466)")' \
  || die "G7: unfold_2d_omnifold_unbinned import preflight failed -- refusing to spend GPU time" 8
root_env_run "$ROOT_PY" -c 'import extract_fullevent_fps as e; print("[p5a] G7 driver importable under ROOT python, xsec schema " + e.XSEC_SCHEMA)' \
  || die "G7: extraction driver is not importable under the ROOT interpreter" 8
echo "[p5a] G7 PASS  the ROOT interpreter imports the whole xsec chain"

if [[ "$CHECK_ONLY" == "1" ]]; then
  echo "[p5a] --check-only: G0..G7 all PASS, no job submitted, no GPU used."
  exit 0
fi

JOB="${SLURM_JOB_ID:-nojob}"
XSEC_OUT="${OUTDIR}/${MARK}.xsec.slurm-${JOB}.npz"
SUMMARY="${OUTDIR}/${MARK}.xsec.slurm-${JOB}.summary.json"

# A reused payload keeps its ORIGINATING job's filename.  That is deliberate: renaming or copying it
# under this job's id would launder 56978466's product into looking like this run's own, and the
# provenance of a 13-minute GPU pass is exactly the thing that must stay attributable.
if [[ "$REUSE_PUSH" == 1 ]]; then
  PUSH_OUT="$PUSH_REUSE"
else
  PUSH_OUT="${OUTDIR}/${MARK}.push.slurm-${JOB}.npz"
fi

# No-clobber on the products this run will write.  The push payload is deliberately NOT in this list
# when it is being reused -- that one is meant to already exist.
for f in "$XSEC_OUT" "${XSEC_OUT}.done" "$SUMMARY"; do
  [[ ! -e "$f" && ! -L "$f" ]] || die "no-clobber: $f already exists" 9
done

echo "[p5a] START $(date -u +%Y-%m-%dT%H:%M:%SZ) job=${JOB}"
echo "[p5a] arm     ${ARM_DIR}"
echo "[p5a] outdir  ${OUTDIR}"
echo "[p5a] push    ${PUSH_OUT}$([[ "$REUSE_PUSH" == 1 ]] && echo '  (REUSED, G6-verified)')"

# ---------------------------------------------------------------------------------------------
# STAGE 1 -- push.  TensorFlow interpreter, GPU.  Skipped entirely when a G6-verified payload is
# being reused, which is the whole point of the driver's stage split (extract_fullevent_fps.py:21-23:
# "the push pass costs GPU time that must not be re-spent when the extraction recipe changes").
#
# This runs under the plain `python3` of the tensorflow/2.15.0 module loaded at G1 -- i.e. the exact
# interpreter in which 56978466's reweight succeeded over all 49,152,885 rows.  Nothing about the
# push stage is changed by this repair, because nothing about it failed.
# ---------------------------------------------------------------------------------------------
if [[ "$REUSE_PUSH" == 1 ]]; then
  echo "[p5a] STAGE push SKIPPED -- consuming the G6-verified payload, no GPU reweight"
else
  TF_PY="$(command -v python3 || true)"
  [[ -n "$TF_PY" && -x "$TF_PY" ]] || die "TensorFlow python3 is unavailable" 6
  "$TF_PY" -c 'import tensorflow, omnifold' \
    || die "TensorFlow/omnifold import preflight failed" 6
  echo "[p5a] STAGE push  $(date -u +%Y-%m-%dT%H:%M:%SZ)  interpreter=$TF_PY"
  "$TF_PY" -u "${PET}/extract_fullevent_fps.py" \
    --stage push \
    --weights "$WEIGHTS" \
    --inputs "$INPUTS" \
    --push-out "$PUSH_OUT" \
    || die "push stage failed" 6
fi

# ---------------------------------------------------------------------------------------------
# STAGE 2 -- xsec.  ROOT interpreter, no TensorFlow, no GPU.  This is the stage that failed in
# 56978466 for want of `import ROOT`, and it is now run under the interpreter G7 already proved can
# import it.  `--weights` is deliberately NOT passed: the driver does not read it in this stage, and
# passing an ignored argument would misrepresent it as consumed.  The weights identity that matters
# here is already pinned by G3 and independently recorded inside the push payload's own
# `source_weights` key, which G6 printed.
# ---------------------------------------------------------------------------------------------
echo "[p5a] STAGE xsec  $(date -u +%Y-%m-%dT%H:%M:%SZ)  interpreter=$ROOT_PY"
root_env_run "$ROOT_PY" -u "${PET}/extract_fullevent_fps.py" \
  --stage xsec \
  --inputs "$INPUTS" \
  --push-out "$PUSH_OUT" \
  --out "$XSEC_OUT" \
  --summary "$SUMMARY" \
  --mcfile "$MCFILE" \
  --flux-hist "$FLUX_HIST" \
  || die "xsec stage failed" 6

# ---------------------------------------------------------------------------------------------
# CONDITION 1's third enforcement: the products say what they are not.
# ---------------------------------------------------------------------------------------------
python3 - "$OUTDIR" "$MARK" "$JOB" "$WEIGHTS" "$GOT_W" "$XSEC_OUT" "$PUSH_OUT" "$SUMMARY" \
         "$REUSE_PUSH" "$GOT_P" "$EXPECTED_PUSH_SHA" <<'PY'
import hashlib, json, os, sys
import numpy as np

outdir, mark, job, weights, wsha, xsec, push, summary = sys.argv[1:9]
reuse_push, push_sha, expected_push_sha = sys.argv[9], sys.argv[10], sys.argv[11]

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

doc = {
    "verdict": "NOT_CANONICAL",
    "what_this_is": "P5A nominal extraction on the ANNEALED arm, authorized 2026-08-14 "
                    "(Joseph verbatim 'Yes I authorize it').",
    "what_this_is_NOT": "the canonical P5A central vector and reported-bin mask. RUNBOOK:213 binds "
                        "every P5B component to the P5A central/mask/order; adopting THESE products "
                        "as that reference is a SEPARATE step and a SEPARATE decision, and nothing "
                        "in this run performs it.",
    "promotion_would_require": [
        "an explicit promotion decision, recorded with its authority as the 2026-08-13 nominal "
        "promotion was (state/p3f-pet-gate4-nominal-promotion-56563761.json)",
        "a resolution of CSTAT-O3: which assembler consumes the 2D P5B C_stat and what ratifies its "
        "common mask -- RUNBOOK:213's named authority did not exist because P5A had never extracted",
        "a quotability position. As of 2026-08-15 what remains of the VL100 quotability question is "
        "ONE ground -- G4, recovery_evaluated still False at the promoted configuration -- and it is "
        "NOT DETERMINABLE READ-ONLY at any effort. See vl100_quotability_scope below for the whole "
        "of it, including what this receipt's earlier emitted copies got wrong."
    ],
    "the_favourable_scalar_and_what_it_cannot_express": {
        "value": "abs_dev 0.035609 against the frozen fold_forward_ratio_dev_max of 0.05",
        "construction": "pet_diagnostic_quarantine.py:104-120 -- "
                        "|(fold_forward_sum_w_push_reco / fold_forward_sum_w_reco)/R - 1|, from two "
                        "sums already taken over the WHOLE reco leg",
        "therefore": "the shape information is integrated away BEFORE the ratio exists, so this "
                     "quantity cannot distinguish a uniform scale offset from a shape distortion "
                     "with the same integral. It bounds the INTEGRAL and says nothing about the grid.",
        "and_shape_dependence_is_measured_elsewhere": "lane D, 2026-08-14, f4267b4 -- per-cell "
            "structure in the fold-forward ratio, measured on the PRE-ANNEAL nominal run's weights. "
            "D's arithmetic reproduces exactly; the target is the pre-anneal arm, not this one. "
            "Numbers with operands: state/vl100-foldforward-shape-test-20260814.json (D's own) and "
            "state/RECEIPT-vl100-shape-corrected-foldforward-20260815.json (the scope correction). "
            "Not restated here: BEN-227/BEN-228 -- a receipt value copied into a second file "
            "diverges from it, so this key carries routes, not numbers.",
        "THE_GAP": "0.035609 bounds the integral and cannot bound the grid. Note what CLOSED and "
                   "what did NOT: the annealed arm's own per-cell fold-forward field HAS now been "
                   "measured post-hoc (the 2026-08-15 receipt above), and the earlier claim here "
                   "that it 'has not been measured by anyone' is superseded. What remains open is "
                   "the TRAINING-TIME question -- the fold-forward acts in iterations 2 and 3 of 3, "
                   "so a defect that mis-delivered weight during training is baked into push and no "
                   "post-hoc reweighting can probe it. That needs a retrained closure (OI-71, "
                   "OI-125).",
    },
    "guards_that_passed_before_this_run": {
        "G1_arm_schema": "seed_policy.lr_policy.schedule == fit-time-anneal-after-iteration-0 "
                         "(the PRIMARY guard; the pre-anneal arm has no lr_policy key at all)",
        "G2_checkpoint_containment": "inference_contract.step2_checkpoint realpath-resolves under "
                                    "fullevent_nominal_annealed/",
        "G3_weights_identity": wsha,
        "G4_inputs_identity": "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625",
        "G5_outputs_outside_the_arm": True,
        "G6_push_payload_identity": (push_sha if push_sha else
                                     "n/a -- this run computed its own push, nothing was reused"),
        "G7_root_interpreter_preflight": "ROOT, unfold_2d_omnifold_unbinned and the driver all "
                                        "imported under the root_6_28 prefix python BEFORE any GPU "
                                        "time was spent",
    },
    "job": job,
    "weights": {"path": weights, "sha256": wsha},
    "products": {},
}

# ------------------------------------------------------------------------------------------------
# PUSH PROVENANCE.  Per CONVENTION-receipt-ingredients (BEN-077): ship the ingredients, not just the
# verdict, so the reported numbers can CONTRADICT each other.  A reader who cannot re-derive
# w_push_mean from this block, or who finds the recomputed sha differing from the pin, has caught a
# real defect -- which a "push reuse: OK" line would have hidden.
# ------------------------------------------------------------------------------------------------
prov = {
    "reused_an_existing_payload": reuse_push == "1",
    "path": os.path.abspath(push),
    "sha256_measured_this_run": push_sha or None,
    "sha256_pin": expected_push_sha if reuse_push == "1" else None,
    "pin_matched": (bool(push_sha) and push_sha == expected_push_sha) if reuse_push == "1" else None,
}
if reuse_push == "1":
    prov["why_reused"] = (
        "job 56978466 FAILED 6:0 in the xsec stage for want of `import ROOT`, but its push stage had "
        "already completed over all 49,152,885 rows and written this payload. The driver splits the "
        "stages (extract_fullevent_fps.py:16-23) precisely so this GPU pass is not re-spent. The "
        "payload's filename retains 56978466's job id on purpose: the reweight is ITS product, not "
        f"job {job}'s."
    )
    prov["originating_job"] = "56978466"
try:
    with np.load(push, allow_pickle=True) as pz:
        w = np.asarray(pz["w_push"], np.float64)
        prov["ingredients"] = {
            "push_schema": str(np.asarray(pz["push_schema"])),
            "estimator_fingerprint": str(np.asarray(pz["estimator_fingerprint"])),
            "n_rows": int(w.size),
            "source_weights": str(np.asarray(pz["source_weights"])),
            "inputs_sha256": str(np.asarray(pz["inputs_sha256"])),
            "w_push_min": float(w.min()),
            "w_push_max": float(w.max()),
            "w_push_mean": float(w.mean()),
            "reweight_telemetry": np.asarray(pz["reweight_telemetry"], dtype=object).item(),
            "subsample_agreement": np.asarray(pz["subsample_agreement"], dtype=object).item(),
        }
        prov["ingredients"]["recomputed_here_vs_telemetry"] = (
            "w_push_min/max/mean above are recomputed from the payload by THIS script; "
            "reweight_telemetry carries the values the producing run printed. They must agree."
        )
except Exception as exc:                     # never let receipt-writing mask a completed run
    prov["ingredients_error"] = f"{type(exc).__name__}: {exc}"
doc["push_provenance"] = prov

# ------------------------------------------------------------------------------------------------
# THE OWED VL100 ANNOTATION, discharged here.  It was authored into this launcher at dc4bb8e but job
# 56978466 died before writing any receipt, so it has never actually reached disk.  It is a TOP-LEVEL
# key rather than only a line inside promotion_would_require because the distinction it draws is the
# one most likely to be flattened by someone quoting it second-hand.
#
# CORRECTED 2026-08-15, AND THE CORRECTION IS OF THIS LAUNCHER'S OWN TEXT.  What this key said until
# now -- that lane D falsified VL100's physics ground, one of four grounds -- is wrong twice, and it
# is here because the MEDIATOR SESSION RELAYED D'S FINDING AS ESTABLISHED INTO THREE PLACES BEFORE
# CHECKING WHICH ARTIFACT IT MEASURED, and had lane C write that relay into this generator.  This is
# a correction of a propagation, not a drift in the record: D's arithmetic reproduces exactly, D read
# the file the closure's own quarantine manifest names, and nothing about the target came from D.
# ------------------------------------------------------------------------------------------------
doc["vl100_quotability_scope"] = {
    "STATUS": "SCOPE-CORRECTED 2026-08-15. Any emitted copy of this key under "
              "fullevent_nominal_annealed_extraction_unpromoted/ that lacks this STATUS field "
              "PREDATES the correction and states the superseded claim. Those artifacts were "
              "deliberately NOT rewritten -- an emitted receipt records what its run asserted. "
              "Read them against this block.",
    "what_IS_established": "the physics ground is MIS-TARGETED, not falsified. It is stated from a "
        "fold-forward deficit measured on the PRE-ANNEAL nominal arm's weights, while VL100 is the "
        "ANNEALED arm's recovery. Under both a well-posed and an adversarial shape correction VL100 "
        "is unchanged and still clears its primary criterion.",
    "and_the_defect_is_in_the_RECORD_not_in_the_probe": "closure 56552326's own quarantine manifest "
        "(NONQUOTABLE-DIAGNOSTIC.manifest.slurm-56552326.json) carries job_id 56552326 and its own "
        "push_sha256 for the annealed closure, then names weights_path / weights_sha256 = the "
        "PRE-ANNEAL fullevent_nominal/ file and computes its fold_forward block, its "
        "rejection_reason and publication_gate_rejects_this_on_physics_alone FROM THAT FILE. Lane D "
        "read exactly the artifact the manifest names as the source of its own rejection. So 'NOT "
        "QUOTABLE on the physics alone' is a TRUE STATEMENT ABOUT A RUN THAT IS NOT THIS ONE, "
        "attached to VL100 by the manifest's pointers. A hash pin verifies you read the file that "
        "was named, never that the right file was named. BEN-312.",
    "the_FOUR_GROUNDS_phrase_was_a_COUNT_WITH_NO_MEMBERS": "do not repeat it, in either direction. "
        "'D examined one of four quotability grounds, the other three are hygiene and unexamined' "
        "originates in f4267b4's own limitation sentence, propagated to five places, and NONE of "
        "them enumerates the four; no CONVENTION-*.md defines quotability. Two of those five "
        "restatements were the mediator's, put into a dispatch and a user report without asking "
        "which artifact enumerated the set. Reconstructed from the artifacts there are THREE and "
        "two are the same ground: G1 physics DETERMINED (does not describe this run); G2 the "
        "NONQUOTABLE-DIAGNOSTIC. label DETERMINED and NOT INDEPENDENT of G1, its own note scoping "
        "it to engine edits and promotion; G3 provenance hygiene DETERMINED CLEAN, with one "
        "residual inherited from G1 because hash:nominal-weights pins the pre-anneal file. "
        "BEN-313.",
    "what_REMAINS_and_is_the_only_live_ground": "G4 -- recovery_evaluated is still False at the "
        "promoted configuration, and it is NOT DETERMINABLE READ-ONLY AT ANY EFFORT, because "
        "recovery is defined against an injected truth reweight and the promoted nominal has "
        "neither tilt nor A/B split. It needs GPU time, not more reading.",
    "why_this_still_withholds_quotability_from_this_product": "G4 is undetermined and the closure "
        "certifying the annealed arm has a fold-forward ratio near unity where the nominal run's is "
        "far from it -- so that closure does not EXERCISE the deficit at all and is SILENT about "
        "that failure mode rather than reassuring about it. Silence is not a licence to quote.",
    "refs_NOT_restated_values": {
        "grounds_determination": "FINDING-20260815-the-quarantine-measured-a-different-run.md",
        "mechanism_of_the_misread": "FINDING-20260815-a-restatement-is-not-a-second-measurement.md",
        "every_number_with_its_operands": "state/RECEIPT-vl100-shape-corrected-foldforward-20260815.json",
        "D_s_own_receipt_untouched": "state/vl100-foldforward-shape-test-20260814.json (f4267b4)",
        "live_items": "OI-71 (G4, and the training-time question), OI-125 (the receipt-chain hole)",
        "why_no_numbers_here": "BEN-227/BEN-228 -- quote with a ref or not at all; a receipt value "
                               "duplicated into a second file diverges from it.",
    },
}
for label, p in (("xsec", xsec), ("push", push), ("summary", summary)):
    if os.path.isfile(p):
        doc["products"][label] = {"path": p, "bytes": os.path.getsize(p), "sha256": sha(p)}

out = os.path.join(outdir, f"{mark}.NOT_CANONICAL.slurm-{job}.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=2, sort_keys=True)
print(f"[p5a] wrote {out}")
PY

echo "[p5a] DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)"
