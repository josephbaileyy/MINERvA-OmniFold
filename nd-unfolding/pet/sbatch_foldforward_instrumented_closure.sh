#!/bin/bash
#SBATCH --job-name=ff_closure
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/foldforward_instrumented/logs/ff_%A_%a.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/foldforward_instrumented/logs/ff_%A_%a.err
#
# FOLD-FORWARD INSTRUMENTED / CORRECTED POWERED CLOSURE  --  OI-71 G4 and OI-125.
#
# READING FIXED IN ADVANCE:
#   docs/orchestration/PREDECLARATION-20260815-foldforward-instrumented-closure.md
#   docs/orchestration/AUTHORIZATION-20260815-foldforward-closure-run.md
#   docs/orchestration/PROPOSAL-20260815-instrumented-and-corrected-foldforward-closure.md
#
# 6 array tasks: 0-2 = ARM 0 (instrumented, uncorrected), 3-5 = ARM 1 (scale-only corrected).
# The three draws per arm are the SAME configuration -- the closure driver takes no seed flag and
# reads NOMINAL_SEED_POLICY -- so the spread is training nondeterminism, exactly as the three
# existing draws (56552326 / 56611837 / 56626305, sd 0.000820128) were produced.
#
# ARM 0 IS A HARD GATE ON READING ARM 1. If arm 0 does not reproduce the existing draws, arm 1 is
# not read at all, whatever it printed. That gate is applied by the reader, not by this launcher --
# a launcher that decided it would be a launcher deciding a verdict.
#
# WHY A NEW LAUNCHER RATHER THAN AN EDIT TO sbatch_powered_closure_stability_repeat.sh: that file
# pins closure_powered_truth_reweight.py by sha256 and is bound by run receipts. Editing any pinned
# launcher is prohibited while receipts bind it (BEN-270, OI-123). Nothing here is repinned; this
# script and closure_foldforward_instrumented.py are both NEW files, and the driver, wrapper and
# engine are untouched and asserted below by digest.
#
# EXPECTED NON-ZERO EXIT, DECLARED IN ADVANCE, and inherited from the driver rather than invented
# here: closure_powered_truth_reweight.py:105 hardcodes RESIDUAL_OVER_GAP_MAX = 0.20 -- the bar
# CLM-012 RETIRED on 2026-08-09 -- and exits 3 when its own literal is unmet. That is why 56552326
# reads FAILED in sacct despite completing and writing its products. This launcher tolerates exit 3
# AND ONLY exit 3, then asserts the report exists and carries both a numeric recovery and the
# fold-forward records. NO THRESHOLD IS ALTERED: the retired bar is not consulted for any verdict.
#
# NO PROMOTION. NO ENGINE EDIT. NO THRESHOLD CHANGE. niter 3. Branch C stays closed.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
# FF_REPO_OVERRIDE is honoured ONLY together with FF_GUARDS_ONLY, so the guard tests can point
# G0 at a sandbox with a deliberately mutated file while a real run CANNOT be redirected by it.
if [[ -n "${FF_GUARDS_ONLY:-}" && -n "${FF_REPO_OVERRIDE:-}" ]]; then REPO="${FF_REPO_OVERRIDE}"; fi
PET="${REPO}/nd-unfolding/pet"
OUTDIR="${PET}/foldforward_instrumented"
MARK="NONQUOTABLE-DIAGNOSTIC"
TASK="${SLURM_ARRAY_TASK_ID:-0}"
JOB="${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-nojob}}"

WRAPPER="${PET}/closure_foldforward_instrumented.py"
ANNEALED="${PET}/closure_powered_annealed_lr.py"
DRIVER="${PET}/closure_powered_truth_reweight.py"
ENGINE="${REPO}/omnifold_nn/omnifold/omnifold.py"
INPUTS="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"

mkdir -p "${OUTDIR}/logs"

die() { echo "[ff-launch] FATAL: $1" >&2; exit "${2:-1}"; }

