#!/bin/bash
#SBATCH --job-name=g6_ml_traj
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:00:00
#SBATCH --array=1-5
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_ml_ensemble/trajectory/logs/g6_traj_%A_%a.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_ml_ensemble/trajectory/logs/g6_traj_%A_%a.err
#
# Gate 6 Leg 1: zero-training trajectory decomposition of every predeclared
# ensemble member.  Each task reads one isolated member and writes only its own
# job/task namespace.  No C_ML construction or estimator promotion occurs.
set -eo pipefail

die() { echo "[g6-traj] FATAL: $*" >&2; exit 64; }

TASK="${SLURM_ARRAY_TASK_ID:-}"
[[ "$TASK" =~ ^[1-5]$ ]] || die "array task must be 1..5, got ${TASK:-<unset>}"
[[ "${SLURM_NTASKS:-1}" == "1" ]] || die "launcher is single-rank"

SCI_REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
CODE_REPO="${GATE6_CODE_REPO:-/pscratch/sd/j/josephrb/gate6-reconcile-56834281}"
CODE_PET="${CODE_REPO}/nd-unfolding/pet"
SCI_PET="${SCI_REPO}/nd-unfolding/pet"
MEMBER_DIR="${SCI_PET}/fullevent_ml_ensemble/member_${TASK}"
ARTIFACT="${MEMBER_DIR}/pet_fullevent_ml_member${TASK}_weights.npz"
DONE="${ARTIFACT}.done"
TARGET="${SCI_REPO}/nd-unfolding/g2_fullevent/gate2/final/superseded-20260813-pre-gate5-rerun/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy"
TARGET_SHA="544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9"
RUN_ID="${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-nojob}}_${TASK}"
OUT_DIR="${MEMBER_DIR}/trajectory"
GATE="${OUT_DIR}/GATE_AB_PUSH_PROVENANCE.slurm-${RUN_ID}.json"
DECOMP="${OUT_DIR}/STEP1_DECOMPOSITION.slurm-${RUN_ID}.json"
TRAJ="${OUT_DIR}/STEP1_TRAJECTORY.slurm-${RUN_ID}.json"
LOCK="${OUT_DIR}/.writer-${RUN_ID}.lock"

mkdir -p "$OUT_DIR"
exec 9>"$LOCK"
flock -n 9 || die "writer lock is already held: $LOCK"
for output in "$GATE" "$DECOMP" "$TRAJ"; do
  [[ ! -e "$output" ]] || die "refusing to overwrite $output"
done
[[ -f "$ARTIFACT" && -f "$DONE" ]] || die "member ${TASK} artifact/done pair incomplete"
[[ -f "$TARGET" ]] || die "archived target is absent: $TARGET"

case "$TASK" in
  1) ARTIFACT_SHA="3e08850d44f773bb50f5cb132a7a1d4d672e0ab15f1d38d785a4eddbf5179b2e" ;;
  2) ARTIFACT_SHA="5b8e129f9dba90659ed0fc17f322499ea41fea505add57ab957ad209152f1c13" ;;
  3) ARTIFACT_SHA="f6087581e320d1bfce1a968e62c737d8fac346dedb94836f7fe173980a5b55e8" ;;
  4) ARTIFACT_SHA="04759d0a07f120bda112b87222b0a91fd0e98a2ce402be12d37f30d06a2a0bfd" ;;
  5) ARTIFACT_SHA="4120a5483255847e9dceb79dc5796dd820fca419cfba8adddabc42924d82eff1" ;;
esac
[[ "$(sha256sum "$ARTIFACT" | awk '{print $1}')" == "$ARTIFACT_SHA" ]] || die "artifact hash mismatch"
[[ "$(sha256sum "$TARGET" | awk '{print $1}')" == "$TARGET_SHA" ]] || die "archived target hash mismatch"

