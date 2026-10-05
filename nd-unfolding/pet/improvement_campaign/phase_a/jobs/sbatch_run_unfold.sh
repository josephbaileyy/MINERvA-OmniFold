#!/bin/bash
# Task A1: the campaign driver (run_unfold.py) on one GPU, through the guard with NO --allow:
# nothing may load from another tree. CONFIGS is a space-separated list of RunConfig JSONs
# (paths relative to phase_a/configs); REFERENCE_DIR, if set, holds the runtime audit's
# runtime_audit_<arm>.json, whose input digests the driver must reproduce.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu&hbm40g
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --time=00:30:00
#SBATCH --job-name=pa1-unfold
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}" ; : "${CONFIGS:?}"
INPUTS=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
INDEX=/pscratch/sd/j/josephrb/campaign-20260920/join
case "$OUT" in /pscratch/sd/j/josephrb/campaign-20260920*) echo "refusing historical output dir" >&2; exit 2;; esac
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]]
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
mkdir -p "$OUT"
scontrol show job -o "$SLURM_JOB_ID" > "$OUT/allocation-$SLURM_JOB_ID.txt"
nvidia-smi --query-gpu=uuid,name,memory.total --format=csv > "$OUT/gpu-$SLURM_JOB_ID.csv"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 NVIDIA_TF32_OVERRIDE=0
module load tensorflow/2.15.0
C="$MINE/nd-unfolding/pet/improvement_campaign"
status=0
for CFG in $CONFIGS; do
  NAME=$(basename "$CFG" .json); ARM=${NAME##*_}
  RUN="$OUT/$NAME"; mkdir -p "$RUN"; cd "$RUN"
  EXTRA=()
  [[ -n "$REFERENCE_DIR" ]] && EXTRA+=(--reference-digests "$REFERENCE_DIR/runtime_audit_$ARM.json")
  [[ "$ARM" == theirs ]] && EXTRA+=(--theirs-index "$INDEX" --theirs-cache "${THEIRS_CACHE:?}")
  python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" \
    --inventory "$RUN/guard.json" --label "A1-$NAME" \
    -- "$C/run_unfold.py" --config "$C/phase_a/configs/$CFG" --repo "$MINE" --out "$RUN" \
    --inputs-npz "$INPUTS" --identity-sidecar "$SIDECAR" "${EXTRA[@]}" \
    > "$RUN/run.log" 2>&1 || { echo "$NAME exit $?" >> "$OUT/exit-codes.txt"; status=1; }
done
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
[[ $status == 0 ]] && echo COMPLETE > "$OUT/terminal-$SLURM_JOB_ID.txt" || echo FAILED > "$OUT/terminal-$SLURM_JOB_ID.txt"
exit $status
