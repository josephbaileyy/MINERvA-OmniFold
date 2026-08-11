#!/bin/bash
#SBATCH --job-name=fe_traj_ann
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_nominal_annealed/logs/fe_traj_ann_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_nominal_annealed/logs/fe_traj_ann_%j.err
#
# DOES THE BRANCH C ITERATION-DYNAMICS DEFECT SURVIVE THE LR ANNEAL?
#
# Job 56525829 localized a training defect to iteration dynamics after initial feedback, on the
# artifact trained 2026-08-08 -- BEFORE the fit-time LR anneal was adopted 2026-08-10. KNOWN_ISSUES.md
# :407-443 names that dead anneal a candidate mechanism for the degradation. An annealed production
# artifact now exists (56563761) and the trajectory has never been run on it, so the campaign does not
# know whether the defect is a property of the estimator or of a retired LR policy.
#
# NO TRAINING. Both arms load saved per-iteration checkpoints and evaluate them. The annealed artifact
# carries the same checkpoint inventory as the pre-anneal one, and the harness resolves its checkpoint
# folder from the artifact's own inference_contract["weights_folder"], so no code change is needed.
#
# PREDECLARED, three-branch, UNRESOLVED is a real outcome:
#   docs/orchestration/PREDECLARATION-20260811-annealed-step1-trajectory.md
# Read the verdict on end_to_end_achieved_over_required, NOT on the first-leg field. Note the
# predeclaration's most likely single outcome is UNRESOLVED via the domain-of-validity guard:
# |required - 1| < 0.02 means the sign carries NO INFORMATION, which is not a pass.
#
# WHY A NEW LAUNCHER RATHER THAN AN EDIT. sbatch_step1_trajectory.sh is cited by the 56525829 record;
# 115 sbatch_* names are load-bearing provenance and are not renamed or repurposed (CLAUDE.md).
#
# ARM 1 IS A POSITIVE CONTROL AND IT RUNS FIRST. It re-runs the pre-anneal trajectory gated against the
# COMMITTED STEP1_DECOMPOSITION.slurm-56445883.json receipt. If it does not reproduce, the instrument is
# not established and arm 2 is not read at all, whatever it printed. Arm 2's own gate is a same-session
# self-consistency check, which is strictly weaker -- arm 1 is what licenses believing it.
set -eo pipefail

# This launcher is intentionally single-rank.  A bare srun inside a multi-GPU
# allocation inherits the allocation's task count; the first interactive hedge
# consequently started four copies, three of which failed in Horovod GPU
# selection while one entered ARM 1.  Refuse that shape before importing
# TensorFlow or opening any output so a routing mistake cannot create a partial
# control/treatment namespace.
STEP_TASKS="${SLURM_STEP_NUM_TASKS:-${SLURM_NTASKS:-1}}"
STEP_PROCID="${SLURM_PROCID:-0}"
if [[ "$STEP_TASKS" != "1" || "$STEP_PROCID" != "0" ]]; then
  echo "[traj-ann] FATAL: single-rank launcher received tasks=${STEP_TASKS} procid=${STEP_PROCID}; use srun --ntasks=1 --gpus-per-task=1" >&2
  exit 64
fi

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PET="${REPO}/nd-unfolding/pet"
JOB="${SLURM_JOB_ID:-nojob}"

PRE="${PET}/fullevent_nominal"
ANN="${PET}/fullevent_nominal_annealed"
LOG_DIR="${ANN}/logs"
RUNLOG="${LOG_DIR}/step1_traj_ann_${JOB}.log"

# Arm 1 (control) outputs
CTRL_TRAJ="${ANN}/STEP1_TRAJECTORY.control-prenneal.slurm-${JOB}.json"
# Arm 2 (treatment) outputs
ANN_GATEAB="${ANN}/GATE_AB_PUSH_PROVENANCE.slurm-${JOB}.json"
ANN_DECOMP="${ANN}/STEP1_DECOMPOSITION.slurm-${JOB}.json"
ANN_TRAJ="${ANN}/STEP1_TRAJECTORY.slurm-${JOB}.json"

