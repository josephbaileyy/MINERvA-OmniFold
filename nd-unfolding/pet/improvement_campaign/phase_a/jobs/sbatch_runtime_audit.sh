#!/bin/bash
# Task A1 Part 1, level-1 evidence: run the historical driver
# (run_arm_evaluation.evaluate at 68cf9d29, unmodified) for both arms on a
# small subsample under phase_a/runtime_audit.py, which only observes.
#
# Guard: the harness lives in the campaign checkout ($MINE, --expect-root).
# The code under test is imported from the pinned historical checkout
# (--allow $HIST), and the historical driver itself puts the hardcoded tree
# /pscratch/sd/j/josephrb/MINERvA-OmniFold at sys.path[0] (OI-136), so that
# tree is --allow'ed too; runtime_audit.py compares every loaded module's git
# blob against `git ls-tree -r 68cf9d29`, which is what makes the allowance
# safe to read. The guard file is unedited (blob 3929da3a in both checkouts).
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu&hbm40g
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --time=00:30:00
#SBATCH --job-name=pa1-audit
set -eo pipefail
: "${HIST:?}" ; : "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}"
: "${MAX_EVENTS:?}" ; : "${STAGE:?}" ; : "${SEED:?}" ; : "${LR:?}"
HIST_COMMIT=68cf9d29f8ab1b0f5acd933d4baec1962b29e34d
HARDCODED=/pscratch/sd/j/josephrb/MINERvA-OmniFold
INPUTS=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
INDEX=/pscratch/sd/j/josephrb/campaign-20260920/join
CKPT=/pscratch/sd/j/josephrb/pet-checkpoints-20260919
case "$OUT" in /pscratch/sd/j/josephrb/campaign-20260920*) echo "refusing historical output dir" >&2; exit 2;; esac

for pair in "$HIST:$HIST_COMMIT" "$MINE:$MINE_COMMIT"; do
  dir=${pair%%:*}; want=${pair##*:}
  [[ "$(git -C "$dir" rev-parse HEAD)" == "$want" ]]
  [[ -z "$(git -C "$dir" status --porcelain)" ]]
done
[[ "$(git -C "$HIST" hash-object nd-unfolding/mnv_guarded_run.py)" == "$(git -C "$MINE" hash-object nd-unfolding/mnv_guarded_run.py)" ]]
mkdir -p "$OUT"
scontrol show job -o "$SLURM_JOB_ID" > "$OUT/allocation-audit.txt"
nvidia-smi --query-gpu=uuid,name,memory.total --format=csv > "$OUT/gpu-audit.csv"
git -C "$HIST" ls-tree -r HEAD > "$OUT/tree-68cf9d29.txt"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 NVIDIA_TF32_OVERRIDE=0
module load tensorflow/2.15.0
CACHE="$OUT/cache/theirs-$STAGE-$MAX_EVENTS.npz"
status=0
cd "$OUT"
for ARM in ours theirs; do
  python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" \
    --allow "$HIST" --allow "$HARDCODED" \
    --inventory "$OUT/guard-audit-$ARM.json" --label "A1-audit-$ARM" \
    -- "$MINE/nd-unfolding/pet/improvement_campaign/phase_a/runtime_audit.py" \
    --historical-repo "$HIST" --tree-listing "$OUT/tree-68cf9d29.txt" \
    --arm "$ARM" --seed "$SEED" --stage "$STAGE" --learning-rate "$LR" --niter 3 \
    --max-events "$MAX_EVENTS" --inputs-npz "$INPUTS" --theirs-index "$INDEX" \
    --theirs-cache "$CACHE" \
    --theirs-state-npz "$CKPT/pretrained_state_s.npz" \
    --theirs-manifest "$CKPT/PRETRAINED_STATE_MANIFEST.json" \
    --identity-sidecar "$SIDECAR" --out-dir "$OUT" \
    --label-root "hardcoded_main_checkout=$HARDCODED" \
    --label-root "campaign_harness_checkout=$MINE" \
    > "$OUT/audit-$ARM.log" 2>&1 || { rc=$?; echo "$ARM exit $rc" >> "$OUT/exit-codes.txt"; status=1; }
done
for dir in "$HIST" "$MINE"; do [[ -z "$(git -C "$dir" status --porcelain)" ]]; done
[[ $status == 0 ]] && echo COMPLETE > "$OUT/terminal-audit.txt" || echo FAILED > "$OUT/terminal-audit.txt"
exit $status
