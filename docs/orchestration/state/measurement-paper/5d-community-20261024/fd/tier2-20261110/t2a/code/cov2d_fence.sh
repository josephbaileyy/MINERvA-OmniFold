#!/bin/bash
# cov2d_fence.sh (T2-BINDING-1 ruling 1): before T2A's connect, on a Perlmutter login node; reads squeue and sacct only.
# CLEAR (exit 0) only if squeue and sacct both answer and no job of ours whose name starts cov2d or t2a is queued,
# running or otherwise unended in the last 14 days. Anything else is exit 3: a matching job, or either command failing.
# Writes nothing. Launched from a /dev/shm copy of itself, whose path is $1; it deletes that copy at exit.
SELF=$1
fin() { rm -f -- "$SELF"; exit "$1"; }
echo "fence host=$(hostname) utc=$(date -u +%FT%TZ)"
q=$(squeue --me -h -o '%i|%j|%T') || { echo "FENCE REFUSED: squeue failed"; fin 3; }
printf '%s\n' "$q" | sed '/^$/d; s/^/squeue: /'
if printf '%s\n' "$q" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ {f=1} END {exit !f}'; then
  echo "FENCE REFUSED: a cov2d/t2a job is queued or running"; fin 3
fi
s=$(sacct -X -n -P -S "$(date -u -d '14 days ago' +%F)" -o JobID,JobName,State) || { echo "FENCE REFUSED: sacct failed"; fin 3; }
u=$(printf '%s\n' "$s" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/')
[ -z "$u" ] || { printf '%s\n' "$u" | sed 's/^/sacct unended: /'; echo "FENCE REFUSED: an unended cov2d/t2a job in sacct"; fin 3; }
echo "sacct cov2d/t2a rows (14 days): $(printf '%s\n' "$s" | awk -F'|' '$2 ~ /^(cov2d|t2a)/' | wc -l), none unended"
echo "FENCE CLEAR"
fin 0
