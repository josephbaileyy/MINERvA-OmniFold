#!/bin/bash
#SBATCH --job-name=fe_s1lr2
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu&a100
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=08:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/step1_iteration_dynamics/logs/s1lr_r2_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/step1_iteration_dynamics/logs/s1lr_r2_%j.err
#
# Changed attempt matching the diagnosed 56531057 import failure. The pending 56531204 launcher has
# the same missing PYTHONPATH. This version preserves all pins and adds an explicit import preflight.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PET="${REPO}/nd-unfolding/pet"
BASE="${PET}/step1_iteration_dynamics"
WRAPPER="${PET}/diagnose_step1_annealed_lr.py"
HELPER="${PET}/diagnose_step1_iteration_dynamics.py"
DRIVER="${PET}/train_fullevent_nominal.py"
LOADER="${PET}/fullevent_fps_dataloader.py"
ENGINE="${REPO}/omnifold_nn/omnifold/omnifold.py"
INPUTS="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
TARGET="${REPO}/nd-unfolding/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy"
TARGET_RECEIPT="${REPO}/nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json"
GATE3="${REPO}/docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json"

EXPECTED_WRAPPER="fa4ad80aee1457d851c82d426c565a35a2a522da12bcc858d0c6a1c8e5d980ad"
EXPECTED_HELPER="831117d84866d644a681e434dcf7c43de886e9393c61e582f4fae1cccd597288"
EXPECTED_DRIVER="66aa1f8f62087e6ef6ca79928aca954ed25aea1bb304d71e8dbf159ec417dadd"
EXPECTED_LOADER="57f33f87b07e0c6b9bd27a8c56f8013acf9863c72f80f1c01de556ad09f97117"
EXPECTED_ENGINE="3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa"
EXPECTED_TARGET="544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9"
EXPECTED_TARGET_RECEIPT="336e8e27fc8afce813f3ee743c6466ea047243c6e4f457e1d040868d5800792f"
EXPECTED_GATE3="306e54596802623693cab3657164851b3880563ef8fb59ce3d2627062480cd2f"

die() { echo "[s1lr-r2][FAIL] $*" >&2; exit 1; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
pin() { local p="$1" want="$2" got; [[ -f "$p" ]] || die "missing $p"; got=$(sha_of "$p"); [[ "$got" == "$want" ]] || die "hash drift $p: $got != $want"; }

[[ -n "${SLURM_JOB_ID:-}" ]] || die "must run as a real Slurm job"
pin "$WRAPPER" "$EXPECTED_WRAPPER"
pin "$HELPER" "$EXPECTED_HELPER"
pin "$DRIVER" "$EXPECTED_DRIVER"
pin "$LOADER" "$EXPECTED_LOADER"
pin "$ENGINE" "$EXPECTED_ENGINE"
pin "$TARGET" "$EXPECTED_TARGET"
pin "$TARGET_RECEIPT" "$EXPECTED_TARGET_RECEIPT"
pin "$GATE3" "$EXPECTED_GATE3"
[[ -s "$INPUTS" ]] || die "missing/empty Gate-2 source $INPUTS"

NS="${BASE}/warm_fixed_annealed_lr/slurm-${SLURM_JOB_ID}"
WEIGHTS="${NS}/weights.npz"
RESULT="${NS}/STEP1_DYNAMICS.json"
[[ ! -e "$WEIGHTS" && ! -e "${WEIGHTS}.done" && ! -e "$RESULT" ]] \
  || die "collision in job-owned namespace $NS"
mkdir -p "$NS" "${BASE}/logs"

source "${REPO}/setup_salloc_env.sh"
module load tensorflow/2.15.0
export PYTHONPATH="${REPO}/omnifold_nn${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONUNBUFFERED=1
python3 -c 'import omnifold, omnifold.omnifold' \
  || die "omnifold import preflight failed with PYTHONPATH=${REPO}/omnifold_nn"

python3 -u "$WRAPPER" \
  --inputs "$INPUTS" \
  --target-npy "$TARGET" \
  --target-receipt "$TARGET_RECEIPT" \
  --gate3-manifest "$GATE3" \
  --out "$WEIGHTS" \
  --result-json "$RESULT"

python3 - "$RESULT" <<'PY'
import json, math, sys
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text())
assert d.get("schema") == "pet-step1-iteration-dynamics-arm-v1"
assert d.get("status") == "COMPLETE" and d.get("arm") == "warm_fixed_annealed_lr"
assert d.get("publication_candidate") is False and len(d.get("rows", [])) == 3
lr=d.get("fit_lr_records", [])
assert len(lr) == 6
assert [round(float(x["learning_rate"]), 7) for x in lr] == [0.0001,0.0001,0.00001,0.00001,0.00001,0.00001]
assert all(math.isfinite(float(r[k])) for r in d["rows"] for k in
           ("r1_mean_w_reco","r1_required_mean","r1_achieved_over_required","push_mean_w_reco"))
print(json.dumps({"validation":"PASS", "arm":d["arm"], "iteration2":d["rows"][2]}, sort_keys=True))
PY

echo "[s1lr-r2] DONE result=${RESULT}"
