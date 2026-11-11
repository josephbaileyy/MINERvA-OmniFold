#!/bin/bash
# E96D full run: the submission (E96D-BINDING-1 at M_E96D 1d25f8e7; Joseph's go of 2026-11-11). Runs on a login node
# from a /dev/shm copy of itself whose path is $1; it deletes that copy at exit. In order:
#   the time cutoff: stop if it is later than 2026-11-11T10:15:00Z (the full run's 3:30 must end before the 14:00Z
#     maintenance);
#   the fence: stop if a cov2d*/t2a* job, or any e96data* job, of ours is queued or running;
#   the dry run's receipts: log-dry/DONE at M_E96D, no FAILED, and GATE.json pass true at M_E96D, its
#     full_queue_sha256 equal to full.tsv's and to the digest sent (the job script checks these again);
#   the deploy: HEAD at M_E96D and clean apart from ignored files (the dry job's caches);
#   iris: stop unless the 4.0 node-h cap is at most half of m3246's remaining balance;
#   a stat of the two inputs and (e)'s product, with atimes (stat only);
#   one sbatch: sbatch_e96data.sh full at M_E96D, --time=3:30:00, job name e96data_full, and --deadline at
#     2026-11-11T13:59:00Z written in the cluster's local time (Slurm reads --deadline as local time); scontrol's
#     TimeLimit must read 03:30:00 and its Deadline the same local time, or the job is cancelled at once.
# Writes only under $NEW/logs. No set -u.
SELF=$1
M=1d25f8e791c503f8ef2ef6f6642546ee2008cc41
NEW=/pscratch/sd/j/josephrb/e96data-20261111
D=$NEW/deploy
CAP=4.0
TLIMIT_ARG=3:30:00
TLIMIT=03:30:00
JOBNAME=e96data_full
FULL_SHA=3d49f92f915dfaa58d3d4660441aece8bcd1861659a2aa0fdf87d543ce14c21a
CUTOFF_UTC=2026-11-11T10:15:00Z
DEADLINE_UTC=2026-11-11T13:59:00Z
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
EPROD=/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ -d "$NEW/logs" ] && [ ! -e "$NEW/logs/full.jobid" ] && [ ! -e "$NEW/log-full" ] || { echo "STOP: no logs dir, or a full run exists"; rm -f -- "$SELF"; exit 9; }
LOG=$NEW/logs/connect-full.log
exec > >(tee -a "$LOG") 2>&1
finish() { echo "e96data full submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$NEW/logs/connect-full.done"; rm -f -- "$SELF"; sleep 1; exit "$1"; }
echo "node $(hostname) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$NEW/logs/e96d_full_submit.sh"

echo "== the time cutoff"
now=$(date -u +%s); cut=$(date -u -d "$CUTOFF_UTC" +%s); dl=$(date -u -d "$DEADLINE_UTC" +%s)
echo "now=$now cutoff=$cut ($CUTOFF_UTC) deadline=$dl ($DEADLINE_UTC)"
[ -n "$cut" ] && [ -n "$dl" ] && [ "$now" -le "$cut" ] || { echo "STOP: past the 10:15Z cutoff; the full run waits until after the maintenance"; finish 11; }
DL_LOCAL=$(date -d "$DEADLINE_UTC" +%Y-%m-%dT%H:%M:%S)
echo "deadline in the cluster's local time ($(date +%Z)): $DL_LOCAL"

echo "== the fence (a cov2d*/t2a* or e96data* job stops)"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$NEW/logs/squeue-before-full.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
cat "$NEW/logs/squeue-before-full.txt"
hit=$(awk -F'|' '$2 ~ /^(cov2d|t2a|e96data)/' "$NEW/logs/squeue-before-full.txt")
[ -z "$hit" ] || { echo "FENCE STOP:"; printf '%s\n' "$hit"; finish 9; }
echo "FENCE: pass"

echo "== the dry run's receipts"
cat "$NEW/log-dry/DONE" 2>/dev/null
[ -s "$NEW/log-dry/DONE" ] && [ ! -e "$NEW/log-dry/FAILED" ] || { echo "STOP: no dry DONE, or a FAILED"; finish 9; }
chk=$( ( source "$D/setup_salloc_env.sh" > /dev/null 2>&1
  python3 -B -c '
import json, sys
d = json.load(open(sys.argv[1])); g = json.load(open(sys.argv[2]))
print("yes" if d.get("pin") == sys.argv[3] and g.get("pass") is True and g.get("pin") == sys.argv[3]
      and g.get("full_queue_sha256") == sys.argv[4] else "no")' "$NEW/log-dry/DONE" "$NEW/log-dry/GATE.json" "$M" "$FULL_SHA" ) )
q=$(sha256sum "$NEW/full.tsv" | cut -d' ' -f1)
echo "dry DONE and GATE at the pin with the sent queue: $chk; full.tsv sha256 $q"
[ "$chk" = yes ] && [ "$q" = "$FULL_SHA" ] || { echo "STOP: the dry receipts or the queue"; finish 9; }

echo "== the deploy"
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M_E96D"; finish 9; }
n=$(git -C "$D" status --porcelain | wc -l); echo "HEAD $M; porcelain lines (ignored files excluded): $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }

echo "== iris"; timeout 120 iris < /dev/null > "$NEW/logs/iris-full.txt" 2>&1; head -2 "$NEW/logs/iris-full.txt"
row=$(grep -E '^m3246 ' "$NEW/logs/iris-full.txt" | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b="$bal" 'BEGIN{printf "%.1f", b/2}') cap=$CAP"
awk -v b="$bal" -v c=$CAP 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the cap is above half the balance"; finish 9; }

echo "== stat (stat only)"
for f in "$NPZ" "$BKG" "$EPROD"; do
  echo "stat utc=$(date -u +%FT%TZ) $(stat -c 'atime=%X mtime=%Y size=%s %n' "$f")" || { echo "STOP: missing $f"; finish 9; }
done
echo "== reservations (read only)"; scontrol show res 2>&1 | grep -E 'ReservationName|StartTime' | head -8

date -u +%FT%TZ
cd "$NEW" || finish 9
sbatch --time=$TLIMIT_ARG --job-name=$JOBNAME --deadline="$DL_LOCAL" --output="$NEW/logs/%x_%j.out" \
  "$D/nd-unfolding/sbatch_e96data.sh" full "$D" "$M" "$NEW" > "$NEW/logs/submit-full.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$NEW/logs/submit-full.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$NEW/logs/submit-full.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "full job $job"; echo "$job" > "$NEW/logs/full.jobid"
sj=$(scontrol show job "$job")
tl=$(printf '%s\n' "$sj" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
dd=$(printf '%s\n' "$sj" | sed -n 's/.*Deadline=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT) Deadline=$dd (sent $DL_LOCAL)"
if [ "$tl" != "$TLIMIT" ] || [ "$dd" != "$DL_LOCAL" ]; then
  scancel "$job"; echo "STOP: TimeLimit or Deadline not as sent; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a %S %r"
finish 0
