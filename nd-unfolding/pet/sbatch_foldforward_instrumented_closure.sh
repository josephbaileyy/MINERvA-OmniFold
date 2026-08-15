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
# G0  the three files this run must NOT have changed, asserted by digest rather than by trust.
#     If any differs, the run is not the configuration the predeclaration describes.
# ---------------------------------------------------------------------------------------------
declare -A PINS=(
  ["$DRIVER"]="a45fae7c3f978c34bf73f35ab56aac668439c5784a3968b4f09799ee6090fd48"
  ["$ANNEALED"]="ce9f11f4872dd611932705e36f4ecfb651f8ee8eed796cca98be598d92fbb911"
  ["$ENGINE"]="3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa"
)
for f in "${!PINS[@]}"; do
  [[ -s "$f" ]] || die "missing: $f" 2
  got="$(sha256sum "$f" | awk '{print $1}')"
  [[ "$got" == "${PINS[$f]}" ]] || die "digest drift on $(basename "$f"): $got != ${PINS[$f]}. This run is NOT the predeclared configuration. Refusing." 2
done
echo "[ff-launch] G0 PASS  driver/annealed-wrapper/engine all match their recorded digests"

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
want = (arm == "arm1")
assert bool(r.get("fold_forward_correction_applied")) == want, \
    f"arm={arm} but fold_forward_correction_applied={r.get('fold_forward_correction_applied')!r}"
for k in rec:
    assert (k.get("applied_correction_factor") is not None) == want, \
        f"arm={arm} but iteration {k['iteration']} correction factor is {k.get('applied_correction_factor')!r}"
print(f"[ff-launch] G3 PASS  recovery={m['recovery']!r}  iterations={len(rec)}  arm={arm}")
for k in rec:
    print(f"[ff-launch]    it{k['iteration']}: ratio={k['reco_weighted_mean_push']!r} "
          f"R={k['step1_class_ratio']!r} dev={k['deviation_from_R']!r} "
          f"factor={k['applied_correction_factor']!r}")
PY

echo "[ff-launch] ${TAG} COMPLETE at $(date -u +%FT%TZ)"
echo "[ff-launch] products:"
ls -la "$OUT_JSON" "$OUT_NPZ"
sha256sum "$OUT_JSON" "$OUT_NPZ"
