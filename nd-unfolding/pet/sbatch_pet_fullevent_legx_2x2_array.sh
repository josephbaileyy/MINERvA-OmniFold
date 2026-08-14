#!/bin/bash
#SBATCH --job-name=g6_legx
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:00:00
#SBATCH --nice=10000
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_legx_2x2/logs/g6_legx_%A_%a.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_legx_2x2/logs/g6_legx_%A_%a.err
#
# Gate 6 Leg X: the {42,46}x{0,4} 2x2, READ AT ITERATION 2 ONLY.
# Rule fixed before either new cell existed:
#   docs/orchestration/PREDECLARATION-20260813-gate6-legX-2x2.md
#
# THIS IS A DIAGNOSTIC, NOT A STEP TOWARD C_ML. It answers whether the iteration-2 trajectory depends
# on estimator initialization by more than across-process noise -- a question the executed DIAGONAL
# member table (42,0)...(46,4) makes unanswerable, because estimator init and training subsample are
# perfectly confounded there. It constructs no C_ML, promotes nothing, moves no central, starts no
# Leg 2, and selects no subset. Gate 6 stays BLOCKED at 19585b7 whatever this returns, and all five
# prohibitions there are live: do_not_select_passing_subset, do_not_construct_C_ML, do_not_move_central,
# do_not_start_leg_2, do_not_retry_unchanged. Constructing C_ML needs a separate decision from Joseph
# that he has not made.
#
# TWO OF THE FOUR CELLS ALREADY EXIST AND ARE NOT RETRAINED:
#   A = (42,0) = fullevent_ml_ensemble/member_1   v[2] = 0.9806897311812962
#   B = (46,4) = fullevent_ml_ensemble/member_5   v[2] = 0.7534768706675813
# This array trains only the two that do not:
#   task 1 -> cell C = (42,4)
#   task 2 -> cell D = (46,0)
# Neither member_1 nor member_5 is ever opened for writing, and a range guard refuses any task id
# outside 1..2 by name.
#
# WHY THE READOUT IS RESTRICTED TO ITERATION 2 -- so nobody later reads an unreplicated 2x2 and assumes
# nobody noticed. Leg F measured the across-process spread at ONE fixed seed pair. At iteration 0 it is
# 89.6% of the five-member spread, so main effects there would be indistinguishable from process noise
# at the same apparent precision as a real result. At iteration 2 it is 15.1%, and iteration 2 is where
# the Gate-6 band applies and where Leg F's own verdict is defined. THE RESTRICTION IS WHAT MAKES THE
# DESIGN SOUND, NOT A LIMITATION OF IT. Joseph decided it: "Sure, do iteration 2."
#
# THE FLOOR RUNS FIRST, AND THAT IS ENFORCED BELOW RATHER THAN TRUSTED. A 2x2 with one run per cell has
# one degree of freedom per effect and NO internal error scale; the standard error of every effect is
# exactly the across-process sigma, which only Leg F can supply. This launcher refuses to start unless a
# Leg F result receipt reports n=5, zero invalid draws and a terminal FLOOR_* verdict. A rule that
# depends on an operator remembering it is a rule the 03:00 session inherits and forgets.
#
# WHY A NEW LAUNCHER RATHER THAN A FLAG -- same reason as Leg F and the ensemble launcher:
# train_fullevent_nominal.py is `/files/driver/path` in the live p3f-pet-gate4-launch-code-gate receipt,
# so editing it turns a code change into a code-gate RE-ISSUE plus re-attestation of every pin. This
# file touches none of them. The ensemble launcher cannot serve either: it hard-refuses any MID outside
# 1..5, which is right for the ensemble and wrong for off-diagonal cells.
#
# Submit (ONLY after the floor closes):  sbatch --array=1-2%1 sbatch_pet_fullevent_legx_2x2_array.sh
set -eo pipefail

die() { echo "[g6-legx] FATAL: $*" >&2; exit "${2:-64}"; }

