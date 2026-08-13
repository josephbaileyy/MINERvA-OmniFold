#!/bin/bash
#SBATCH --job-name=g6_floor
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
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_floor_42_0/logs/g6_floor_%A_%a.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_floor_42_0/logs/g6_floor_%A_%a.err
#
# Gate 6 Leg F: the ACROSS-PROCESS FLOOR at the fixed member-1 policy (42,0).
# Rule fixed before any draw existed:
#   docs/orchestration/PREDECLARATION-20260813-gate6-floor-replication.md
#
# THIS IS A MEASUREMENT, NOT A RETRY. Every draw uses the IDENTICAL seed pair (42,0); what varies is
# the process, node and GPU. That is why it proceeds under `do_not_retry_unchanged`. It constructs no
# C_ML, promotes nothing, moves no central, starts no Leg 2, and selects no subset. Gate 6 stays
# BLOCKED whatever this returns.
#
# DRAW 1 IS THE EXISTING member_1 ARTIFACT AND IS NOT RETRAINED. This array is tasks 2-5 only, so
# member_1 is never opened for writing and its trajectory value is reused as the fifth data point.
#
# WHY A NEW LAUNCHER RATHER THAN A FLAG ON AN EXISTING ONE -- the same reasoning
# sbatch_pet_fullevent_ml_ensemble.sh:20-26 gives, and it still holds: train_fullevent_nominal.py is
# `/files/driver/path` in the live p3f-pet-gate4-launch-code-gate receipt, so editing it converts a
# code change into a code-gate RE-ISSUE plus re-attestation of every pin. This file touches none of
# them. The ensemble launcher itself also cannot serve: it hard-refuses any MID outside 1..5 ("a sixth
# member is not authorized"), which is correct for the ensemble and wrong for same-policy replicates.
#
# ONE JOB PER DRAW, FOUR STAGES. Training runs the SCIENCE repo's driver, byte-for-byte what the five
# members ran; the three no-training diagnostics run the CODE repo's pinned copies, byte-for-byte what
# array 56847059 verified. Every one of those digests is asserted below before any GPU work starts.
#
# Submit:  sbatch --array=2-5%2 sbatch_pet_fullevent_floor_replicate_array.sh
set -eo pipefail

die() { echo "[g6-floor] FATAL: $*" >&2; exit "${2:-64}"; }

DRAW="${SLURM_ARRAY_TASK_ID:-${DRAW_ID:?set DRAW_ID or submit as an array}}"
[[ "$DRAW" =~ ^[2-5]$ ]] || die "draw must be 2..5 (draw 1 is the existing member_1 and is NOT retrained), got ${DRAW}" 3
[[ "${SLURM_NTASKS:-1}" == "1" ]] || die "launcher is single-rank; Horovod and rank slicing are prohibited here" 3

# ---- THE POLICY. Identical for every draw -- that is the whole point of this leg. --------------
EST=42
SUB=0

SCI_REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
CODE_REPO="${G6_FLOOR_CODE_REPO:-/pscratch/sd/j/josephrb/gate6-reconcile-56834281}"
CODE_PET="${CODE_REPO}/nd-unfolding/pet"
SCI_PET="${SCI_REPO}/nd-unfolding/pet"
DRIVER="${SCI_PET}/train_fullevent_nominal.py"
INPUTS="${SCI_REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
INPUTS_SHA="fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
TARGET="${SCI_REPO}/nd-unfolding/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy"
TARGET_SHA="544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9"
RECEIPT="${SCI_REPO}/nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json"
GATE3_MANIFEST="${SCI_REPO}/docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json"
MEMBER1="${SCI_PET}/fullevent_ml_ensemble/member_1/pet_fullevent_ml_member1_weights.npz"

FLOORDIR="${SCI_PET}/fullevent_floor_42_0"
DRAWDIR="${FLOORDIR}/draw_${DRAW}"
OUT="${DRAWDIR}/pet_fullevent_floor_draw${DRAW}_weights.npz"
RUN_ID="${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-nojob}}_${DRAW}"
GATE="${DRAWDIR}/GATE_AB_PUSH_PROVENANCE.slurm-${RUN_ID}.json"
DECOMP="${DRAWDIR}/STEP1_DECOMPOSITION.slurm-${RUN_ID}.json"
TRAJ="${DRAWDIR}/STEP1_TRAJECTORY.slurm-${RUN_ID}.json"
ENVID="${DRAWDIR}/EXECUTION_ENVIRONMENT.slurm-${RUN_ID}.json"
LOCK="${DRAWDIR}/.writer-${RUN_ID}.lock"

