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
# It is NOT a quotability claim: lane D established 2026-08-14 that the fold-forward deficit is
# SHAPE-dependent (per-cell ratio 0.173 -> 1.420, 68x clear of the noise expectation), so the
# "normalization divides out" argument is unavailable and how far VL100 moves is unrecomputed.
#
# USAGE
#   bash sbatch_p5a_fullevent_nominal_extract.sh --check-only   # run G1..G5 and exit; no job, no GPU
#   sbatch sbatch_p5a_fullevent_nominal_extract.sh              # the real run
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

if [[ "$CHECK_ONLY" == "1" ]]; then
  echo "[p5a] --check-only: G0..G5 all PASS, no job submitted, no GPU used."
  exit 0
fi

JOB="${SLURM_JOB_ID:-nojob}"
PUSH_OUT="${OUTDIR}/${MARK}.push.slurm-${JOB}.npz"
XSEC_OUT="${OUTDIR}/${MARK}.xsec.slurm-${JOB}.npz"
SUMMARY="${OUTDIR}/${MARK}.xsec.slurm-${JOB}.summary.json"

echo "[p5a] START $(date -u +%Y-%m-%dT%H:%M:%SZ) job=${JOB}"
echo "[p5a] arm     ${ARM_DIR}"
echo "[p5a] outdir  ${OUTDIR}"

python3 "${PET}/extract_fullevent_fps.py" \
  --stage all \
  --weights "$WEIGHTS" \
  --inputs "$INPUTS" \
  --push-out "$PUSH_OUT" \
  --out "$XSEC_OUT" \
  --summary "$SUMMARY" \
  --mcfile "$MCFILE" \
  --flux-hist "$FLUX_HIST" \
  || die "extraction driver failed" 6

# ---------------------------------------------------------------------------------------------
# CONDITION 1's third enforcement: the products say what they are not.
# ---------------------------------------------------------------------------------------------
python3 - "$OUTDIR" "$MARK" "$JOB" "$WEIGHTS" "$GOT_W" "$XSEC_OUT" "$PUSH_OUT" "$SUMMARY" <<'PY'
import hashlib, json, os, sys

outdir, mark, job, weights, wsha, xsec, push, summary = sys.argv[1:9]

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
        "a quotability position: lane D established 2026-08-14 that the fold-forward deficit is "
        "SHAPE-dependent (per-cell ratio 0.173->1.420, 68x clear of noise), so the 'normalization "
        "divides out of unit-normalized spectra' argument is NOT available and how far VL100 moves "
        "is unrecomputed"
    ],
    "guards_that_passed_before_this_run": {
        "G1_arm_schema": "seed_policy.lr_policy.schedule == fit-time-anneal-after-iteration-0 "
                         "(the PRIMARY guard; the pre-anneal arm has no lr_policy key at all)",
        "G2_checkpoint_containment": "inference_contract.step2_checkpoint realpath-resolves under "
                                    "fullevent_nominal_annealed/",
        "G3_weights_identity": wsha,
        "G4_inputs_identity": "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625",
        "G5_outputs_outside_the_arm": True,
    },
    "job": job,
    "weights": {"path": weights, "sha256": wsha},
    "products": {},
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