CELL="${SLURM_ARRAY_TASK_ID:-${CELL_ID:?set CELL_ID or submit as an array}}"
[[ "$CELL" =~ ^[1-2]$ ]] || die "cell must be 1 or 2 (1=(42,4), 2=(46,0)); cells (42,0)=member_1 and (46,4)=member_5 ALREADY EXIST and are NOT retrained, got ${CELL}" 3
[[ "${SLURM_NTASKS:-1}" == "1" ]] || die "launcher is single-rank; Horovod and rank slicing are prohibited here" 3

# ---- THE TWO CELLS. Off-diagonal by construction: that is the entire point of this leg. -----------
case "$CELL" in
  1) EST=42; SUB=4 ;;
  2) EST=46; SUB=0 ;;
esac
# Defence in depth: refuse the diagonal even if the table above is later mis-edited. (42,0) and (46,4)
# are the two cells that already exist; retraining either would overwrite a committed Gate-6 member.
if { [[ "$EST" == "42" && "$SUB" == "0" ]] || [[ "$EST" == "46" && "$SUB" == "4" ]]; }; then
  die "cell (${EST},${SUB}) is a DIAGONAL cell that already exists as a committed Gate-6 member -- Leg X trains the OFF-DIAGONAL only" 3
fi

SCI_REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
CODE_REPO="${G6_LEGX_CODE_REPO:-/pscratch/sd/j/josephrb/gate6-reconcile-56834281}"
CODE_PET="${CODE_REPO}/nd-unfolding/pet"
SCI_PET="${SCI_REPO}/nd-unfolding/pet"
DRIVER="${SCI_PET}/train_fullevent_nominal.py"
INPUTS="${SCI_REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
INPUTS_SHA="fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
TARGET="${SCI_REPO}/nd-unfolding/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy"
TARGET_SHA="544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9"
RECEIPT="${SCI_REPO}/nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json"
GATE3_MANIFEST="${SCI_REPO}/docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json"
MEMBER_A="${SCI_PET}/fullevent_ml_ensemble/member_1/pet_fullevent_ml_member1_weights.npz"
MEMBER_B="${SCI_PET}/fullevent_ml_ensemble/member_5/pet_fullevent_ml_member5_weights.npz"
FLOOR_RESULT="${G6_LEGX_FLOOR_RESULT:-${SCI_REPO}/docs/orchestration/state/gate6-floor-replication-result-56863958.json}"

LEGXDIR="${SCI_PET}/fullevent_legx_2x2"
CELLDIR="${LEGXDIR}/cell_${EST}_${SUB}"
OUT="${CELLDIR}/pet_fullevent_legx_${EST}_${SUB}_weights.npz"
RUN_ID="${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-nojob}}_${CELL}"
GATE="${CELLDIR}/GATE_AB_PUSH_PROVENANCE.slurm-${RUN_ID}.json"
DECOMP="${CELLDIR}/STEP1_DECOMPOSITION.slurm-${RUN_ID}.json"
TRAJ="${CELLDIR}/STEP1_TRAJECTORY.slurm-${RUN_ID}.json"
ENVID="${CELLDIR}/EXECUTION_ENVIRONMENT.slurm-${RUN_ID}.json"
LOCK="${CELLDIR}/.writer-${RUN_ID}.lock"

