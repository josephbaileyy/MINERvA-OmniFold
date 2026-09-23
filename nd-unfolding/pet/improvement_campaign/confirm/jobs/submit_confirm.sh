#!/bin/bash
# Submit a run manifest as a self-chaining gpu_debug job and, optionally, race it against
# full-node copies in other QOS: whichever copy STARTS first claims $OUT/race-*/winner, cancels
# the other copies this submission created (their ids are recorded here, and the winner checks
# they are still this user's `pv1-chain` jobs before cancelling), and runs the manifest; a copy
# that starts after the winner exits at once. Chained resubmissions never race.
#
#   submit_confirm.sh <checkout> <manifest, relative to confirm/> <out dir> [race QOS ...]
#   e.g. submit_confirm.sh $C runs/v1-infrastructure.tsv $T/v1 regular preempt
#
# The race copies are full nodes (4 GPUs) with RACE_TIME (default 03:00:00: `preempt` refused a
# 01:30:00 request as matching no policy, job submission 2026-09-23); `preempt` copies are
# submitted with --requeue (the runs resume bit-exactly after a preemption). A copy stops as soon
# as every row is COMPLETE, so the limit is a cap, not a charge.
set -euo pipefail
MINE=$(realpath "$1"); MANIFEST=$2; OUT=$(realpath -m "$3"); shift 3
SHA=$(git -C "$MINE" rev-parse HEAD)
[[ -z "$(git -C "$MINE" status --porcelain)" ]] || { echo "dirty checkout $MINE" >&2; exit 2; }
case "$OUT" in /pscratch/sd/j/josephrb/campaign-20260920*) echo "refusing historical output dir" >&2; exit 2;; esac
SELF="$MINE/nd-unfolding/pet/improvement_campaign/confirm/jobs/sbatch_confirm_chain.sh"
[[ -f "$MINE/nd-unfolding/pet/improvement_campaign/confirm/$MANIFEST" ]]
mkdir -p "$OUT"
RACE_DIR=""
if (( $# > 0 )); then RACE_DIR="$OUT/race-$(date +%Y%m%dT%H%M%S)"; mkdir -p "$RACE_DIR"; fi
ENV="ALL,MINE=$MINE,MINE_COMMIT=$SHA,OUT=$OUT,MANIFEST=$MANIFEST,RACE_DIR=$RACE_DIR"
J=$(sbatch --parsable -q debug -t 00:30:00 -o "$OUT/slurm-%j.out" --export="$ENV" "$SELF")
echo "debug chain: $J"
[[ -n "$RACE_DIR" ]] && touch "$RACE_DIR/submitted-$J"
for QOS in "$@"; do
  EXTRA=(); [[ "$QOS" == preempt ]] && EXTRA=(--requeue)
  R=$(sbatch --parsable -q "$QOS" -t "${RACE_TIME:-03:00:00}" "${EXTRA[@]}" \
        -o "$OUT/slurm-%j.out" --export="$ENV" "$SELF")
  touch "$RACE_DIR/submitted-$R"
  echo "race copy ($QOS): $R"
done
