#!/bin/bash
# IBUB connect R, the run (IBUB-DECLARATION.md section 8). On a Perlmutter login node, from a /dev/shm copy of itself
# whose path is $1; it deletes that copy at exit. It follows MSR connect B (msr_build_connect.template.sh): the same
# fences, clone, overlap and records-on-every-stop.
#   usage: ibub_run_connect.sh <self> <window_end_epoch>
#
# In order, each failure a final stop:
#  1. the window;
#  2. cov2d's fence rev 3 (7e81a721, embedded and sha-checked), then this lane's sacct fence: no job named ibub_,
#     ibuchi_, cov2d, t2a, rpd or msr may be unended;
#  3. $N must not exist yet;
#  4. a fresh clone at M: clean, with the ibub files at their sha256;
#  5. the overlap check (ibub_overlap.py run) reads CLEAR;
#  6. the preflight (ibub_unit.py preflight): both references at their pins, and all 600 toy files present;
#  7. the staging (ibub_unit.py stage): $CV, $MC and libRooUnfold.so, O_NOATIME copies at their pins, made read-only;
#  8. sbatch of the one job, named ibub_run, at --time 11:29:00, with the deploy, $N and M as arguments;
#  9. sacct lists the job id (up to 5 minutes), and scontrol shows its name, QOS and limit;
# 10. the clone is unchanged.
#
# The records (logs, stage.json, the job's submission record) are copied with dd iflag=noatime, checked and tarred.
# Writes only $N and /dev/shm/ibub-connect. Nothing goes to CFS. Job states come from sacct only, and squeue is never
# run. No set -u. Any stop is final.
SELF=$1; WEND=$2
set -o pipefail
TAG=run
M=@@M@@
N=/pscratch/sd/j/josephrb/ibub-20261123
D=$N/deploy
FR=$N/fetch-$TAG
SHM=/dev/shm/ibub-connect
PY=$HOME/.conda/envs/root_6_28/bin/python3
FENCE_SHA=7e81a721476da987a0e1262ab2054132bd8440cd49b0dc7a5c4f01d50a310738
PREFIXES=ibub_,ibuchi_,cov2d,t2a,rpd,msr
JOBNAME=ibub_run
LIMIT=11:29:00
bail() { echo "BAIL $*"; rm -rf -- "$SHM"; rm -f -- "$SELF"; exit 9; }   # a precondition failed: nothing in $N
[[ "$WEND" =~ ^[0-9]{10}$ ]] || bail "window end '$WEND'"
now=$(date +%s); [ "$now" -le "$WEND" ] || bail "the window ended (now $now > $WEND)"
[ ! -e "$N" ] || bail "$N exists"
[ ! -e "$SHM" ] || bail "$SHM exists"
[ -x "$PY" ] || bail "no $PY"

# ---- cov2d's fence, rev 3, exactly (embedded, sha-checked), then this lane's sacct fence for every prefix
mkdir -m 700 "$SHM" || bail "mkdir $SHM"
base64 -d > "$SHM/cov2d_fence.sh" <<'B64' || bail "fence decode"
@@FENCE_B64@@
B64
[ "$(sha256sum "$SHM/cov2d_fence.sh" | cut -d' ' -f1)" = "$FENCE_SHA" ] || bail "cov2d_fence.sh is not rev 3"
fence_out=$(bash "$SHM/cov2d_fence.sh" 2>&1); frc=$?
[ "$frc" -eq 0 ] || { printf '%s\n' "$fence_out"; bail "cov2d fence rev 3 not clear (rc $frc)"; }
fence_sacct() {
  local rows bad
  rows=$(sacct -X -n -P -S now-14days -o JobID,JobName,State 2>&1) || { echo "sacct failed: $rows"; return 2; }
  bad=$(printf '%s\n' "$rows" | awk -F'|' -v pre="$PREFIXES" '
    BEGIN { n = split(pre, P, ",") }
    NF == 0 { next }
    NF != 3 || $1 !~ /^[0-9]+([_+].*)?$/ { print "malformed: " $0; next }
    {
      split($3, w, " ")
      term = (w[1] ~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)$/)
      if (term) next
      for (i = 1; i <= n; i++) if (P[i] != "" && index($2, P[i]) == 1) { print; break }
    }') || { echo "fence awk failed"; return 2; }
  [ -z "$bad" ] || { echo "fenced jobs not terminal, or malformed rows: $bad"; return 1; }
  return 0
}
fo=$(fence_sacct 2>&1) || bail "fence (sacct) not clear: $fo"