# ---- SEQUENCING GATE. The floor must be CLOSED, not merely started. It runs before `mkdir`, before the
# writer lock, before the module load and before any GPU work -- so a premature submission costs seconds
# and leaves NOTHING behind, not even an empty cell directory. (The first version of this file ran
# `mkdir -p` first; its own test battery caught that the gate then never executed off-cluster, and that
# a refused submission would still have created directories.)
[[ -s "$FLOOR_RESULT" ]] || die "Leg F result receipt absent: ${FLOOR_RESULT}. THE FLOOR RUNS FIRST -- a 2x2 with one run per cell has no internal error scale, so without F_sd[2] there is no threshold and no verdict to reach. Do not work around this by pointing G6_LEGX_FLOOR_RESULT at a partial receipt." 2
python3 - "$FLOOR_RESULT" <<'PY' || die "Leg F has not closed with a usable floor; refusing to start" 2
import json, sys
p = sys.argv[1]
d = json.load(open(p))
inv = d.get("inventory") or {}
n = inv.get("n")
invalid = inv.get("draws_invalid") or []
verdict = d.get("verdict") or ""
stats = d.get("statistics") or {}
if n != 5:
    raise SystemExit(f"[g6-legx][FAIL] floor receipt reports n={n!r}, need 5")
if invalid:
    raise SystemExit(f"[g6-legx][FAIL] floor receipt reports invalid draws {invalid}; a floor with an "
                     f"invalid draw reaches no verdict and supplies no sigma")
if not verdict.startswith("FLOOR_"):
    raise SystemExit(f"[g6-legx][FAIL] floor verdict is {verdict!r}, not a terminal FLOOR_* value")
sd = ((stats.get("2") or {}).get("F_sd_ddof1"))
if not isinstance(sd, float) or not (sd > 0.0):
    raise SystemExit(f"[g6-legx][FAIL] floor F_sd[2] is {sd!r}; the threshold is 2.7764451051977987*sigma "
                     f"and cannot be formed")
mde = 2.7764451051977987 * sd
print(f"[g6-legx] floor CLOSED: n=5, verdict {verdict}, F_sd[2]={sd!r}, "
      f"MDE = t(0.975,4)*sigma = {mde!r}")
PY

mkdir -p "${LEGXDIR}/logs" "$CELLDIR"

# ---- SOLE WRITER. flock, then refuse every output that already exists.
exec 9>"$LOCK"
flock -n 9 || die "writer lock is already held: $LOCK" 4
for o in "$OUT" "$OUT.done" "$GATE" "$DECOMP" "$TRAJ" "$ENVID"; do
  [[ ! -e "$o" ]] || die "refusing to overwrite $o -- remove nothing, investigate" 4
done
# The two existing members are inputs to this leg and must never be written by it.
for m in "$MEMBER_A" "$MEMBER_B"; do
  [[ -s "$m" ]] || die "existing cell artifact missing: $m -- cells A and B are read-only references"
  [[ "$OUT" != "$m" ]] || die "output path collides with a committed Gate-6 member: $m" 4
done

# ---- FAIL CLOSED ON DATA IDENTITY, before the module load and before any GPU work.
[[ -s "$INPUTS" ]] || die "inputs missing: $INPUTS"
[[ -s "$TARGET" ]] || die "target missing: $TARGET"
[[ -s "$RECEIPT" ]] || die "Gate-2 receipt missing: $RECEIPT"
[[ -s "$GATE3_MANIFEST" ]] || die "Gate-3 manifest missing: $GATE3_MANIFEST"
got="$(sha256sum "$INPUTS" | cut -d' ' -f1)"
[[ "$got" == "$INPUTS_SHA" ]] || die "inputs sha mismatch: $got != $INPUTS_SHA" 3
got="$(sha256sum "$TARGET" | cut -d' ' -f1)"
[[ "$got" == "$TARGET_SHA" ]] || die "target sha mismatch: $got != $TARGET_SHA -- this is NOT the array
the existing cells consumed, so the 2x2 would compare cells trained against different targets" 3
echo "[g6-legx] data identity verified: inputs ${INPUTS_SHA:0:16} target ${TARGET_SHA:0:16}"

