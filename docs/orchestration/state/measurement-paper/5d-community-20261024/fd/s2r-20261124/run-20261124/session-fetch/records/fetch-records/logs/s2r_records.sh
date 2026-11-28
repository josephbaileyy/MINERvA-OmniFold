#!/bin/bash
# S2R: the records connect, after the job (S2R-DECLARATION.md section 5). Derived from T3's reviewed read connect
# t3p_read_connect.sh rev 1 (9c4b604c), without the read: s2r_run read its own products in the job.
# On a Perlmutter login node, from a /dev/shm copy of itself whose path is $1; it deletes that copy at exit.
#   usage: s2r_fetch.sh <self> <window_end_epoch> <fence prefixes, comma-separated>
# In order, each failure a final stop before any copy:
#   the window; the fence by sacct (the submit connect's, unchanged);
#   logs/run.jobid names one job, which sacct shows COMPLETED as s2r_run;
#   log/DONE present and no log/STOP or log/FAILED; read/readout.json and read/readout.txt present; fetch-records,
#     fetch-records.tar, .list, .sums and this connect's log and done absent;
#   log/SHA256SUMS has exactly 6 well-formed `<64 hex>  runs/....npz` lines and holds under `sha256sum --strict -c`, and
#     runs/ holds exactly 6 products.
# Then the records: every regular file under logs/, log/, read/ and queues/, and manifest.json, stage.json and fence.txt
# (no .npz; this connect's own log is fetched beside the tar), copied through dd iflag=noatime into
# $OUT/fetch-records/, each copy's sha256 equal to its source's, then one tar, whose sha256 this log prints.
# Writes only $OUT/fetch-records, $OUT/fetch-records.tar, the transient .list and .sums, and its own log and done.
# No set -u. Any stop is final.
SELF=$1; WEND=$2; FENCE=$3
set -o pipefail
TAG=records
OUT=/pscratch/sd/j/josephrb/s2r-20261124
FR=$OUT/fetch-$TAG
bail() { echo "BAIL $*"; rm -f -- "$SELF"; exit 9; }
[[ "$WEND" =~ ^[0-9]{10}$ ]] || bail "window end '$WEND'"
now=$(date +%s); [ "$now" -le "$WEND" ] || bail "the window ended (now $now > $WEND)"
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || bail "fence '$FENCE'"

fence_sacct() {
  local rows bad
  rows=$(sacct -X -n -P -S now-14days -o JobID,JobName,State 2>&1) || { echo "sacct failed: $rows"; return 2; }
  bad=$(printf '%s\n' "$rows" | awk -F'|' -v pre="$FENCE,s2r_" '
    BEGIN { n = split(pre, P, ",") }
    NF >= 3 {
      st = $3; sub(/ by [0-9]+$/, "", st)
      term = (st ~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)$/)
      if (term) next
      for (i = 1; i <= n; i++) if (P[i] != "" && index($2, P[i]) == 1) { print; break }
    }')
  [ -z "$bad" ] || { echo "fenced or s2r_ jobs not terminal: $bad"; return 1; }
  return 0
}
fence_sacct > /dev/null 2>&1 || bail "fence (sacct) not clear"
[ -d "$OUT/logs" ] || bail "no $OUT/logs"
job=$(dd if="$OUT/logs/run.jobid" iflag=noatime status=none 2>/dev/null)
[[ "$job" =~ ^[0-9]+$ ]] || bail "logs/run.jobid '$job'"
row=$(sacct -j "$job" -X -n -P -o JobName,State 2>/dev/null | head -1)
[ "$row" = "s2r_run|COMPLETED" ] || bail "job $job is '$row', not s2r_run|COMPLETED"
[ -s "$OUT/log/DONE" ] && [ ! -e "$OUT/log/STOP" ] && [ ! -e "$OUT/log/FAILED" ] || bail "log/ has no clean DONE"
[ -s "$OUT/read/readout.json" ] && [ -s "$OUT/read/readout.txt" ] || bail "no readout"
for p in "$FR" "$FR.tar" "$FR.sums" "$FR.list" "$OUT/logs/connect-$TAG.log" "$OUT/logs/connect-$TAG.done"; do
  [ ! -e "$p" ] || bail "$p exists"
