#!/bin/bash
# The q0 study's extract connect (PLAN.md section 2; the director's approval of 2026-11-24). On a Perlmutter login node,
# from a /dev/shm copy of itself whose path is $1; it deletes that copy at exit. 0 node-h: no Slurm job. Derived from
# MSR connect B (msr_build_connect.sh 2a5c1c92), with the same fences (cov2d's rev 3 7e81a721, embedded and sha-checked,
# then a sacct fence on the named prefixes) and records-on-every-stop. q0_extract.py is embedded (base64) and run only
# if its sha256 is the pinned one, so no clone is made. Job states come from sacct only.
#   usage: q0_connect.sh <self> <window_end_epoch> <fence prefixes, comma-separated>
# In order, each failure a final stop: the window; the fences; $OUT (fresh) absent; the extractor at its sha256; the
# extract (q0_extract.py: the omnifile's sha256 read O_NOATIME, the branches, the passing count, its atime, the recovery
# control; reads mc_signal_reco only); the records (sha256 of every file under logs/ and extract/, then one tar).
# Writes only $OUT and /dev/shm/q0study-connect. Nothing to CFS. No set -u. Any stop is final.
SELF=$1; WEND=$2; FENCE=$3
set -o pipefail
TAG=q0
OUT=/pscratch/sd/j/josephrb/q0study-20261124
SHM=/dev/shm/q0study-connect
PY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
OMNI=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_MEFHC.root
FENCE_SHA=7e81a721476da987a0e1262ab2054132bd8440cd49b0dc7a5c4f01d50a310738
XSHA=@@XSHA@@
bail() { echo "BAIL $*"; rm -rf -- "$SHM"; rm -f -- "$SELF"; exit 9; }   # a precondition failed: nothing in $OUT
[[ "$WEND" =~ ^[0-9]{10}$ ]] || bail "window end '$WEND'"
now=$(date +%s); [ "$now" -le "$WEND" ] || bail "the window ended (now $now > $WEND)"
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || bail "fence '$FENCE'"
[ ! -e "$OUT" ] || bail "$OUT exists"
[ ! -e "$SHM" ] || bail "$SHM exists"
[ -x "$PY" ] || bail "no $PY"
[ -f "$OMNI" ] || bail "no $OMNI"

# ---- cov2d's fence, rev 3, exactly (embedded, sha-checked), then the sacct fence for the named prefixes
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
  bad=$(printf '%s\n' "$rows" | awk -F'|' -v pre="$FENCE" '
    BEGIN { n = split(pre, P, ",") }
    NF >= 3 {
      st = $3; sub(/ by [0-9]+$/, "", st)
      term = (st ~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)$/)
      if (term) next
      for (i = 1; i <= n; i++) if (P[i] != "" && index($2, P[i]) == 1) { print; break }
    }') || { echo "fence awk failed"; return 2; }
  [ -z "$bad" ] || { echo "fenced jobs not terminal: $bad"; return 1; }
  return 0
}
fo=$(fence_sacct 2>&1) || bail "fence (sacct) not clear: $fo"

# ---- the extractor, decoded and checked before $OUT exists
base64 -d > "$SHM/q0_extract.py" <<'B64' || bail "extractor decode"
@@X_B64@@
B64
[ "$(sha256sum "$SHM/q0_extract.py" | cut -d' ' -f1)" = "$XSHA" ] || bail "q0_extract.py is not the pinned one"

mkdir -m 700 "$OUT" "$OUT/logs" "$OUT/extract" || bail "mkdir $OUT"
LOG=$OUT/logs/connect-$TAG.log
exec > "$LOG" 2>&1
RECORDED=0
finish() {
  local rc=$1
  if [ "$RECORDED" -eq 0 ]; then RECORDED=1; records || { [ "$rc" -eq 0 ] && rc=4; }; fi
  echo "q0 $TAG rc=$rc"; date -u +%FT%TZ; echo "$rc" > "$OUT/logs/connect-$TAG.done"; rm -rf -- "$SHM"; rm -f -- "$SELF"; exit "$rc"
}
records() {
  echo "== records"; date -u +%FT%TZ
  ( cd "$OUT" && find logs extract -type f ! -name "connect-$TAG.log" -print0 | sort -z | xargs -0 -r sha256sum ) \
    > "$OUT/RECORDS.SHA256SUMS" || { echo "records: the sums failed"; return 1; }
  [ -s "$OUT/RECORDS.SHA256SUMS" ] || { echo "records: no files"; return 1; }
  cat "$OUT/RECORDS.SHA256SUMS"
  tar -C "$OUT" -cf "$OUT/fetch-$TAG.tar" --exclude="logs/connect-$TAG.log" logs extract RECORDS.SHA256SUMS \
    || { echo "records: tar failed"; return 1; }
  echo "fetch-$TAG.tar sha256 $(sha256sum "$OUT/fetch-$TAG.tar" | cut -d' ' -f1) bytes $(stat -c %s "$OUT/fetch-$TAG.tar")"
}
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ; echo "window_end_epoch $WEND (now $now); fence prefixes $FENCE"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/q0_${TAG}.sh"
cp "$SHM/q0_extract.py" "$OUT/logs/q0_extract.py"
echo "== cov2d fence rev 3 ($FENCE_SHA)"; printf '%s\n' "$fence_out"
echo "== fence (sacct)"; fence_sacct || { echo "STOP: fence"; finish 9; }; echo "fence clear"
echo "== extractor sha256 $XSHA (checked)"

export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONHASHSEED=0
echo "threads 2; nice 19; ionice idle; python $("$PY" -c 'import sys; print(sys.version.split()[0])')"
echo "== extract (mc_signal_reco only; O_NOATIME)"
( cd "$SHM" && nice -n 19 ionice -c3 env -u PYTHONPATH /usr/bin/time -v "$PY" -I -B "$SHM/q0_extract.py" --omni "$OMNI" \
    --out "$OUT/extract" > "$OUT/logs/extract.out" 2> "$OUT/logs/extract.err" ); c=$?
cat "$OUT/logs/extract.out"
grep -E 'STOP|REFUSED|Maximum resident|Elapsed' "$OUT/logs/extract.err"
[ "$c" -eq 0 ] || { echo "STOP: extract rc $c"; finish 5; }
[ -f "$OUT/extract/q0_extract.npz" ] && [ -f "$OUT/extract/q0_extract.json" ] || { echo "STOP: the extract wrote no product"; finish 5; }
finish 0
