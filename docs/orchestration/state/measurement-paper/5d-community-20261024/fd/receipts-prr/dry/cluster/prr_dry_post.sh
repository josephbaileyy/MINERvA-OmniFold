#!/bin/bash
# FD-PRR dry run: the post connect (FD-PRR-DECLARATION.md section 10.3; BINDING 1 ruling 7), on a login node, after the
# prr_dry job has ended. It reads only this study's own files under $OUT and Slurm's records, and writes only under
# $OUT/post-dry. It runs nothing, repairs nothing and relaunches nothing; a STOP or a refused staging is reported as it
# stands. In order:
#   the job id from $OUT/logs/dry.jobid; sacct must show the job ended (not PENDING, RUNNING, REQUEUED or empty);
#   sacct's record of the job and its steps, and the charge, ElapsedRaw x NNodes / 3600 node-h;
#   copies of the small receipt files: the connect's logs, the manifest, stage.json, the queues, and log-dry's records
#   (DONE, STOP or FAILED, pair.json, env.log, the stage and pair logs, SHA256SUMS, each task's .start, .end, .time and
#   .log); the products themselves stay on pscratch, listed by sha256 in log-dry/SHA256SUMS;
#   a SHA256SUMS over the copies, then one tar.gz of $OUT/post-dry for the lane to fetch.
# No set -u. Launched from a /dev/shm copy of itself, whose path is $1; it deletes that copy at exit.
SELF=$1
OUT=/pscratch/sd/j/josephrb/fd-prr-20261108
P=$OUT/post-dry
bail() { rm -f -- "$SELF"; exit 9; }
[ -s "$OUT/logs/dry.jobid" ] && [ ! -e "$P" ] || bail
job=$(cat "$OUT/logs/dry.jobid")
case "$job" in ''|*[!0-9]*) bail ;; esac
state=$(sacct -j "$job" -X -n -P -o State | head -1)
case "$state" in PENDING|RUNNING|REQUEUED|"") bail ;; esac
mkdir -p "$P" || bail
exec > "$P/post.log" 2>&1
finish() { echo "prr dry post rc=$1"; date -u +%FT%TZ; echo "$1" > "$P/post.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname)"; date -u +%FT%TZ
echo "post script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$P/prr_dry_post.sh"
echo "job $job state $state"
sacct -j "$job" -P -o JobID,JobName,State,ExitCode,Elapsed,ElapsedRaw,NNodes,AllocCPUS,Start,End,TimelimitRaw,Timelimit \
  > "$P/sacct.txt" 2>&1
cat "$P/sacct.txt"
charge=$(sacct -j "$job" -X -n -P -o ElapsedRaw,NNodes | head -1 | awk -F'|' '{printf "%.4f", $1 * $2 / 3600}')
echo "charge_node_h=$charge (ElapsedRaw x NNodes / 3600; the dry limit is 5.25)"
echo "$charge" > "$P/charge_node_h.txt"
mkdir -p "$P/logs" "$P/log-dry/tasks" "$P/queues" || finish 9
cp -p "$OUT"/logs/* "$P/logs/" 2>/dev/null
cp -p "$OUT/manifest.json" "$OUT/stage.json" "$P/" 2>/dev/null
cp -p "$OUT"/queues/*.tsv "$P/queues/" 2>/dev/null
L=$OUT/log-dry
if [ -d "$L" ]; then
  for f in DONE STOP FAILED pair.json pair.log env.log stage.log SHA256SUMS; do [ -e "$L/$f" ] && cp -p "$L/$f" "$P/log-dry/"; done
  cp -p "$L"/*.start "$L"/*.end "$P/log-dry/" 2>/dev/null
  cp -p "$L"/tasks/* "$P/log-dry/tasks/" 2>/dev/null
else
  echo "no log-dry: the job refused before it made its log"
fi
echo "copied: $(find "$P" -type f | wc -l) files"
ls -la "$L" 2>/dev/null
( cd "$P" && find . -type f ! -name SHA256SUMS ! -name post.log ! -name post.done -print0 | sort -z | xargs -0 sha256sum ) > "$P/SHA256SUMS"
tar -C "$OUT" -czf "$OUT/post-dry.tar.gz" post-dry || finish 5
sha256sum "$OUT/post-dry.tar.gz"
finish 0