mkdir -m 700 "$N" "$N/logs" || bail "mkdir $N"
LOG=$N/logs/connect-$TAG.log
exec > "$LOG" 2>&1
RECORDED=0
finish() {
  local rc=$1
  if [ "$RECORDED" -eq 0 ]; then RECORDED=1; records || { [ "$rc" -eq 0 ] && rc=4; }; fi
  echo "ibub $TAG rc=$rc"; date -u +%FT%TZ; echo "$rc" > "$N/logs/connect-$TAG.done"; rm -rf -- "$SHM"; rm -f -- "$SELF"; exit "$rc"
}
records() {
  echo "== records"; date -u +%FT%TZ
  mkdir "$FR" || { echo "records: mkdir $FR failed"; return 1; }
  local rel src a b fail=0 nf=0
  # stage.json exists only after the staging; the test is written so its absence is not a failure under pipefail
  ( cd "$N" && { find logs -type f ! -name "connect-$TAG.log" -print0; [ ! -f stage/stage.json ] || printf 'stage/stage.json\0'; } | sort -z ) > "$FR.list" \
    || { echo "records: the list failed (find)"; return 1; }
  while IFS= read -r -d '' rel; do
    src="$N/$rel"
    mkdir -p "$FR/$(dirname "$rel")" || { echo "mkdir failed: $rel"; fail=1; continue; }
    dd if="$src" of="$FR/$rel" iflag=noatime status=none || { echo "copy failed: $rel"; fail=1; continue; }
    a=$(dd if="$src" iflag=noatime status=none | sha256sum | cut -d' ' -f1) || { echo "re-read failed: $rel"; fail=1; continue; }
    b=$(sha256sum "$FR/$rel" | cut -d' ' -f1) || { echo "hash failed: $rel"; fail=1; continue; }
    [ "$a" = "$b" ] || { echo "copy differs: $rel"; fail=1; }
    echo "$b  $rel" >> "$FR.sums"; nf=$((nf + 1))
  done < "$FR.list"
  [ "$fail" -eq 0 ] && [ "$nf" -gt 0 ] || { echo "records: a copy failed or differs, or none ($nf)"; return 1; }
  rm -f -- "$FR.list"
  mv "$FR.sums" "$FR/RECORDS.SHA256SUMS" || return 1
  echo "records copied: $nf files, $(du -sb "$FR" | cut -f1) bytes"
  tar -C "$N" -cf "$FR.tar" "fetch-$TAG" || { echo "records: tar failed"; return 1; }
  echo "fetch-$TAG.tar sha256 $(sha256sum "$FR.tar" | cut -d' ' -f1) bytes $(stat -c %s "$FR.tar")"
}
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ; echo "window_end_epoch $WEND (now $now); fence prefixes $PREFIXES"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$N/logs/ibub_${TAG}_connect.sh"
echo "== cov2d fence rev 3 ($FENCE_SHA)"; printf '%s\n' "$fence_out"
echo "== fence (sacct)"; fence_sacct || { echo "STOP: fence"; finish 9; }; echo "fence clear"

# ---- the deploy: a fresh clone at M, clean, the ibub files at their sha256
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$N/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
gs=$(git -C "$D" status --porcelain --ignored) || { echo "STOP: git status failed (before)"; finish 9; }
echo "HEAD $M; porcelain --ignored before: '${gs}'"
[ -z "$gs" ] || { echo "STOP: the deploy is not clean"; finish 9; }
( cd "$D/2d-unfolding/ibub" && sha256sum --strict -c ) <<SUMS || { echo "STOP: the ibub files are not the declared ones"; finish 9; }
@@IBUB_SUMS@@
SUMS
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN() { ( cd "$D" && nice -n 19 ionice -c3 env -u PYTHONPATH "$PY" -I -B "$@" ); }
echo "threads 2; nice 19; ionice idle; python $("$PY" -c 'import sys; print(sys.version.split()[0])')"

