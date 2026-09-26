#!/bin/bash
# PET2-hybrid smoke test: every row of a pet2 manifest (e.g. P2pre then P2scr on one replicate) in
# ONE gpu_shared allocation, each through nd-unfolding/mnv_guarded_run.py from a clean checkout
# pinned at MINE_COMMIT, then scored by the predecessor's UNCHANGED confirm/score_replicate.py.
# Device-level GPU memory is sampled by nvidia-smi beside the run (the driver records the TF
# allocator's peak per step); host peak RSS comes from /usr/bin/time -v.
#   env: MINE MINE_COMMIT OUT MANIFEST (relative to MINE)
#        [STOP_AFTER=0] [THEIRS_CACHE=$OUT/theirs-cache.npz] [ITER_ESTIMATE=1200]
#   sbatch -A m3246_g -C gpu -q shared -G 1 -c 32 -t 01:00:00 \
#          --export=ALL,MINE=..,MINE_COMMIT=..,OUT=..,MANIFEST=.. sbatch_pet2_smoke.sh
#SBATCH --job-name=pfd-pet2-smoke
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}" ; : "${MANIFEST:?}"
case "$(realpath -m "$OUT")" in
  /pscratch/sd/j/josephrb/pet-final-design-20260925/*) ;;
  *) echo "OUT must be under the study namespace" >&2; exit 2;;
esac
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]] || { echo "checkout not at $MINE_COMMIT" >&2; exit 2; }
[[ -z "$(git -C "$MINE" status --porcelain)" ]] || { echo "checkout not clean" >&2; exit 2; }
mkdir -p "$OUT"
scontrol show job -o "$SLURM_JOB_ID" > "$OUT/allocation-$SLURM_JOB_ID.txt"
source "$MINE/nd-unfolding/pet/improvement_campaign/confirm/jobs/confirm_lib.sh"   # INPUTS SIDECAR POOLS POPULATIONS C V GUARD
setup_env
nvidia-smi --query-gpu=uuid,name,memory.total --format=csv > "$OUT/gpu-$SLURM_JOB_ID.csv"
END_UNIX=$(date -d "$(squeue -h -j "$SLURM_JOB_ID" -o %e)" +%s)
DEADLINE=$(( END_UNIX - 240 ))
RUNNER="$MINE/nd-unfolding/pet/final_design/pet2/run_pet2_replicate.py"
nvidia-smi --query-gpu=timestamp,memory.used,memory.total,utilization.gpu --format=csv,nounits \
  -l 2 > "$OUT/nvsmi-$SLURM_JOB_ID.csv" &
SMI=$!
trap 'kill $SMI 2>/dev/null || true' EXIT
status=0
while IFS=$'\t' read -r name cfg hash selection distortion ref extra runner; do
  [[ -z "$name" || "$name" == \#* ]] && continue
  [[ "$runner" == final_design/pet2/run_pet2_replicate.py ]] || { echo "$name: runner $runner" >> "$OUT/exit-codes.txt"; status=1; continue; }
  RUN="$OUT/$name"; mkdir -p "$RUN"
  echo "$name start $(date +%s.%N)" >> "$OUT/phases-$SLURM_JOB_ID.txt"
  /usr/bin/time -v python "$GUARD" --expect-root "$MINE" \
    --inventory "$RUN/guard-$SLURM_JOB_ID.json" --label "PET2-$name" \
    -- "$RUNNER" --config "$V/$cfg" --config-hash "$hash" --repo "$MINE" --out "$RUN" \
    --inputs-npz "$INPUTS" --identity-sidecar "$SIDECAR" --populations "$POPULATIONS" \
    --pool "${selection%%:*}" --replicate "${selection##*:}" --pools-npz "$POOLS" \
    --manifest "$C/pools/POOL_MANIFEST.json" --distortion "$distortion" \
    --theirs-cache "${THEIRS_CACHE:-$OUT/theirs-cache.npz}" \
    --deadline-unix "$DEADLINE" --first-iteration-estimate-s "${ITER_ESTIMATE:-1200}" \
    --stop-after-iteration "${STOP_AFTER:-0}" $extra \
    >> "$RUN/run-$SLURM_JOB_ID.log" 2>&1 || { echo "$name exit $? (job $SLURM_JOB_ID)" >> "$OUT/exit-codes.txt"; status=1; }
  echo "$name end $(date +%s.%N)" >> "$OUT/phases-$SLURM_JOB_ID.txt"
  if [[ -s "$RUN/receipt.json" ]]; then
    python "$GUARD" --expect-root "$MINE" --inventory "$RUN/guard-score-$SLURM_JOB_ID.json" \
      --label "PET2-score-$name" -- "$V/score_replicate.py" --run "$RUN" \
      >> "$RUN/score-$SLURM_JOB_ID.log" 2>&1 || { echo "$name score exit $?" >> "$OUT/exit-codes.txt"; status=1; }
  fi
done < "$MINE/$MANIFEST"
[[ -z "$(git -C "$MINE" status --porcelain)" ]] || status=1
echo "status $status" >> "$OUT/phases-$SLURM_JOB_ID.txt"
exit $status