# ---- FAIL CLOSED ON CODE IDENTITY. Same tables as Leg F, for the same reason: cells A and B were
# trained under exactly these digests, and a 2x2 across different code is not a 2x2.
declare -A SCI_SHA=(
  [train_fullevent_nominal.py]="91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc"
  [fullevent_fps_dataloader.py]="e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1"
)
for f in "${!SCI_SHA[@]}"; do
  got="$(sha256sum "${SCI_PET}/${f}" | cut -d' ' -f1)"
  [[ "$got" == "${SCI_SHA[$f]}" ]] || die "science-repo code hash mismatch: $f ($got)" 3
done
got="$(sha256sum "${SCI_REPO}/omnifold_nn/omnifold/omnifold.py" | cut -d' ' -f1)"
[[ "$got" == "3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa" ]] \
  || die "science-repo engine hash mismatch ($got)" 3

declare -A CODE_SHA=(
  [diagnostic_target_override.py]="3f2ee2d2dc39c58c0ba71dc85ad1560ecab7166082ce418864701a6f5ee78671"
  [gate_ab_push_provenance.py]="fd181aeba1e43b4ddfe6fc257f7ce39dc95b74834fee16feb9caf72d313d6c95"
  [step1_pull_push_decomposition.py]="175edde3860da313cf07024514922a0b1a89fb802aaaa94abdf120674f92fabe"
  [step1_increment_trajectory.py]="48f8353d6c06f78823314ad81e2e1412fb9b81f3705257a406e8e6dad4518296"
  [train_fullevent_nominal.py]="91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc"
  [fullevent_fps_dataloader.py]="e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1"
  [extract_fullevent_fps.py]="de0f044b612782edb58e152205b426e6dbbca7637b7f3f342a1373fe4dc7d51a"
)
for f in "${!CODE_SHA[@]}"; do
  got="$(sha256sum "${CODE_PET}/${f}" | cut -d' ' -f1)"
  [[ "$got" == "${CODE_SHA[$f]}" ]] || die "code-repo hash mismatch: $f ($got)" 3
done
got="$(sha256sum "${CODE_REPO}/omnifold_nn/omnifold/omnifold.py" | cut -d' ' -f1)"
[[ "$got" == "3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa" ]] \
  || die "code-repo engine hash mismatch ($got)" 3
echo "[g6-legx] code identity verified: 2 science + 7 code-repo files + both engines"

# ---- EXECUTION-ENVIRONMENT IDENTITY, per cell. Cells A and B predate this and do NOT carry it; that
# asymmetry is recorded in the predeclaration rather than waived, and it is one reason the FLOOR is the
# reference scale rather than the members.
GPU_ID="$(nvidia-smi --query-gpu=uuid,name --format=csv,noheader 2>/dev/null | tr '\n' ';')"
SCI_HEAD="$(cd "$SCI_REPO" && git rev-parse HEAD 2>/dev/null || echo unknown)"
CODE_HEAD="$(cd "$CODE_REPO" && git rev-parse HEAD 2>/dev/null || echo unknown)"
cat > "$ENVID" <<JSON
{
  "schema_version": 1,
  "leg": "gate6-leg-X-2x2-estimator-vs-subsample",
  "predeclaration": "docs/orchestration/PREDECLARATION-20260813-gate6-legX-2x2.md",
  "cell": {"task": ${CELL}, "estimator_seed": ${EST}, "subsample_seed": ${SUB}, "is_off_diagonal": true},
  "readout_iteration": 2,
  "why_iteration_2_only": "Leg F measured the across-process spread at ONE fixed seed pair: 89.6% of the five-member spread at iteration 0 against 15.1% at iteration 2. At iteration 0 main effects would be indistinguishable from process noise at the same apparent precision as a real result. Iteration 2 is also where the Gate-6 band applies. The restriction is what makes an unreplicated 2x2 sound, not a limitation of it. Joseph's decision: 'Sure, do iteration 2.'",
  "iterations_0_and_1_are_computed_but_INELIGIBLE": true,
  "existing_cells_not_retrained": {"(42,0)": "fullevent_ml_ensemble/member_1", "(46,4)": "fullevent_ml_ensemble/member_5"},
  "floor_receipt_required_and_verified": "${FLOOR_RESULT}",
  "execution": {
    "slurm_job_id": "${SLURM_JOB_ID:-none}",
    "slurm_array_job_id": "${SLURM_ARRAY_JOB_ID:-none}",
    "slurm_array_task_id": "${SLURM_ARRAY_TASK_ID:-none}",
    "host": "$(hostname)",
    "gpu_identity": "${GPU_ID}",
    "started_at_utc": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
    "science_head_at_runtime": "${SCI_HEAD}",
    "code_head_at_runtime": "${CODE_HEAD}"
  },
  "bound_digests": {
    "inputs_npz": "${INPUTS_SHA}",
    "target_npy": "${TARGET_SHA}",
    "gate2_receipt": "$(sha256sum "$RECEIPT" | cut -d' ' -f1)",
    "driver": "${SCI_SHA[train_fullevent_nominal.py]}",
    "loader": "${SCI_SHA[fullevent_fps_dataloader.py]}",
    "engine": "3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa"
  },
  "prohibitions_still_live": ["do_not_select_passing_subset", "do_not_construct_C_ML",
    "do_not_move_central", "do_not_start_leg_2", "do_not_retry_unchanged"],
  "c_ml_construction_allowed": false,
  "is_a_retry": false,
  "is_a_step_toward_c_ml": false,
  "note": "Off-diagonal cell of the {42,46}x{0,4} 2x2. Diagnostic answering seed-versus-estimator. Gate 6 remains BLOCKED at 19585b7 whatever this returns."
}
JSON
python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$ENVID" \
  || die "the execution-environment sidecar I just wrote is not valid JSON" 5