echo "== overlap (ibub_overlap.py run)"
RUN 2d-unfolding/ibub/ibub_overlap.py run "$N" --clone "$D"; orc=$?
[ "$orc" -eq 0 ] || { echo "STOP: overlap rc $orc"; finish 9; }

echo "== preflight (ibub_unit.py preflight)"
RUN 2d-unfolding/ibub/ibub_unit.py preflight > "$N/logs/preflight.json"; prc=$?
cat "$N/logs/preflight.json"
[ "$prc" -eq 0 ] || { echo "STOP: preflight rc $prc"; finish 9; }

echo "== staging (ibub_unit.py stage)"; date -u +%FT%TZ
RUN 2d-unfolding/ibub/ibub_unit.py stage > "$N/logs/stage.json"; src_=$?
cat "$N/logs/stage.json"; date -u +%FT%TZ
[ "$src_" -eq 0 ] || { echo "STOP: staging rc $src_"; finish 9; }

echo "== the fence again, just before the submission"
fence_sacct || { echo "STOP: fence (before sbatch)"; finish 9; }
echo "== sbatch"
# the job's stdout and stderr go to a fresh private directory, made here just before the submission (it cannot exist:
# $N is this connect's own), so nothing can be planted where Slurm will open the files. Both are pinned, so an
# inherited SBATCH_OUTPUT or SBATCH_ERROR cannot send either elsewhere
mkdir -m 700 "$N/slurm" || { echo "STOP: mkdir $N/slurm"; finish 5; }
jid=$(sbatch --parsable --job-name="$JOBNAME" --time="$LIMIT" --output="$N/slurm/%x-%j.out" \
  --error="$N/slurm/%x-%j.err" \
  "$D/2d-unfolding/ibub/jobs/ibub_job.sbatch" "$D" "$N" "$M" 2> "$N/logs/sbatch.err"); brc=$?
cat "$N/logs/sbatch.err"
[ "$brc" -eq 0 ] && [[ "$jid" =~ ^[0-9]+$ ]] || { echo "STOP: sbatch rc $brc, id '$jid'"; finish 5; }
echo "$jid" > "$N/logs/job.id"; echo "submitted $jid $(date -u +%FT%TZ)"
listed=0
for i in $(seq 1 20); do
  row=$(sacct -X -n -P -j "$jid" -o JobID,JobName,State 2>&1) && [ -n "$row" ] && { listed=1; break; }
  sleep 15
done
echo "sacct: ${row:-<none>}"
[ "$listed" -eq 1 ] || { echo "STOP: sacct did not list $jid within 5 minutes (the job may exist: do not resubmit)"; finish 5; }
# the connect's own record; the batch writes scontrol-batch-<id>.txt, so neither can refuse or overwrite the other
SREC="$N/logs/scontrol-connect-$jid.txt"
[ ! -e "$SREC" ] && [ ! -L "$SREC" ] || { echo "STOP: $SREC exists or is a symlink"; finish 5; }
info=$(scontrol show job "$jid" 2>&1); ( set -o noclobber; printf '%s\n' "$info" > "$SREC" ) \
  || { echo "STOP: writing $SREC"; finish 5; }
# scontrol ends its first line with JobName=..., so each key is matched up to a space or the end of the line
grep -Eq "JobName=$JOBNAME( |\$)" <<<"$info" && grep -Eq "QOS=regular( |\$)" <<<"$info" \
  && grep -Eq "TimeLimit=$LIMIT( |\$)" <<<"$info" \
  || { echo "STOP: scontrol does not show $JOBNAME / regular / $LIMIT for $jid"; finish 5; }
echo "scontrol: name, QOS and limit as declared"
gs=$(git -C "$D" status --porcelain --ignored) || { echo "STOP: git status failed (after)"; finish 9; }
echo "porcelain --ignored after: '${gs}'"
[ -z "$gs" ] || { echo "STOP: the deploy changed (no exception: the job requires it clean)"; finish 9; }
finish 0
