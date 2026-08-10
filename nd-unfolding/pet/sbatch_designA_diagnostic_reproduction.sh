#!/bin/bash
#SBATCH --job-name=dA_repro
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=06:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/bisect_designA/logs/dA_repro_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/bisect_designA/logs/dA_repro_%j.err
#
# DESIGN A -- does the 2026-08-09 diagnostic arm (56534117) REPRODUCE?
# Reading FIXED IN ADVANCE, three outcomes:
#   docs/orchestration/PREDECLARATION-20260810-designA-diagnostic-reproduction.md  (committed f1901e5)
#     REPRODUCED  dev in [-0.0121046, -0.0113440]
#     DISSOLVED   dev in [-0.0359893, -0.0352286]
#     UNRESOLVED  anything else -> next step is a SECOND repeat of A, NOT the subclass-isolation run
#
# WHY THE CODE IS STAGED OUTSIDE THE REPO. 56534117 ran train_fullevent_nominal.py at 8f2bcb0
# (sha 66aa1f8f), which constructs a PLAIN MultiFold and takes its anneal entirely from the wrapper's
# `omnifold.MultiFold = AnnealedMultiFold` monkeypatch. HEAD's driver (5fda80df) constructs
# _AnnealedMultiFold itself, so the wrapper's `len(instances) != 1` guard fails fast against it -- the
# harness is fail-closed and CANNOT be run against the current driver. Reproducing 56534117 therefore
# requires its driver. That copy lives in /pscratch/.../bisect_designA/ and NOT in the checkout, so a
# stale-looking driver cannot read as corpus drift to the GBDT lane's sweep guard (mid-PB3, told).
#
# sys.path[0] is the SCRIPT's directory, which outranks PYTHONPATH -- so the wrapper is run FROM the
# staging directory. Running it from ${PET} would silently re-import HEAD's driver and measure nothing.
#
# NO PROMOTION. No threshold touched. niter stays 3. Branch C closed. The 08-08 baseline is asserted
# unchanged before and after. Compute authorized by Joseph 2026-08-10 22:04:41Z.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PET="${REPO}/nd-unfolding/pet"
STAGE="/pscratch/sd/j/josephrb/bisect_designA"
JOB="${SLURM_JOB_ID:-nojob}"

WRAPPER="${STAGE}/diagnose_step1_annealed_lr.py"
HELPER="${STAGE}/diagnose_step1_iteration_dynamics.py"
DRIVER="${STAGE}/train_fullevent_nominal.py"
LOADER="${PET}/fullevent_fps_dataloader.py"
ENGINE="${REPO}/omnifold_nn/omnifold/omnifold.py"
INPUTS="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
TARGET="${REPO}/nd-unfolding/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy"
TARGET_RECEIPT="${REPO}/nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json"
GATE3="${REPO}/docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json"
BASELINE="${PET}/fullevent_nominal/pet_fullevent_nominal_weights.npz"

# EVERY pin is the ORIGINAL launcher's (sbatch_step1_annealed_lr_r2.sh), unchanged. That is the point:
# if these still hold, the staged code IS 56534117's code, byte for byte.
EXPECTED_WRAPPER="fa4ad80aee1457d851c82d426c565a35a2a522da12bcc858d0c6a1c8e5d980ad"
EXPECTED_HELPER="831117d84866d644a681e434dcf7c43de886e9393c61e582f4fae1cccd597288"
EXPECTED_DRIVER="66aa1f8f62087e6ef6ca79928aca954ed25aea1bb304d71e8dbf159ec417dadd"
EXPECTED_LOADER="57f33f87b07e0c6b9bd27a8c56f8013acf9863c72f80f1c01de556ad09f97117"
EXPECTED_ENGINE="3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa"
EXPECTED_TARGET="544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9"
EXPECTED_TARGET_RECEIPT="336e8e27fc8afce813f3ee743c6466ea047243c6e4f457e1d040868d5800792f"
EXPECTED_GATE3="306e54596802623693cab3657164851b3880563ef8fb59ce3d2627062480cd2f"