echo "[g6-legx] cell=(${EST},${SUB}) run_id=${RUN_ID} host=$(hostname) gpu=${GPU_ID}"

# ---- ENVIRONMENT. Exactly the ensemble launcher's sequence, because cells A and B trained under it.
source "${SCI_REPO}/setup_salloc_env.sh"
module load tensorflow/2.15.0
export PYTHONUNBUFFERED=1
export MNV_REPO="$SCI_REPO"
python3 -c "import tensorflow as tf; print('[g6-legx] tensorflow', tf.__version__)" \
  || die "tensorflow not importable after module load -- environment is wrong, not the physics" 5

# ---- STAGE 1: TRAIN. Science repo, defaults for --target-npy/--target-receipt. Seeds are the ONLY
# thing that differs from cells A and B.
echo "[g6-legx] STAGE 1/4 TRAIN cell=(${EST},${SUB}) $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
cd "$SCI_PET"
python3 "$DRIVER" --inputs "$INPUTS" --out "$OUT" --tag nominal \
  --gate3-manifest "$GATE3_MANIFEST" \
  --estimator-seed "$EST" --subsample-seed "$SUB" \
  || die "cell (${EST},${SUB}) training failed" 6

# ---- POST-CONDITION on the REALIZED policy, plus the predeclaration's clause 4 and clause 5. Clause 5
# is BY SUBSAMPLE LEVEL, not global: a cell sharing subsample_seed with an existing member must match it
# exactly, and must differ from the other level. A 2x2 whose subsample axis does not move is not a 2x2.
python3 - "$OUT" "$EST" "$SUB" "$MEMBER_A" "$MEMBER_B" <<'PY' || die "cell validity check failed" 7
import sys
import numpy as np
out, est, sub = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
member_a, member_b = sys.argv[4], sys.argv[5]     # A=(42,0), B=(46,4)
R_COMMON = 1.1240802949941018
with np.load(out, allow_pickle=True) as z:
    if "seed_policy" not in z:
        raise SystemExit(f"[g6-legx][FAIL] cell ({est},{sub}): no seed_policy persisted")
    sp = z["seed_policy"].item()
    tgt = z["target"].item()
    imc = np.asarray(z["mc_indices"])