mkdir -p "${FLOORDIR}/logs" "$DRAWDIR"

# SOLE WRITER. flock, then refuse every output that already exists -- the collision-isolation the
# member array used, applied per draw.
exec 9>"$LOCK"
flock -n 9 || die "writer lock is already held: $LOCK" 4
for o in "$OUT" "$OUT.done" "$GATE" "$DECOMP" "$TRAJ" "$ENVID"; do
  [[ ! -e "$o" ]] || die "refusing to overwrite $o -- remove nothing, investigate" 4
done

# ---- FAIL CLOSED ON DATA IDENTITY, before the module load and before any GPU work. -------------
[[ -s "$INPUTS" ]] || die "inputs missing: $INPUTS"
[[ -s "$TARGET" ]] || die "target missing: $TARGET"
[[ -s "$RECEIPT" ]] || die "Gate-2 receipt missing: $RECEIPT"
[[ -s "$GATE3_MANIFEST" ]] || die "Gate-3 manifest missing: $GATE3_MANIFEST"
[[ -s "$MEMBER1" ]] || die "member_1 artifact missing: $MEMBER1 -- draw 1 is the reference"
got="$(sha256sum "$INPUTS" | cut -d' ' -f1)"
[[ "$got" == "$INPUTS_SHA" ]] || die "inputs sha mismatch: $got != $INPUTS_SHA" 3
got="$(sha256sum "$TARGET" | cut -d' ' -f1)"
[[ "$got" == "$TARGET_SHA" ]] || die "target sha mismatch: $got != $TARGET_SHA -- this is NOT the array
the five members consumed, so a floor measured against it would not be a floor" 3
echo "[g6-floor] data identity verified: inputs ${INPUTS_SHA:0:16} target ${TARGET_SHA:0:16}"

# ---- FAIL CLOSED ON CODE IDENTITY. The training trio must be what the members ran, and the three
# diagnostics must be what array 56847059 verified. A floor is only a floor under the same code.
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
echo "[g6-floor] code identity verified: 2 science + 7 code-repo files + both engines"

# ---- EXECUTION-ENVIRONMENT IDENTITY. The OI-15 residual, and the thing an across-process floor
# exists to expose. Written by the LAUNCHER into a sidecar, because the driver that would otherwise
# carry it is a live Gate-4 pin. Shape copied from train_fullevent_replica.py:347-353.
GPU_ID="$(nvidia-smi --query-gpu=uuid,name --format=csv,noheader 2>/dev/null | tr '\n' ';')"
SCI_HEAD="$(cd "$SCI_REPO" && git rev-parse HEAD 2>/dev/null || echo unknown)"
CODE_HEAD="$(cd "$CODE_REPO" && git rev-parse HEAD 2>/dev/null || echo unknown)"
cat > "$ENVID" <<JSON
{
  "schema_version": 1,
  "leg": "gate6-leg-F-across-process-floor",
  "predeclaration": "docs/orchestration/PREDECLARATION-20260813-gate6-floor-replication.md",
  "draw": ${DRAW},
  "requested_seed_policy": {"estimator_seed": ${EST}, "subsample_seed": ${SUB}},
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
  "note": "Same-policy across-process replicate. Draw 1 is the existing member_1 and is not retrained."
}
JSON
python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$ENVID" \
  || die "the execution-environment sidecar I just wrote is not valid JSON" 5
echo "[g6-floor] draw=${DRAW} run_id=${RUN_ID} host=$(hostname) gpu=${GPU_ID}"

# ---- ENVIRONMENT. Exactly the ensemble launcher's sequence, because the members trained under it.
source "${SCI_REPO}/setup_salloc_env.sh"
module load tensorflow/2.15.0
export PYTHONUNBUFFERED=1
export MNV_REPO="$SCI_REPO"
python3 -c "import tensorflow as tf; print('[g6-floor] tensorflow', tf.__version__)" \
  || die "tensorflow not importable after module load -- environment is wrong, not the physics" 5