# ---------------------------------------------------------------------------------------------
# G0  every file this run's BEHAVIOUR depends on, asserted by digest rather than by trust.
#     If any differs, the run is not the configuration the predeclaration describes.
#
#     THE WRAPPER PIN WAS ADDED 2026-08-15 AND ITS ABSENCE WAS A REAL EXPOSURE. The first version
#     pinned the driver, the annealed wrapper and the engine -- and NOT
#     closure_foldforward_instrumented.py, the module that decides what the arm actually does. So a
#     task could satisfy every pin the launcher declared while running different code. That went
#     from hypothetical to concrete when 57012031_3 died on a dtype promotion and the fix had to be
#     WITHHELD from the cluster, because copying it while _4/_5 were PENDING would have put two
#     tasks of one array on two code versions with the array id as their only shared provenance.
#     Generalised in BEN-312: THE THING THAT VERIFIES A RUN MUST NAME EVERY OBJECT THE RUN'S
#     BEHAVIOUR DEPENDS ON -- a pin set that omits one is satisfiable by a run it does not describe.
#
#     Maintenance note, stated because it is the cost of the pin: editing the wrapper changes its
#     digest and this literal must be updated in the same commit. That is the pin working. Do NOT
#     delete the pin to avoid the edit; and do not repin the DRIVER, which is receipt-bound
#     (BEN-270).
#
#     WRAPPER PIN MOVE 1, 2026-08-15, ee269b09 -> b24cfefe, for the two report-annotation fixes
#     in closure_foldforward_instrumented.py (non-quotability as a field; the retired-0.80-bar
#     rename). This is the maintenance action the paragraph above prescribes, not a BEN-270 repin:
#     the driver/annealed/engine pins are byte-identical and untouched, and NO receipt binds the
#     wrapper digest -- the six 2026-08-15 products record `fold_forward_instrumented_by` as a
#     basename only. Arm 1's provenance survives the move because G0 PRINTS the digests it checked,
#     so logs/ff_57038937_{3,4,5}.out carry `ee269b09...` as the wrapper those tasks actually ran.
#     Arm 0 (57012031_{0,1,2}) predates the wrapper pin entirely and its log prints the 3-pin line.
#
#     WRAPPER PIN MOVE 2, 2026-08-16, b24cfefe -> 0e1471ba, for the ANNEAL ATTESTATION (BEN-317).
#     The wrapper now calls its own `attest_anneal_took_effect` and emits `anneal_lr_proof` into the
#     report, so a FUTURE run proves the anneal took effect instead of asserting that
#     install_annealed_multifold() was called. The old boolean
#     `fold_forward_composed_with_annealed_arm` was True even when the LR record list was EMPTY --
#     the exact state closure_powered_annealed_lr.py:114-115 fails closed on -- which made an
#     un-annealed run indistinguishable from an annealed one in the receipt.
#
#     Same maintenance action, same reasoning as move 1, and the same three things still hold: the
#     driver/annealed/engine pins are byte-identical and untouched, no receipt binds the wrapper
#     digest, and the digests G0 checked are PRINTED so every run stays readable from its own log.
#
#     THIS MOVE DOES NOT AND CANNOT RETRO-ATTEST THE SIX 2026-08-15 PRODUCTS. They ran b24cfefe or
#     earlier, they carry the boolean alone, and they remain BOUNDED, NOT ATTESTED -- see BEN-317.
#     Only runs launched after this commit carry `anneal_lr_proof`.
#
#     WRAPPER PIN MOVE 3, 2026-08-16, 0e1471ba -> 7499814e, for END-OF-RUN PUSH RECORDING.
#     Predeclared in PREDECLARATION-20260816-endofrun-push-recording.md BEFORE any run carries it.
#     The wrapper now also hooks RunStep2 and records the push it LEAVES, so the value
#     `closure_powered_truth_reweight.py:332-333` persists -- the one OI-125 is about -- is RECORDED
#     BY THE RUN instead of re-reduced by a reader. The RunStep1 hook records at CONSUMPTION and
#     therefore cannot see it: `RunStep2(niter-1)` leaves a push nothing consumes. Substituting the
#     last RunStep1 row gives 0.981165 against a predicted 1.011418, a ~105-draw-sd 'disagreement'
#     with the sign of ratio-1 flipped (BEN-360, VL134).
#
#     NO RUN IS ATTACHED TO THIS MOVE. The 3-draw re-run was proposed and DENIED on 2026-08-16: the
#     driver takes no seed flag (see :23-24), so a new run is a NEW SAMPLE and its recorded scalar
#     could not validate VL134 -- it would sit in the ledger beside it as a non-comparable number.
#     This lands so the next run that happens FOR ITS OWN REASONS carries the value for free.
#
#     ORDERING IS FIXED IN THE RECORD, not left to whoever launches next: this and move 2 (the anneal
#     attestation) both land BEFORE anything launches. A run wants both.
# ---------------------------------------------------------------------------------------------
declare -A PINS=(
  ["$DRIVER"]="a45fae7c3f978c34bf73f35ab56aac668439c5784a3968b4f09799ee6090fd48"
  ["$ANNEALED"]="ce9f11f4872dd611932705e36f4ecfb651f8ee8eed796cca98be598d92fbb911"
  ["$ENGINE"]="3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa"
  ["$WRAPPER"]="7499814ecb460fdb05c8c83a2d6d54a63214e5661f4b29c2466de7592af3fb6f"
)
for f in "${!PINS[@]}"; do
  [[ -s "$f" ]] || die "missing: $f" 2
  got="$(sha256sum "$f" | awk '{print $1}')"
  [[ "$got" == "${PINS[$f]}" ]] || die "digest drift on $(basename "$f"): $got != ${PINS[$f]}. This run is NOT the predeclared configuration. Refusing." 2
