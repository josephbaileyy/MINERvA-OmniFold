#!/bin/bash
# (b) part 1 (and part 3's tables): the one read connect (B-SEL-DECLARATION.md §1). On a Perlmutter login node, from a
# /dev/shm copy of itself whose path is $1; it deletes that copy at exit. No Slurm job.
#   usage: bsel_read.sh <self> <window_end_epoch> <fence prefixes, comma-separated>
# In order, each failure a final stop before any copy:
#   the window; the fence by sacct (no job of this user whose name starts with a fenced prefix is non-terminal);
#   $OUT absent; every source present (a purged source STOPs here: the HPSS fallback is a separate amendment).
# Then, per source: stat; one read through dd iflag=noatime into sha256sum, which must equal its pin; one copy through
# dd iflag=noatime into $OUT/fetch-bsel/, whose sha256 must equal the pin; stat again, which must be unmoved (size,
# mtime, atime, inode). Then RECORDS.SHA256SUMS (strict line count) and one tar, whose sha256 this log prints.
# Writes only $OUT and the launcher's /dev/shm copy. Nothing to CFS. No set -u. Any stop is final.
SELF=$1; WEND=$2; FENCE=$3
set -o pipefail
OUT=/pscratch/sd/j/josephrb/bsel-20261124
FR=$OUT/fetch-bsel
SOURCES='7384c6518aa0f59bd4964170fcc9b652f1c31958f422f1e1b597cd3e59219ad9 /pscratch/sd/j/josephrb/fd-f0b-20261026/fd_f0b_experiments.npz
997c7dae34ef9703291baece51eed05f3dd7d38a043630cac9667efaad2775bc /pscratch/sd/j/josephrb/fd-f1-20261027/grade/fd_f1_experiments.npz
198205b6466a4b7ab65555c15c3248b379830a4d6a376b1599fe51923aeb4c94 /pscratch/sd/j/josephrb/fd-f1-20261027/f1c/closure/f1_closure_genie_v3_g18.npz
532a6ac014274e54f2c1fa82b46a3411ff0a62c803e108cf85fa6bcfe070e208 /pscratch/sd/j/josephrb/fd-f1-20261027/f1c/closure/f1_closure_genie_v3_ar23.npz
eb3e218866dd36e093c85e85a791f8dd8de1491f4ad0694924644b01c8e55f08 /pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-5D-PV_e_closure_tune_v1.npz
fff9030e7fd63c538b27c58f2a35417b5d28c3d2f6de2880219b181812215182 /pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-5D-PV_e_closure_nuwro.npz'
NSRC=6
bail() { echo "BAIL $*"; rm -f -- "$SELF"; exit 9; }
[[ "$WEND" =~ ^[0-9]{10}$ ]] || bail "window end '$WEND'"
now=$(date +%s); [ "$now" -le "$WEND" ] || bail "the window ended (now $now > $WEND)"
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || bail "fence '$FENCE'"
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
    }')
  [ -z "$bad" ] || { echo "fenced jobs not terminal: $bad"; return 1; }
  return 0
}
fence_sacct > /dev/null 2>&1 || bail "fence (sacct) not clear"
[ ! -e "$OUT" ] || bail "$OUT exists"
n=0; while read -r pin src; do
  [ -n "$src" ] || continue
  [ -f "$src" ] || bail "source missing (purged?): $src"
  n=$((n + 1))
done <<< "$SOURCES"
[ "$n" -eq "$NSRC" ] || bail "the source list holds $n entries, not $NSRC"
mkdir -p "$OUT/logs" "$FR" || bail "mkdir"
LOG=$OUT/logs/connect-bsel.log
exec > "$LOG" 2>&1
finish() { echo "bsel read rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-bsel.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ; echo "window_end_epoch $WEND (now $now); fence prefixes $FENCE"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/bsel_read.sh"
echo "== fence (sacct)"; fence_sacct || { echo "STOP: fence"; finish 9; }; echo "fence clear"
echo "== sources"
printf 'pin\tsha256_ok\tcopy_ok\tstat_unmoved\tsize\tatime_before_s\tatime_after_s\tsrc\n'
fail=0; nf=0
while read -r pin src; do
  [ -n "$src" ] || continue
  st() { stat -c '%s %Y %X %i %.9X' "$src"; }
  before=$(st) || { echo "STOP: stat $src"; finish 4; }
  got=$(dd if="$src" iflag=noatime bs=16M status=none | sha256sum | cut -d' ' -f1) || { echo "STOP: read $src"; finish 4; }
  dst="$FR/$(basename "$src")"
  [ ! -e "$dst" ] || { echo "STOP: two sources share the name $(basename "$src")"; finish 4; }
  dd if="$src" of="$dst" iflag=noatime bs=16M status=none || { echo "STOP: copy $src"; finish 4; }
  cp_sha=$(sha256sum "$dst" | cut -d' ' -f1) || { echo "STOP: hash $dst"; finish 4; }
  after=$(st) || { echo "STOP: stat $src"; finish 4; }
  okr=false; okc=false; oks=false
  [ "$got" = "$pin" ] && okr=true
  [ "$cp_sha" = "$pin" ] && okc=true
  [ "$before" = "$after" ] && oks=true
  set -- $before; sz=$1; ab=$5; set -- $after; aa=$5
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "${pin:0:16}" "$okr" "$okc" "$oks" "$sz" "$ab" "$aa" "$src"
  { $okr && $okc && $oks; } || fail=1
  echo "$cp_sha  $(basename "$src")" >> "$FR/RECORDS.SHA256SUMS" || fail=1
  nf=$((nf + 1))
done <<< "$SOURCES"
[ "$fail" -eq 0 ] && [ "$nf" -eq "$NSRC" ] || { echo "STOP: a source failed its pin, its copy, or moved ($nf of $NSRC)"; finish 4; }
nl=$(grep -c '' "$FR/RECORDS.SHA256SUMS"); ng=$(grep -cE '^[0-9a-f]{64}  [^[:space:]/]+$' "$FR/RECORDS.SHA256SUMS")
[ "$nl" -eq "$NSRC" ] && [ "$ng" -eq "$NSRC" ] || { echo "STOP: RECORDS.SHA256SUMS holds $nl lines ($ng well-formed)"; finish 4; }
( cd "$FR" && sha256sum --strict --quiet -c RECORDS.SHA256SUMS ) || { echo "STOP: a copy does not match its sum"; finish 4; }
tar -C "$OUT" -cf "$FR.tar" "fetch-bsel" || { echo "STOP: tar"; finish 4; }
echo "fetch-bsel.tar sha256 $(sha256sum "$FR.tar" | cut -d' ' -f1) bytes $(stat -c %s "$FR.tar")"
finish 0
