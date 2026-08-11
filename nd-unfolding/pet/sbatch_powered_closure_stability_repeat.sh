#!/bin/bash
#SBATCH --job-name=pc_stab
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=06:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/annealed_shape_validation/logs/pc_stab_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/annealed_shape_validation/logs/pc_stab_%j.err
#
# POWERED-CLOSURE STABILITY REPEAT -- is 0.5126033 a point estimate or one draw?
# Reading FIXED IN ADVANCE, three branches:
#   docs/orchestration/PREDECLARATION-20260811-powered-closure-stability.md
#     STABLE CONFIRMED  delta <= 0.0003803   (3 x production scatter 0.000126775)
#     DIAGNOSTIC-SCALE  delta >= 0.0014459   (1/3 x diagnostic spread 0.004337639)
#     UNRESOLVED        in between           -> a THIRD run, not a re-reading of two
#
# WHY. 0.5126033 passed the adopted CLM-012 criterion with margin +0.0180209 -- 142 production
# scatters if its wrapper is in the stable family, 4.2 diagnostic spreads if it is not. Code reading
# (8b8f238) says stable: closure_powered_annealed_lr.py overrides exactly {__init__, CompileModel,
# RunModel}, the production set, versus the diagnostic's six. But the two MEASURED families differ in
# BOTH override set and driver version, so that attribution is confounded. This measures it instead.
#
# EXPECTED NON-ZERO EXIT, DECLARED IN ADVANCE. closure_powered_truth_reweight.py:105 hardcodes
# RESIDUAL_OVER_GAP_MAX = 0.20 -- the bar CLM-012 RETIRED on 2026-08-09 -- and exits 3 when its own
# literal is unmet. That is why 56552326 reads FAILED in sacct despite completing and writing its
# products, and why its reading block never ran (set -e killed the script first). This launcher
# tolerates exit 3 AND ONLY exit 3, then asserts the report exists and carries a numeric recovery.
# NO THRESHOLD IS ALTERED: the retired bar is not consulted for the verdict, and the adopted
# criterion is applied by the validator exactly as always. Handling a known exit code is not raising
# a tolerance -- masking the products, which is what happened last time, is the actual failure.
#
# NO PROMOTION. NO ENGINE EDIT. niter 3. Branch C closed.
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
# The 56552326 run's own recorded shas -- if these drift, this is not a repeat of that job.
EXPECTED_ENGINE="3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa"
EXPECTED_WRAPPER="ce9f11f4872dd611932705e36f4ecfb651f8ee8eed796cca98be598d92fbb911"
EXPECTED_DRIVER="a45fae7c3f978c34bf73f35ab56aac668439c5784a3968b4f09799ee6090fd48"

REPORT="${OUTDIR}/${MARK}.POWERED_CLOSURE_ANNEALED.slurm-${JOB}.json"
ARTIFACT="${OUTDIR}/${MARK}.POWERED_CLOSURE_ANNEALED.slurm-${JOB}.npz"
PFRECEIPT="${OUTDIR}/${MARK}.PREFLIGHT.slurm-${JOB}.json"
WEIGHTS="${OUTDIR}/weights_stab_${JOB}"
RUNLOG="${OUTDIR}/logs/pc_stab_${JOB}.log"