done
LOG=$OUT/logs/connect-$TAG.log
exec > "$LOG" 2>&1
finish() { echo "s2r $TAG rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-$TAG.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ; echo "window_end_epoch $WEND (now $now); fence prefixes $FENCE"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/s2r_${TAG}.sh"
echo "== fence (sacct)"; fence_sacct || { echo "STOP: fence"; finish 9; }; echo "fence clear"
echo "== the job (sacct)"
sacct -j "$job" -X -n -P -o JobID,JobName,State,ExitCode,Start,End,ElapsedRaw,NNodes | head -1
echo "log/DONE: $(dd if="$OUT/log/DONE" iflag=noatime status=none)"

SUMS="$OUT/log/SHA256SUMS"
[ -f "$SUMS" ] || { echo "STOP: no log/SHA256SUMS"; finish 9; }
nl=$(grep -c '' "$SUMS"); ng=$(grep -cE '^[0-9a-f]{64}  runs/[^[:space:]]+\.npz$' "$SUMS")
echo "log/SHA256SUMS: $nl lines, $ng well-formed product lines (want 6)"
[ "$nl" -eq 6 ] && [ "$ng" -eq 6 ] || { echo "STOP: log/SHA256SUMS is not 6 well-formed lines"; finish 9; }
( cd "$OUT" && sha256sum --strict --quiet -c log/SHA256SUMS ) || { echo "STOP: the products are not log/SHA256SUMS's"; finish 9; }
echo "log/SHA256SUMS: OK"
na=$(find "$OUT/runs" -type f -name '*.npz' | wc -l) || { echo "STOP: find under runs/ failed"; finish 9; }
echo "npz files under runs/: $na"
[ "$na" -eq 6 ] || { echo "STOP: runs/ does not hold exactly 6 products"; finish 9; }
for f in readout.json readout.txt; do
  echo "read/$f sha256 $(dd if="$OUT/read/$f" iflag=noatime status=none | sha256sum | cut -d' ' -f1) bytes $(stat -c %s "$OUT/read/$f")"
done

echo "== records"
date -u +%FT%TZ
mkdir "$FR" || { echo "STOP: mkdir $FR"; finish 9; }
roots=(logs log read queues manifest.json stage.json fence.txt)
( cd "$OUT" && find "${roots[@]}" -type f ! -name '*.npz' ! -name "connect-$TAG.log" -print0 | sort -z ) > "$FR.list" \
  || { echo "STOP: the records list failed (find)"; finish 4; }
fail=0; nf=0
while IFS= read -r -d '' rel; do
  src="$OUT/$rel"
  mkdir -p "$FR/$(dirname "$rel")" || { echo "mkdir failed: $rel"; fail=1; continue; }
  dd if="$src" of="$FR/$rel" iflag=noatime status=none || { echo "copy failed: $rel"; fail=1; continue; }
  a=$(dd if="$src" iflag=noatime status=none | sha256sum | cut -d' ' -f1) || { echo "re-read failed: $rel"; fail=1; continue; }
  b=$(sha256sum "$FR/$rel" | cut -d' ' -f1) || { echo "hash failed: $rel"; fail=1; continue; }
  [ "$a" = "$b" ] || { echo "copy differs: $rel"; fail=1; }
  echo "$b  $rel" >> "$FR.sums" || { echo "sum append failed: $rel"; fail=1; continue; }
  nf=$((nf + 1))
done < "$FR.list"
[ "$fail" -eq 0 ] && [ "$nf" -gt 0 ] || { echo "STOP: a record copy failed or differs, or no records ($nf)"; finish 4; }
nl=$(grep -c '' "$FR.sums") && ng=$(grep -cE '^[0-9a-f]{64}  [^[:space:]].*$' "$FR.sums") \
  || { echo "STOP: the records' sums cannot be counted"; finish 4; }
[ "$nl" -eq "$nf" ] && [ "$ng" -eq "$nf" ] || { echo "STOP: the records' sums hold $nl lines ($ng well-formed) for $nf files"; finish 4; }
rm -f -- "$FR.list"
mv "$FR.sums" "$FR/RECORDS.SHA256SUMS" || finish 4
echo "records copied: $nf files, $(du -sb "$FR" | cut -f1) bytes"
tar -C "$OUT" -cf "$FR.tar" "fetch-$TAG" || { echo "STOP: tar"; finish 4; }
echo "fetch-$TAG.tar sha256 $(sha256sum "$FR.tar" | cut -d' ' -f1) bytes $(stat -c %s "$FR.tar")"
finish 0
