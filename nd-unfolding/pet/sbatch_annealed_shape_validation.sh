#!/bin/bash
#SBATCH --job-name=ann_shape
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=08:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/annealed_shape_validation/logs/ann_shape_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/annealed_shape_validation/logs/ann_shape_%j.err
#
# D2 POWERED CLOSURE UNDER THE INTENDED LR ANNEAL -- the SHAPE validation.
# Authorized by Joseph 2026-08-09/10 (authorize_annealed_shape_validation, option b).
# Reading FIXED IN ADVANCE: docs/orchestration/PREDECLARATION-20260810-annealed-shape-validation.md
#
#   rec > 0.566853        REAL REPAIR (shape improves too)
#   |rec - 0.546853|<=.02 NO INFORMATION on shape (normalization repair not paid for in shape)
#   rec < 0.526853        TRADE-OFF CONFIRMED, ARM REJECTED
#   rec < 0.494582        FAILS the adopted CLM-012 criterion outright
#
# NO THRESHOLD IS MODIFIED. NO ENGINE EDIT (the anneal is a MultiFold subclass overriding CompileModel
# at fit time; omnifold.py is read-only and its sha is recorded). NO PROMOTION. Branch C stays closed.
# A CLEAN RESULT DOES NOT AUTHORIZE EDITING omnifold.py -- that decision is separate and Joseph's.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PET="${REPO}/nd-unfolding/pet"
OUTDIR="${PET}/annealed_shape_validation"
MARK="NONQUOTABLE-DIAGNOSTIC"
JOB="${SLURM_JOB_ID:-nojob}"

WRAPPER="${PET}/closure_powered_annealed_lr.py"
DRIVER="${PET}/closure_powered_truth_reweight.py"
PREFLIGHT="${PET}/preflight_powered_closure.py"
ENGINE="${REPO}/omnifold_nn/omnifold/omnifold.py"
INPUTS="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
EXPECTED_INPUTS_SHA="fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"

REPORT="${OUTDIR}/${MARK}.POWERED_CLOSURE_ANNEALED.slurm-${JOB}.json"
ARTIFACT="${OUTDIR}/${MARK}.POWERED_CLOSURE_ANNEALED.slurm-${JOB}.npz"
PFRECEIPT="${OUTDIR}/${MARK}.PREFLIGHT.slurm-${JOB}.json"
WEIGHTS="${OUTDIR}/weights_annealed_${JOB}"
RUNLOG="${OUTDIR}/logs/ann_shape_${JOB}.log"

mkdir -p "${OUTDIR}/logs" "$WEIGHTS"

die() { echo "[ann] FATAL: $*" >&2; exit "${2:-1}"; }
for f in "$WRAPPER" "$DRIVER" "$PREFLIGHT" "$ENGINE" "$INPUTS"; do
  [[ -s "$f" ]] || die "missing $f"
done

echo "[ann] job=${JOB} host=$(hostname)"
echo "[ann] THIS PRODUCT IS NOT QUOTABLE. Shape validation of a candidate repair, not a result."
echo "[ann] engine sha256 (READ-ONLY, not edited): $(sha256sum "$ENGINE" | cut -d' ' -f1)"

gs="$(sha256sum "$INPUTS" | cut -d' ' -f1)"
[[ "$gs" == "$EXPECTED_INPUTS_SHA" ]] || die "inputs sha mismatch: $gs != $EXPECTED_INPUTS_SHA" 3
echo "[ann] inputs sha OK ${gs:0:16}"

module load tensorflow/2.15.0
export MNV_REPO="$REPO"
export PYTHONPATH="${REPO}/omnifold_nn${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONUNBUFFERED=1
cd "$PET"

# BEN-075 rule (1): probe EVERY stage's imports up front. Two seconds, and it fails here rather than
# after a two-hour closure. This job needs TF + the engine; it does NOT need ROOT (no xsec stage).
python3 -c "import tensorflow, omnifold; from omnifold import MultiFold; import numpy" \
  || die "import preflight failed with PYTHONPATH=${PYTHONPATH}" 4