die() { echo "[dA][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
pin() { local p="$1" want="$2" got; [[ -f "$p" ]] || die "missing $p"; got=$(sha_of "$p"); [[ "$got" == "$want" ]] || die "hash drift $p: $got != $want"; }

[[ -n "${SLURM_JOB_ID:-}" ]] || die "must run as a real Slurm job"
echo "[dA] job=${JOB} host=$(hostname) $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

pin "$WRAPPER" "$EXPECTED_WRAPPER"
pin "$HELPER" "$EXPECTED_HELPER"
pin "$DRIVER" "$EXPECTED_DRIVER"
pin "$LOADER" "$EXPECTED_LOADER"
pin "$ENGINE" "$EXPECTED_ENGINE"
pin "$TARGET" "$EXPECTED_TARGET"
pin "$TARGET_RECEIPT" "$EXPECTED_TARGET_RECEIPT"
pin "$GATE3" "$EXPECTED_GATE3"
[[ -s "$INPUTS" ]] || die "missing/empty Gate-2 source $INPUTS"
echo "[dA] all 8 original pins HOLD -- the staged code is 56534117's code byte for byte"

# The staged driver must differ from HEAD's, or this run measures nothing.
head_driver="$(sha_of "${PET}/train_fullevent_nominal.py")"
[[ "$head_driver" != "$EXPECTED_DRIVER" ]] \
  || die "staged driver == HEAD driver; there is no delta to test" 4
echo "[dA] HEAD driver ${head_driver:0:16} != staged ${EXPECTED_DRIVER:0:16}  (the delta under test)"

[[ -s "$BASELINE" ]] || die "the 2026-08-08 baseline is missing; refusing to run without it" 5
BASE_BEFORE="$(sha_of "$BASELINE")"
echo "[dA] baseline preserved-check, before: ${BASE_BEFORE:0:16}"

NS="${STAGE}/slurm-${JOB}"
WEIGHTS="${NS}/weights.npz"
RESULT="${NS}/STEP1_DYNAMICS.json"
[[ ! -e "$WEIGHTS" && ! -e "${WEIGHTS}.done" && ! -e "$RESULT" ]] || die "collision in $NS"
mkdir -p "$NS" "${STAGE}/logs"

source "${REPO}/setup_salloc_env.sh"
module load tensorflow/2.15.0
# PET is on PYTHONPATH for the loader; the STAGE dir wins for the driver because the wrapper is
# executed from there and sys.path[0] outranks PYTHONPATH.
export PYTHONPATH="${REPO}/omnifold_nn:${PET}${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONUNBUFFERED=1

python3 -c 'import omnifold, omnifold.omnifold' || die "omnifold import preflight failed" 6
# Prove the resolution BEFORE spending three hours on it: the driver that will actually be imported
# must be the staged one. This is the single assumption the whole design rests on.
cd "$STAGE"
python3 -c "
import sys, hashlib
sys.path.insert(0, '${STAGE}')
import train_fullevent_nominal as d
p = d.__file__
h = hashlib.sha256(open(p,'rb').read()).hexdigest()
print('[dA] resolved driver:', p)
print('[dA] resolved sha256:', h)
assert h == '${EXPECTED_DRIVER}', 'WRONG DRIVER RESOLVED -- would have measured HEAD, not 8f2bcb0'
assert not hasattr(d, 'LR_POLICY_ANNEALED'), 'staged driver carries the adopted policy; wrong version'
" || die "driver resolution preflight failed -- refusing to run" 7

echo "[dA] running the 56534117 harness $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 -u "$WRAPPER" \
  --inputs "$INPUTS" \
  --target-npy "$TARGET" \
  --target-receipt "$TARGET_RECEIPT" \
  --gate3-manifest "$GATE3" \
  --out "$WEIGHTS" \
  --result-json "$RESULT"

BASE_AFTER="$(sha_of "$BASELINE")"
[[ "$BASE_AFTER" == "$BASE_BEFORE" ]] \
  || die "THE 2026-08-08 BASELINE WAS MODIFIED (${BASE_BEFORE:0:16} -> ${BASE_AFTER:0:16})" 8
echo "[dA] baseline preserved-check, after: ${BASE_AFTER:0:16} UNCHANGED"

# Apply the PREDECLARED three-branch reading. Reports, never decides; never widens the tolerance.
python3 - "$WEIGHTS" "$RESULT" <<'PY'
import json, sys
import numpy as np
E_DIAG, E_PROD, TOL = -0.011724321, -0.035608971, 3 * 0.000126775
with np.load(sys.argv[1], allow_pickle=True) as z:
    t = z["target"]
    try: t = t.item()
    except Exception: pass
    R = float(t["step1_class_ratio"])
    num = float(np.asarray(z["fold_forward_sum_w_push_reco"]).ravel()[0])
    den = float(np.asarray(z["fold_forward_sum_w_reco"]).ravel()[0])
push = num / den
dev = push / R - 1.0
print("[dA] ===== PREDECLARED READING (three outcomes) =====")
print(f"[dA] push {push:.10f}   R {R:.16f}   dev {dev:+.9f}")
print(f"[dA] tolerance 3 x 0.000126775 = {TOL:.7f}  (BORROWED from the production configuration --")
print( "[dA]   the diagnostic configuration's own scatter is exactly what this run measures)")
print(f"[dA] REPRODUCED window [{E_DIAG-TOL:+.7f}, {E_DIAG+TOL:+.7f}]")
print(f"[dA] DISSOLVED  window [{E_PROD-TOL:+.7f}, {E_PROD+TOL:+.7f}]")
if abs(dev - E_DIAG) <= TOL:
    v = ("REPRODUCED -- -0.011724 is a property of the configuration; the code-path delta is REAL "
         "and the subclass-isolation run becomes a clean one-variable follow-up")
elif abs(dev - E_PROD) <= TOL:
    v = ("DISSOLVED -- 56534117 was never reproducible. The 188x-production-scatter framing collapses "
         "and the FINDING becomes the scatter generalisation itself")
else:
    v = ("UNRESOLVED -- neither conclusion follows. Per the predeclaration the next step is a SECOND "
         "REPEAT OF DESIGN A, not the subclass-isolation run. Do NOT read this as leaning either way")
print(f"[dA] VERDICT: {v}")
try:
    rows = json.load(open(sys.argv[2])).get("rows") or []
    print(f"[dA] in-loop push_mean_w_reco by iteration: "
          f"{[round(r.get('push_mean_w_reco', float('nan')), 10) for r in rows]}")
except Exception as e:
    print(f"[dA] (could not read in-loop trajectory: {e})")
print("[dA] No promotion. No threshold touched. niter 3. Branch C closed. Baseline untouched.")
PY
echo "[dA] DONE $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