# ---- STAGE 1: TRAIN. Science repo, defaults for --target-npy/--target-receipt, which now resolve to
# the byte-identical canonical target (verified above). Seeds are the ONLY thing passed.
echo "[g6-floor] STAGE 1/4 TRAIN draw=${DRAW} seeds=(${EST},${SUB}) $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
cd "$SCI_PET"
python3 "$DRIVER" --inputs "$INPUTS" --out "$OUT" --tag nominal \
  --gate3-manifest "$GATE3_MANIFEST" \
  --estimator-seed "$EST" --subsample-seed "$SUB" \
  || die "draw ${DRAW} training failed" 6

# ---- POST-CONDITION on the REALIZED policy, plus the two validity checks the predeclaration adds:
# R must be exactly member 1's, and the subsample must be array-equal to member 1's.
python3 - "$OUT" "$EST" "$SUB" "$DRAW" "$MEMBER1" <<'PY' || die "draw validity check failed" 7
import sys
import numpy as np
out, est, sub, draw, member1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
R_MEMBER1 = 1.1240802949941018
with np.load(out, allow_pickle=True) as z:
    if "seed_policy" not in z:
        raise SystemExit(f"[g6-floor][FAIL] draw {draw}: no seed_policy persisted")
    sp = z["seed_policy"].item()
    tgt = z["target"].item()
    imc = np.asarray(z["mc_indices"])
got = (int(sp["estimator_seed"]), int(sp["subsample_seed"]))
if got != (est, sub):
    raise SystemExit(f"[g6-floor][FAIL] draw {draw}: realized seeds {got} != requested {(est, sub)}")
for k, want in (("niter", 3), ("epochs", 8), ("train_events", 2000000), ("batch_size", 512)):
    if int(sp[k]) != want:
        raise SystemExit(f"[g6-floor][FAIL] draw {draw}: {k}={sp[k]} != {want}")
R = float(tgt["step1_class_ratio"])
if R != R_MEMBER1:
    raise SystemExit(f"[g6-floor][FAIL] draw {draw}: R={R!r} != member 1's {R_MEMBER1!r}; R is "
                     f"subsample-invariant and shared, so this is a different target or inventory")
with np.load(member1, allow_pickle=True) as m:
    imc1 = np.asarray(m["mc_indices"])
if not np.array_equal(imc, imc1):
    raise SystemExit(f"[g6-floor][FAIL] draw {draw}: mc_indices differ from member 1's with "
                     f"subsample_seed={sub} fixed; this is not a same-policy replicate")
print(f"[g6-floor] draw {draw} VALID: realized (42,0), niter=3/epochs=8/rows=2000000/batch=512, "
      f"R exact, subsample array-equal to member 1 ({imc.size} rows)")
PY

# ---- STAGES 2-4: the three no-training diagnostics, from the pinned code repo. No target override:
# the artifact's recorded canonical path exists and holds the certified bytes.
export PYTHONPATH="${CODE_REPO}/omnifold_nn:${CODE_REPO}/nd-unfolding:${CODE_PET}${PYTHONPATH:+:$PYTHONPATH}"
cd "$CODE_PET"
echo "[g6-floor] STAGE 2/4 GATE A/B draw=${DRAW} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 -u gate_ab_push_provenance.py --artifact "$OUT" --json "$GATE" || die "gate A/B failed" 8
echo "[g6-floor] STAGE 3/4 DECOMPOSITION draw=${DRAW} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 -u step1_pull_push_decomposition.py --artifact "$OUT" --gate-receipt "$GATE" \
  --json "$DECOMP" || die "decomposition failed" 8
echo "[g6-floor] STAGE 4/4 TRAJECTORY draw=${DRAW} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 -u step1_increment_trajectory.py --weights "$OUT" --decomposition-receipt "$DECOMP" \
  --json "$TRAJ" || die "trajectory failed" 8

echo "[g6-floor] draw=${DRAW} rc=0 trajectory=${TRAJ} env=${ENVID} end=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "[g6-floor] NO C_ML CONSTRUCTED. NO MEMBER SELECTED. Gate 6 remains BLOCKED at 19585b7."