declare -A CODE_SHA=(
  [diagnostic_target_override.py]="3f2ee2d2dc39c58c0ba71dc85ad1560ecab7166082ce418864701a6f5ee78671"
  [gate_ab_push_provenance.py]="fd181aeba1e43b4ddfe6fc257f7ce39dc95b74834fee16feb9caf72d313d6c95"
  [step1_pull_push_decomposition.py]="175edde3860da313cf07024514922a0b1a89fb802aaaa94abdf120674f92fabe"
  [step1_increment_trajectory.py]="48f8353d6c06f78823314ad81e2e1412fb9b81f3705257a406e8e6dad4518296"
  [train_fullevent_nominal.py]="91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc"
  [fullevent_fps_dataloader.py]="e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1"
  [extract_fullevent_fps.py]="de0f044b612782edb58e152205b426e6dbbca7637b7f3f342a1373fe4dc7d51a"
)
for file in "${!CODE_SHA[@]}"; do
  [[ "$(sha256sum "${CODE_PET}/${file}" | awk '{print $1}')" == "${CODE_SHA[$file]}" ]] || die "code hash mismatch: $file"
done
[[ "$(sha256sum "${CODE_REPO}/omnifold_nn/omnifold/omnifold.py" | awk '{print $1}')" == "3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa" ]] || die "engine hash mismatch"

module load tensorflow/2.15.0
export PYTHONUNBUFFERED=1
export MNV_REPO="$SCI_REPO"
export PYTHONPATH="${CODE_REPO}/omnifold_nn:${CODE_REPO}/nd-unfolding:${CODE_PET}${PYTHONPATH:+:$PYTHONPATH}"
cd "$CODE_PET"

# Fail before model construction unless the artifact resolves to this task's
# isolated 3-iteration, eight-checkpoint namespace.
python3 -u - "$ARTIFACT" "$MEMBER_DIR" "$TASK" <<'PYEOF'
import json, os, sys
import numpy as np
artifact, member_dir, task = sys.argv[1:]
with np.load(artifact, allow_pickle=True) as data:
    contract = data["inference_contract"].item()
    policy = data["seed_policy"].item()
folder = os.path.realpath(contract["weights_folder"])
expected_folder = os.path.realpath(os.path.join(member_dir, "w_nominal"))
if folder != expected_folder:
    raise SystemExit(f"weights_folder collision: {folder} != {expected_folder}")
if int(policy["niter"]) != 3:
    raise SystemExit(f"niter changed: {policy['niter']}")
name = contract["multifold_name"]
expected = sorted(
    [f"OmniFold_{name}_iter{i}_step{s}.weights.h5" for i in range(3) for s in (1, 2)]
    + [f"OmniFold_{name}_iter2_step{s}_final.weights.h5" for s in (1, 2)]
)
actual = sorted(x for x in os.listdir(folder) if x.endswith(".weights.h5"))
if actual != expected:
    raise SystemExit(f"checkpoint inventory mismatch: {actual}")
print(json.dumps({"member": int(task), "weights_folder": folder,
                  "checkpoint_count": len(actual), "preflight": "PASS"}, sort_keys=True))
PYEOF

echo "[g6-traj] member=${TASK} run_id=${RUN_ID} host=$(hostname) start=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 -u gate_ab_push_provenance.py \
  --artifact "$ARTIFACT" --json "$GATE" \
  --precomputed-target-override "$TARGET" \
  --precomputed-target-sha256 "$TARGET_SHA"
python3 -u step1_pull_push_decomposition.py \
  --artifact "$ARTIFACT" --gate-receipt "$GATE" --json "$DECOMP" \
  --precomputed-target-override "$TARGET" \
  --precomputed-target-sha256 "$TARGET_SHA"
python3 -u step1_increment_trajectory.py \
  --weights "$ARTIFACT" --decomposition-receipt "$DECOMP" --json "$TRAJ" \
  --precomputed-target-override "$TARGET" \
  --precomputed-target-sha256 "$TARGET_SHA"
echo "[g6-traj] member=${TASK} rc=0 trajectory=${TRAJ} end=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