got = (int(sp["estimator_seed"]), int(sp["subsample_seed"]))
if got != (est, sub):
    raise SystemExit(f"[g6-legx][FAIL] realized seeds {got} != requested {(est, sub)}")
for k, want in (("niter", 3), ("epochs", 8), ("train_events", 2000000), ("batch_size", 512)):
    if int(sp[k]) != want:
        raise SystemExit(f"[g6-legx][FAIL] cell ({est},{sub}): {k}={sp[k]} != {want}")
R = float(tgt["step1_class_ratio"])
if R != R_COMMON:
    raise SystemExit(f"[g6-legx][FAIL] cell ({est},{sub}): R={R!r} != the common {R_COMMON!r}; R is "
                     f"subsample-invariant, so this is a different target or inventory")
with np.load(member_a, allow_pickle=True) as m:
    imc_sub0 = np.asarray(m["mc_indices"])
with np.load(member_b, allow_pickle=True) as m:
    imc_sub4 = np.asarray(m["mc_indices"])
same, other = (imc_sub0, imc_sub4) if sub == 0 else (imc_sub4, imc_sub0)
if not np.array_equal(imc, same):
    raise SystemExit(f"[g6-legx][FAIL] cell ({est},{sub}): mc_indices differ from the existing cell at "
                     f"the SAME subsample_seed={sub}; the subsample axis is not reproducible and the "
                     f"2x2's two levels are not what they claim")
if np.array_equal(imc, other):
    raise SystemExit(f"[g6-legx][FAIL] cell ({est},{sub}): mc_indices are IDENTICAL to the other "
                     f"subsample level; the subsample axis does not move and this is not a 2x2")
n_diff = int((imc != other).sum())
print(f"[g6-legx] cell ({est},{sub}) VALID: realized seeds, niter=3/epochs=8/rows=2000000/batch=512, "
      f"R exact, subsample array-equal to the same level and differing from the other in {n_diff} of "
      f"{imc.size} rows")
PY

# ---- STAGES 2-4: the three no-training diagnostics, from the pinned code repo. Iterations 0 and 1 are
# computed and persisted by the trajectory script; the PREDECLARATION makes them ineligible for the
# effect estimates. This launcher does not filter them -- suppressing them would hide the caveat.
export PYTHONPATH="${CODE_REPO}/omnifold_nn:${CODE_REPO}/nd-unfolding:${CODE_PET}${PYTHONPATH:+:$PYTHONPATH}"
cd "$CODE_PET"
echo "[g6-legx] STAGE 2/4 GATE A/B cell=(${EST},${SUB}) $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 -u gate_ab_push_provenance.py --artifact "$OUT" --json "$GATE" || die "gate A/B failed" 8
echo "[g6-legx] STAGE 3/4 DECOMPOSITION cell=(${EST},${SUB}) $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 -u step1_pull_push_decomposition.py --artifact "$OUT" --gate-receipt "$GATE" \
  --json "$DECOMP" || die "decomposition failed" 8
echo "[g6-legx] STAGE 4/4 TRAJECTORY cell=(${EST},${SUB}) $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 -u step1_increment_trajectory.py --weights "$OUT" --decomposition-receipt "$DECOMP" \
  --json "$TRAJ" || die "trajectory failed" 8

echo "[g6-legx] cell=(${EST},${SUB}) rc=0 trajectory=${TRAJ} env=${ENVID} end=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "[g6-legx] EFFECTS ARE READ AT ITERATION 2 ONLY. Iterations 0 and 1 in the receipt above are"
echo "[g6-legx] INELIGIBLE per the predeclaration -- at iteration 0 the same-seed floor is 89.6% of the"
echo "[g6-legx] member spread, so an effect there cannot be told from process noise."
echo "[g6-legx] NO C_ML CONSTRUCTED. NO MEMBER SELECTED. NO MEMBER RETRAINED. Gate 6 remains BLOCKED at 19585b7."
