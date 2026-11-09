#!/bin/bash
# FD-PRR prr_ibu, attempt 3: the post connect (FD-PRR-DECLARATION.md section 10.3; BINDING 1 ruling 7), on a login node, after the
# prr_ibu job has ended; the cap post's pattern (15a7e143). It reads only this study's own files under $OUT and Slurm's
# records, and writes only under $OUT/post-ibu and $OUT/post-ibu.tar.gz{,.sha256}. It runs nothing, repairs nothing
# and relaunches nothing; a STOP, a refused gate or a failed task is reported as it stands. In order:
#   the job id from $OUT/logs/ibu-3.jobid (attempt 3's; ibu.jobid and ibu-2.jobid are attempts 1's and 2's); sacct must show the job ended (not PENDING, RUNNING, REQUEUED or empty);
#   sacct's record of the job and its steps, and the charge, ElapsedRaw x NNodes / 3600 node-h; the study's charge so
#   far over every ended prr_* job;
#   copies of the small receipt files: the ibu connect's logs (logs/*ibu*, the job's .out among them), queues/ibu.tsv,
#   and log-ibu's records (DONE, STOP or FAILED, env.log, verify-stage.log, ibu.log, SHA256SUMS, every .start and .end, the
#   dry run's copied in among them, and each task's .time and .log); the products stay on pscratch, listed by sha256 in
#   log-ibu/SHA256SUMS; ibu has no queue file, no .start, .end or tasks/, so those copies find nothing;
#   a SHA256SUMS over the copies, then one tar.gz of $OUT/post-ibu, its sha256 written beside it for the fetch's check.
# No set -u. Launched from a /dev/shm copy of itself, whose path is $1; it deletes that copy at exit.
SELF=$1
MODE=ibu
OUT=/pscratch/sd/j/josephrb/fd-prr-20261108
P=$OUT/post-$MODE
bail() { rm -f -- "$SELF"; exit 9; }
[ -s "$OUT/logs/$MODE-3.jobid" ] && [ ! -e "$P" ] && [ ! -e "$P.tar.gz" ] || bail
job=$(cat "$OUT/logs/$MODE-3.jobid")
case "$job" in ''|*[!0-9]*) bail ;; esac
state=$(sacct -j "$job" -X -n -P -o State | head -1)
case "$state" in PENDING|RUNNING|REQUEUED|"") bail ;; esac
mkdir -p "$P" || bail
exec > "$P/post.log" 2>&1
finish() { echo "prr $MODE post rc=$1"; date -u +%FT%TZ; echo "$1" > "$P/post.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname)"; date -u +%FT%TZ
echo "post script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$P/prr_${MODE}_post.sh"
echo "job $job state $state"
sacct -j "$job" -P -o JobID,JobName,State,ExitCode,Elapsed,ElapsedRaw,NNodes,AllocCPUS,Start,End,TimelimitRaw,Timelimit \
  > "$P/sacct.txt" 2>&1
cat "$P/sacct.txt"
charge=$(sacct -j "$job" -X -n -P -o ElapsedRaw,NNodes | head -1 | awk -F'|' '{printf "%.4f", $1 * $2 / 3600}')
echo "charge_node_h=$charge (ElapsedRaw x NNodes / 3600; the $MODE limit is 0.5)"
echo "$charge" > "$P/charge_node_h.txt"
sacct -X -n -P -S 2026-11-08T00:00:00 -o JobID,JobName,State,ElapsedRaw,NNodes --name=prr_dry,prr_iter,prr_cap,prr_misc,prr_ibu \
  > "$P/study-charge.txt" 2>&1
cat "$P/study-charge.txt"
echo "study_charged_node_h=$(awk -F'|' '{s += $4 * $5 / 3600} END {printf "%.4f", s}' "$P/study-charge.txt") (cap 27.0)"
mkdir -p "$P/logs" "$P/log-$MODE/tasks" "$P/queues" || finish 9
cp -p "$OUT"/logs/*"$MODE"* "$P/logs/" 2>/dev/null
cp -p "$OUT/queues/$MODE.tsv" "$P/queues/" 2>/dev/null
L=$OUT/log-$MODE
if [ -d "$L" ]; then
  for f in DONE STOP FAILED env.log verify-stage.log ibu.log SHA256SUMS; do [ -e "$L/$f" ] && cp -p "$L/$f" "$P/log-$MODE/"; done
  cp -p "$L"/*.start "$L"/*.end "$P/log-$MODE/" 2>/dev/null
  cp -p "$L"/tasks/* "$P/log-$MODE/tasks/" 2>/dev/null
else
  echo "no log-$MODE: the job refused before it made its log"
fi
echo "copied: $(find "$P" -type f | wc -l) files"
ls -la "$L" 2>/dev/null | head -5; echo "log-$MODE entries: $(ls "$L" 2>/dev/null | wc -l); tasks/: $(ls "$L/tasks" 2>/dev/null | wc -l)"
( cd "$P" && find . -type f ! -name SHA256SUMS ! -name post.log ! -name post.done -print0 | sort -z | xargs -0 sha256sum ) > "$P/SHA256SUMS"
tar -C "$OUT" -czf "$P.tar.gz" "post-$MODE" || finish 5
( cd "$OUT" && sha256sum "post-$MODE.tar.gz" ) > "$P.tar.gz.sha256" || finish 5
cat "$P.tar.gz.sha256"
finish 0
