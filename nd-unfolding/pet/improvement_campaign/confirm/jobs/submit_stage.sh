#!/bin/bash
# Submit a stage manifest: one self-chaining gpu_debug chain (4 runs per round) PLUS one
# single-GPU gpu_shared copy per row (sbatch_confirm_single.sh); the copies race per run through
# the run's lock (confirm_lib.sh) and a run's pending copy is cancelled once the run is COMPLETE.
#   submit_stage.sh <checkout> <manifest, relative to confirm/> <out dir> [--no-chain]
set -euo pipefail
MINE=$(realpath "$1"); MANIFEST=$2; OUT=$(realpath -m "$3"); NOCHAIN=${4:-}
SHA=$(git -C "$MINE" rev-parse HEAD)
[[ -z "$(git -C "$MINE" status --porcelain)" ]] || { echo "dirty checkout $MINE" >&2; exit 2; }
case "$OUT" in /pscratch/sd/j/josephrb/campaign-20260920*) echo "refusing historical output dir" >&2; exit 2;; esac
J="$MINE/nd-unfolding/pet/improvement_campaign/confirm/jobs"
M="$MINE/nd-unfolding/pet/improvement_campaign/confirm/$MANIFEST"
mkdir -p "$OUT"
ENV="ALL,MINE=$MINE,MINE_COMMIT=$SHA,OUT=$OUT,MANIFEST=$MANIFEST"
if [[ "$NOCHAIN" != --no-chain ]]; then
  C=$(sbatch --parsable -q debug -t 00:30:00 -o "$OUT/slurm-%j.out" --export="$ENV" "$J/sbatch_confirm_chain.sh")
  echo "$(date -u +%FT%TZ) chain $C" | tee -a "$OUT/submissions.txt"
fi
grep -v '^#' "$M" | grep -v '^[[:space:]]*$' | cut -f1 | while read -r ROW; do
  mkdir -p "$OUT/$ROW"
  [[ "$(cat "$OUT/$ROW/status.txt" 2>/dev/null)" == COMPLETE ]] && continue
  S=$(sbatch --parsable -o "$OUT/$ROW/slurm-%j.out" --export="$ENV,ROW=$ROW" "$J/sbatch_confirm_single.sh")
  echo "$S" > "$OUT/$ROW/shared_job"
  echo "$(date -u +%FT%TZ) single $ROW $S" | tee -a "$OUT/submissions.txt"
done