mkdir -p "$LOG_DIR"
module load tensorflow/2.15.0
export MNV_REPO="$REPO"
# BEN-081: hash-pinning a package file does not make its package importable. omnifold_nn is placed on
# the path by train_fullevent_nominal at import time, but state it explicitly rather than relying on
# an import side effect of another module.
export PYTHONPATH="${REPO}/omnifold_nn:${REPO}/nd-unfolding:${PET}${PYTHONPATH:+:$PYTHONPATH}"
cd "$PET"

# Whole stream to a file, then filter READS of it. Never truncated at write time (BEN-026).
{
  echo "=== fe_traj_ann job ${JOB} on $(hostname) at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

  # ---- PREFLIGHT: prove the import path resolves AND bind which copy loaded ----------------------
  # BEN-081: run the actual imports before any GPU work. BEN-083: sys.path[0] is the executed script's
  # own directory and outranks PYTHONPATH, so a pin on a path proves nothing about which copy was
  # imported -- hash module.__file__ AFTER import and print it. This is the only evidence in the run
  # that it measured what it claims to.
  python3 -u - <<'PYEOF'
import hashlib, importlib, os, sys
print("[preflight] sys.executable", sys.executable)
import train_fullevent_nominal as T          # must come first: it puts omnifold_nn on sys.path
mods = {"train_fullevent_nominal": T}
for name in ("omnifold", "extract_fullevent_fps", "fullevent_fps_dataloader",
             "step1_increment_trajectory", "step1_pull_push_decomposition",
             "gate_ab_push_provenance"):
    mods[name] = importlib.import_module(name)
for name, m in mods.items():
    f = getattr(m, "__file__", None)
    if not f:
        print(f"[preflight] {name}: no __file__ (namespace package)"); continue
    h = hashlib.sha256(open(f, "rb").read()).hexdigest()
    print(f"[preflight] {name:<32} {h[:16]}  {os.path.realpath(f)}")
from omnifold import PET  # the class the harness actually builds
print("[preflight] omnifold.PET resolved OK")
print("[preflight] PASS")
PYEOF

  # ---- ARM 1: CONTROL -- reproduce 56525829 against the COMMITTED receipt ------------------------
  echo "=== ARM 1 (CONTROL, pre-anneal): trajectory gated on committed 56445883 decomposition"
  python3 -u step1_increment_trajectory.py \
    --weights "${PRE}/pet_fullevent_nominal_weights.npz" \
    --decomposition-receipt "${PRE}/STEP1_DECOMPOSITION.slurm-56445883.json" \
    --json "$CTRL_TRAJ"

  # ---- ARM 2: TREATMENT -- the annealed artifact, full three-stage chain -------------------------
  echo "=== ARM 2 (TREATMENT, annealed 56563761): gates A/B"
  python3 -u gate_ab_push_provenance.py \
    --artifact "${ANN}/pet_fullevent_nominal_weights.npz" \
    --json "$ANN_GATEAB"

  echo "=== ARM 2: step-1 pull/push decomposition"
  python3 -u step1_pull_push_decomposition.py \
    --artifact "${ANN}/pet_fullevent_nominal_weights.npz" \
    --gate-receipt "$ANN_GATEAB" \
    --json "$ANN_DECOMP"

  echo "=== ARM 2: per-iteration trajectory"
  python3 -u step1_increment_trajectory.py \
    --weights "${ANN}/pet_fullevent_nominal_weights.npz" \
    --decomposition-receipt "$ANN_DECOMP" \
    --json "$ANN_TRAJ"

  echo "=== DONE at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
} >>"$RUNLOG" 2>&1

echo "[traj-ann] rc=0"
echo "  control  : ${CTRL_TRAJ}"
echo "  annealed : ${ANN_TRAJ}"
echo "  gates    : ${ANN_GATEAB}"
echo "  decomp   : ${ANN_DECOMP}"
echo "  log      : ${RUNLOG}"