echo "[ann] import preflight OK"

# The predeclared protocol gate, same as the graded run's route, receipt in the quarantine namespace.
set +e
python3 "$PREFLIGHT" --inputs "$INPUTS" --json "$PFRECEIPT" --inputs-sha256 "$gs" >>"$RUNLOG" 2>&1
pf_rc=$?
set -e
pf_verdict="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("verdict","<none>"))' "$PFRECEIPT" 2>/dev/null || echo "NO_RECEIPT")"
echo "[ann] preflight rc=${pf_rc} verdict=${pf_verdict}"
[[ $pf_rc -eq 0 ]] || die "preflight gate refused the run (verdict=${pf_verdict})" "$pf_rc"

# Whole stream to a file; filter READS of it, never the write (BEN-026).
srun -n 1 -c 32 --gpus=1 python3 -u "$WRAPPER" \
  --inputs "$INPUTS" \
  --json "$REPORT" \
  --artifact "$ARTIFACT" \
  --weights-folder "$WEIGHTS" \
  >>"$RUNLOG" 2>&1
echo "[ann] closure rc=0  report=${REPORT}"

# Self-declaring rejection manifest -- non-quotability PROVEN, not asserted.
python3 -u - <<PY >>"$RUNLOG" 2>&1
import sys
sys.path.insert(0, "${PET}")
import pet_diagnostic_quarantine as q
q.build_diagnostic_manifest(
    weights_npz="${PET}/fullevent_nominal/pet_fullevent_nominal_weights.npz",
    xsec_npz="${REPORT}",
    push_npz="${ARTIFACT}",
    xsec_summary="${PFRECEIPT}",
    inputs_npz="${INPUTS}",
    out_path="${OUTDIR}/${MARK}.manifest.slurm-${JOB}.json",
    job_id="${JOB}",
    extra={"launcher": "sbatch_annealed_shape_validation.sh",
           "arm": "powered_closure_warm_fixed_annealed_lr",
           "predeclaration": "docs/orchestration/PREDECLARATION-20260810-annealed-shape-validation.md",
           "engine_edited": False,
           "authorizes_engine_change": False,
           "note": "shape validation of a candidate repair; a clean result does NOT authorize "
                   "editing omnifold.py -- that promotion is separate and Joseph's"})
PY

# Apply the PREDECLARED reading. Reports, never decides -- and never edits a threshold.
python3 - "$REPORT" <<'PY'
import json, sys
rep = json.load(open(sys.argv[1]))
rec = (rep.get("metrics") or {}).get("recovery")
BASE, BAND, THRESH = 0.546853, 0.02, 0.494582
print("[ann] ===== PREDECLARED READING =====")
print(f"[ann] recovery (annealed) = {rec}")
print(f"[ann] baseline            = {BASE}   band +/-{BAND}   adopted threshold {THRESH}")
if rec is None:
    print("[ann] VERDICT: NO RECOVERY REPORTED -- inconclusive, fail closed")
elif rec < THRESH:
    print(f"[ann] VERDICT: FAILS THE ADOPTED CRITERION ({rec:.6f} < {THRESH}) -- arm rejected")
elif rec > BASE + BAND:
    print(f"[ann] VERDICT: REAL REPAIR -- shape improves too (+{rec-BASE:.6f})")
elif rec < BASE - BAND:
    print(f"[ann] VERDICT: TRADE-OFF CONFIRMED, ARM REJECTED ({rec-BASE:+.6f} vs baseline)")
else:
    print(f"[ann] VERDICT: NO INFORMATION on shape ({rec-BASE:+.6f}, inside the predeclared band)")
lp = (rep.get("annealed_lr_arm") or {}).get("lr_proof") or {}
print(f"[ann] anneal proof: {lp.get('n_fits_base_lr')} fit(s) at {lp.get('base_lr')}, "
      f"{lp.get('n_fits_annealed')} at {lp.get('annealed_lr')}")
print("[ann] Branch C remains closed. No threshold modified. No engine edit. No promotion.")
PY
echo "[ann] DONE."
