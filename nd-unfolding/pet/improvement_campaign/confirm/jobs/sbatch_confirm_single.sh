#!/bin/bash
# One manifest row on ONE GPU in gpu_shared (no 30-min cap): the racing copy of a run that the
# debug chain may also be working on. Takes the run's lock (else exits: the other job holds it),
# resumes it bit-exactly where it stands, runs to COMPLETE within its walltime, scores it.
#   env: MINE MINE_COMMIT OUT MANIFEST ROW (the row's name)  [DEADLINE_MARGIN=180]
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --gpus=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:30:00
#SBATCH --job-name=pv1-single
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}" ; : "${MANIFEST:?}" ; : "${ROW:?}"
case "$(realpath -m "$OUT")" in /pscratch/sd/j/josephrb/campaign-20260920*) exit 2;; esac
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]]
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
source "$MINE/nd-unfolding/pet/improvement_campaign/confirm/jobs/confirm_lib.sh"
LINE=$(manifest_rows | awk -F'\t' -v n="$ROW" '$1==n')
[[ -n "$LINE" ]] || { echo "no row $ROW" >&2; exit 2; }
echo "$(date -u +%FT%TZ) single job $SLURM_JOB_ID started" >> "$OUT/$ROW/lock-history.txt"
if is_complete "$ROW"; then echo "already COMPLETE" >> "$OUT/$ROW/lock-history.txt"; exit 0; fi
require_coherent_flock
claim "$ROW" || { echo "$(date -u +%FT%TZ) single $SLURM_JOB_ID: held by another job, exiting" >> "$OUT/$ROW/lock-history.txt"; exit 0; }
if is_complete "$ROW"; then echo "already COMPLETE (after claim)" >> "$OUT/$ROW/lock-history.txt"; exit 0; fi
setup_env
END_UNIX=$(date -d "$(squeue -h -j "$SLURM_JOB_ID" -o %e)" +%s)
rc=0
run_row "$LINE" "${CUDA_VISIBLE_DEVICES:-0}" $(( END_UNIX - ${DEADLINE_MARGIN:-180} )) || rc=1
is_complete "$ROW" && score_row "$LINE"
release "$ROW"
exit $rc