mkdir -p "${OUTDIR}/logs" "$WEIGHTS"
die() { echo "[pcstab] FATAL: $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
pin() { local p="$1" want="$2" got; [[ -f "$p" ]] || die "missing $p"; got=$(sha_of "$p"); [[ "$got" == "$want" ]] || die "hash drift $p: $got != $want"; }

echo "[pcstab] job=${JOB} host=$(hostname) $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "[pcstab] THIS PRODUCT IS NOT QUOTABLE. Stability measurement, not a new result."
pin "$ENGINE" "$EXPECTED_ENGINE"
pin "$WRAPPER" "$EXPECTED_WRAPPER"
pin "$DRIVER" "$EXPECTED_DRIVER"
gs="$(sha_of "$INPUTS")"
[[ "$gs" == "$EXPECTED_INPUTS_SHA" ]] || die "inputs sha mismatch: $gs" 3
echo "[pcstab] pins HOLD -- engine/wrapper/driver/inputs identical to 56552326's recorded shas"

module load tensorflow/2.15.0
export MNV_REPO="$REPO"
export PYTHONPATH="${REPO}/omnifold_nn${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONUNBUFFERED=1
cd "$PET"

# BEN-083: assert the LOADED module, not the path. Cheap, and the only evidence the run measured
# what it claims. BEN-075: probe every import up front.
python3 -c "
import inspect, hashlib, tensorflow, omnifold
from omnifold import MultiFold
from closure_powered_annealed_lr import install_annealed_multifold
import closure_powered_annealed_lr as w, closure_powered_truth_reweight as cpt
for mod, want in ((w, '${EXPECTED_WRAPPER}'), (cpt, '${EXPECTED_DRIVER}')):
    h = hashlib.sha256(open(mod.__file__,'rb').read()).hexdigest()
    print('[pcstab] resolved', mod.__name__, h[:16])
    assert h == want, f'WRONG MODULE LOADED: {mod.__file__} {h}'
A, _ = install_annealed_multifold()
assert 'early_stop' in inspect.signature(A.__init__).parameters
ov = {n for n in ('__init__','cache','CompileModel','RunModel','RunStep1','RunStep2') if n in A.__dict__}
print('[pcstab] annealed override set:', sorted(ov))
assert ov == {'__init__','CompileModel','RunModel'}, f'override set changed: {sorted(ov)}'
" || die "import / loaded-module / override-set preflight failed" 4
echo "[pcstab] preflight OK -- override set is the PRODUCTION set, as read at 8b8f238"

set +e
python3 "$PREFLIGHT" --inputs "$INPUTS" --json "$PFRECEIPT" --inputs-sha256 "$gs" >>"$RUNLOG" 2>&1
pf_rc=$?
set -e
[[ $pf_rc -eq 0 ]] || die "preflight gate refused the run (rc=${pf_rc})" "$pf_rc"

# Whole stream to a file; filter READS of it (BEN-026). Exit 3 is the retired-bar exit, declared above.
set +e
srun -n 1 -c 32 --gpus=1 python3 -u "$WRAPPER" \
  --inputs "$INPUTS" --json "$REPORT" --artifact "$ARTIFACT" --weights-folder "$WEIGHTS" \
  >>"$RUNLOG" 2>&1
rc=$?
set -e
if [[ $rc -ne 0 && $rc -ne 3 ]]; then die "closure failed with rc=${rc} (only 3, the retired-bar exit, is expected)" "$rc"; fi
[[ $rc -eq 3 ]] && echo "[pcstab] closure exited 3 = the RETIRED-bar self-report, expected and declared; products below are intact"
[[ -s "$REPORT" ]] || die "no report written despite rc=${rc}" 5

# Apply the PREDECLARED three-branch reading. Reports, never decides.
python3 - "$REPORT" <<'PY'
import json, sys
REF, T_STABLE, T_DIAG = 0.5126032761517403, 0.0003803, 0.0014459
rep = json.load(open(sys.argv[1]))
m = rep.get("metrics") or {}
rec = m.get("recovery")
print("[pcstab] ===== PREDECLARED READING (three branches) =====")
print(f"[pcstab] reference (56552326) = {REF!r}")
print(f"[pcstab] this run  recovery   = {rec!r}")
if rec is None:
    print("[pcstab] VERDICT: NO RECOVERY REPORTED -- inconclusive, fail closed")
else:
    d = abs(float(rec) - REF)
    print(f"[pcstab] delta = {d:.9f}")
    print(f"[pcstab]   STABLE   <= {T_STABLE}  (3 x production scatter 0.000126775)")
    print(f"[pcstab]   DIAGNOSTIC >= {T_DIAG}  (1/3 x diagnostic spread 0.004337639)")
    if d <= T_STABLE:
        v = ("STABLE CONFIRMED -- the override-set attribution is right and RETIRED as an inference. "
             "The D2 pass stands, margin ~142 scatters; the k=3 restatement may re-derive from it")
    elif d >= T_DIAG:
        v = ("DIAGNOSTIC-SCALE -- the override-set attribution is WRONG. 0.5126033 is one draw; the D2 "
             "PASS, the +0.0180209 margin and the -0.03424972 trade-off all need n>=2 before being quoted")
    else:
        v = ("UNRESOLVED -- neither follows. Next step is a THIRD powered-closure run, NOT a re-reading "
             "of these two. Do NOT read this as leaning either way")
    print(f"[pcstab] VERDICT: {v}")
    for k in ("gap", "floor", "residual", "residual_over_gap"):
        if k in m: print(f"[pcstab]   ingredient {k} = {m[k]}")
print("[pcstab] No promotion. No threshold touched. niter 3. Branch C closed.")
PY
echo "[pcstab] DONE $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
