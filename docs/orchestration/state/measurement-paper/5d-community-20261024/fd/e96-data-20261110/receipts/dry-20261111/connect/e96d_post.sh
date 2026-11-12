#!/bin/bash
# E96D: the poll and post-run read of one stage (dry or full), on a login node from a /dev/shm copy of itself ($1),
# deleted at exit. Read-only on everything but $NEW/post-<stage>.tar.gz (rewritten on each call once the job has
# ended). Prints sacct's row for the stage's job; if the job has not ended it stops there (exit 10, re-run later).
# Once it has ended: the job's .out, DONE or FAILED, the task end and failed markers, and for dry GATE.json and
# gate.log; then packs logs/, log-<stage>/ (no products) and the two queues into post-<stage>.tar.gz and prints its
# sha256. It first prints a stat-only atime reading of the two inputs and (e)'s product. Products under runs/ are pinned by log-<stage>/SHA256SUMS, which the job wrote. No set -u.
SELF=$1; STAGE=$2
NEW=/pscratch/sd/j/josephrb/e96data-20261111
fin() { rm -f -- "$SELF"; exit "$1"; }
case "$STAGE" in dry|full) ;; *) echo "STOP: stage '$STAGE'"; fin 9;; esac
echo "post $STAGE host=$(hostname) utc=$(date -u +%FT%TZ)"
job=$(cat "$NEW/logs/$STAGE.jobid" 2>/dev/null) || { echo "STOP: no $STAGE.jobid"; fin 9; }
echo "job $job"
echo "== atime reading (stat only; the director's ruling for LL5D's gate receipts)"
for f in /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz /pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz \
         /pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz; do
  echo "stat utc=$(date -u +%FT%TZ) $(stat -c 'atime=%X mtime=%Y size=%s %n' "$f")"
done
sacct -j "$job" -X -n -P -o JobID,JobName,State,Start,End,Elapsed,NNodes,TimelimitRaw || { echo "STOP: sacct failed"; fin 9; }
st=$(sacct -j "$job" -X -n -P -o State | head -1)
case "$st" in PENDING*|RUNNING*|REQUEUED*|SUSPENDED*|"") squeue -j "$job" -h -o "%i %j %T %M %l %S %r"; echo "NOT ENDED: $st"; fin 10;; esac
L=$NEW/log-$STAGE
echo "== job .out"; cat "$NEW/logs/e96data_${STAGE}_$job.out"
echo "== receipts"; for f in DONE FAILED; do [ -e "$L/$f" ] && { echo "$f: $(cat "$L/$f")"; }; done
ls "$L" | grep -E '\.(end|failed|teardown)$' | sort | tr '\n' ' '; echo
if [ "$STAGE" = dry ]; then echo "== GATE.json"; cat "$L/GATE.json"; echo "== gate.log"; cat "$L/gate.log"; fi
echo "== SHA256SUMS"; cat "$L/SHA256SUMS"
( cd "$NEW" && tar czf "post-$STAGE.tar.gz.tmp" logs "log-$STAGE" dry.tsv full.tsv && mv "post-$STAGE.tar.gz.tmp" "post-$STAGE.tar.gz" ) || { echo "STOP: tar"; fin 9; }
sha256sum "$NEW/post-$STAGE.tar.gz"
echo "post $STAGE rc=0 state=$st"
fin 0