done
echo "[ff-launch] G0 PASS  driver/annealed-wrapper/engine/instrumentation all match their digests"
for f in "${!PINS[@]}"; do echo "[ff-launch]    ${PINS[$f]}  $(basename "$f")"; done

# ---------------------------------------------------------------------------------------------
# G1  arm assignment is derived from the task id and PRINTED, so the log says which arm ran.
# ---------------------------------------------------------------------------------------------
if   (( TASK >= 0 && TASK <= 2 )); then ARM="arm0"; DRAW=$(( TASK ));     EXTRA=""
elif (( TASK >= 3 && TASK <= 5 )); then ARM="arm1"; DRAW=$(( TASK - 3 )); EXTRA="--correct-fold-forward"
else die "task id ${TASK} is outside 0-5; arms are 0-2=arm0, 3-5=arm1" 2
fi
TAG="${ARM}_draw${DRAW}"
OUT_JSON="${OUTDIR}/${MARK}.FOLDFORWARD_${ARM^^}_DRAW${DRAW}.slurm-${JOB}_${TASK}.json"
OUT_NPZ="${OUT_JSON%.json}.npz"
WEIGHTS="${OUTDIR}/weights_${TAG}_${JOB}_${TASK}"
echo "[ff-launch] G1 task=${TASK} -> ${TAG}  extra='${EXTRA}'"
echo "[ff-launch]    report  ${OUT_JSON}"

# ---------------------------------------------------------------------------------------------
# G2  refuse to overwrite a completed product. Validate CONTENT, not existence (BEN-023): a
#     partial report must not block its own repair.
# ---------------------------------------------------------------------------------------------
if [[ -s "$OUT_JSON" ]]; then
  if python3 - "$OUT_JSON" <<'PY'
import json, sys
try:
    r = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(1)
ok = (isinstance((r.get("metrics") or {}).get("recovery"), float)
      and len(r.get("fold_forward_per_iteration") or []) > 0)
sys.exit(0 if ok else 1)
PY
  then die "a COMPLETE report already exists at ${OUT_JSON}; refusing to overwrite" 0
  else echo "[ff-launch] G2 an INCOMPLETE report exists; it will be replaced (BEN-023)"
  fi
fi

# GUARDS-ONLY MODE. Exists so the pins above can be SEEN TO FAIL without burning an allocation --
# a guard nobody has watched refuse is not yet a guard. Exercised by
# tests/test_foldforward_launcher_guards.sh; does no training and writes no product.
if [[ -n "${FF_GUARDS_ONLY:-}" ]]; then
  echo "[ff-launch] FF_GUARDS_ONLY set -- guards passed, exiting before any work"
  exit 0
fi

module load tensorflow/2.15.0
export MNV_REPO="${REPO}"
mkdir -p "$WEIGHTS"

echo "[ff-launch] launching ${TAG} at $(date -u +%FT%TZ)"
set +e
python3 -u "$WRAPPER" --annealed ${EXTRA} \
  --inputs "$INPUTS" \
  --json "$OUT_JSON" \
  --artifact "$OUT_NPZ" \
  --weights-folder "$WEIGHTS"
rc=$?
set -e
echo "[ff-launch] driver exit ${rc}"

# Exit 3 AND ONLY exit 3 is tolerated, for the reason in the header.
if (( rc != 0 && rc != 3 )); then die "driver exited ${rc}, which is neither 0 nor the declared 3" "$rc"; fi

# ---------------------------------------------------------------------------------------------
# G3  the products must exist AND carry what this run was launched to produce. A tolerated exit
#     code with no fold-forward records is a failure, not a pass.
# ---------------------------------------------------------------------------------------------
python3 - "$OUT_JSON" "$ARM" <<'PY' || die "product validation failed" 4
import json, sys
path, arm = sys.argv[1], sys.argv[2]
r = json.load(open(path))
rec = r.get("fold_forward_per_iteration") or []
m = (r.get("metrics") or {})
assert isinstance(m.get("recovery"), float), "no numeric recovery in the report"
assert rec, "no fold_forward_per_iteration records"
niter = (r.get("configuration") or {}).get("niter")
assert niter is None or len(rec) == int(niter), f"{len(rec)} records vs niter={niter}"
# ANNEAL ATTESTATION IS A PRODUCT REQUIREMENT, not just a wrapper courtesy (BEN-317). This launcher
# always passes --annealed, so a report without a passing proof is a report whose configuration is
# unestablished -- which is what the six 2026-08-15 products are, and the reason this assert exists.
proof = r.get("anneal_lr_proof")
assert isinstance(proof, dict), (
    "no `anneal_lr_proof` in the report. The wrapper emits one for every --annealed run since "
    "2026-08-16; its absence means an older wrapper ran, and G0 should already have refused that.")
assert proof.get("pass") is True, f"anneal_lr_proof did not pass: {proof!r}"
assert proof.get("n_fits_at_annealed_lr", 0) > 0, (
    f"anneal_lr_proof records ZERO fits at the annealed rate, so nothing was annealed: {proof!r}")
# THE END-OF-RUN PUSH MUST BE PRESENT AND SELF-CONSISTENT (BEN-360, VL134). The last
# fold_forward_per_iteration row is the push entering the FINAL iteration, one step earlier; the
# quantity OI-125 needs is the one RunStep2(niter-1) leaves, which no RunStep1 row can see.
eor = r.get("fold_forward_end_of_run")
s2 = r.get("fold_forward_post_step2_per_iteration") or []
assert isinstance(eor, dict), (
    "no `fold_forward_end_of_run` in the report. Emitted for every run since 2026-08-16; its "
    "absence means an older wrapper ran, and G0 should already have refused that.")
assert niter is None or len(s2) == int(niter), f"{len(s2)} post-RunStep2 records vs niter={niter}"
assert isinstance(eor.get("reco_weighted_mean_push"), float), f"end-of-run push not numeric: {eor!r}"
assert eor.get("is_end_of_run_push") is True, f"end-of-run row not flagged as such: {eor!r}"
# The overlap the wrapper already gated, re-checked HERE so the launcher does not take the wrapper's
# word for it: RunStep2(i) leaves the push RunStep1(i+1) consumes.
_by = {int(k["iteration"]): k for k in rec}
for k in s2:
    nxt = _by.get(int(k["iteration"]) + 1)
    if nxt is not None:
        assert k["reco_weighted_mean_push"] == nxt["reco_weighted_mean_push"], (
            f"hooks disagree on the push at iteration {k['iteration']}: "
            f"{k['reco_weighted_mean_push']!r} vs {nxt['reco_weighted_mean_push']!r}")
want = (arm == "arm1")
assert bool(r.get("fold_forward_correction_applied")) == want, \
    f"arm={arm} but fold_forward_correction_applied={r.get('fold_forward_correction_applied')!r}"
for k in rec:
    assert (k.get("applied_correction_factor") is not None) == want, \
        f"arm={arm} but iteration {k['iteration']} correction factor is {k.get('applied_correction_factor')!r}"
print(f"[ff-launch] G3 PASS  recovery={m['recovery']!r}  iterations={len(rec)}  arm={arm}")
print(f"[ff-launch]    END-OF-RUN push (RunStep2({eor['iteration']}) left it): "
      f"{eor['reco_weighted_mean_push']!r}  dev_from_R={eor['deviation_from_R']!r}")
for k in rec:
    print(f"[ff-launch]    it{k['iteration']}: ratio={k['reco_weighted_mean_push']!r} "
          f"R={k['step1_class_ratio']!r} dev={k['deviation_from_R']!r} "
          f"factor={k['applied_correction_factor']!r}")
PY

echo "[ff-launch] ${TAG} COMPLETE at $(date -u +%FT%TZ)"
echo "[ff-launch] products:"
ls -la "$OUT_JSON" "$OUT_NPZ"
sha256sum "$OUT_JSON" "$OUT_NPZ"
