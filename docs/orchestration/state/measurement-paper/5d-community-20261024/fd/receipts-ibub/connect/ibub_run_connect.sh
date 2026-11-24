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
M=d12c4f2a38a53001eb92bbefc8b2dc6001f034dc
N=/pscratch/sd/j/josephrb/ibub-20261124
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
IyEvYmluL2Jhc2gKIyBjb3YyZF9mZW5jZS5zaCByZXYgMyAoMjAyNi0xMS0yMyk6IHRoZSBDT1Yy
RCBmZW5jZSwgcnVuIG9uIGEgUGVybG11dHRlciBsb2dpbiBub2RlIGJlZm9yZSBhbm90aGVyIGxh
bmUncyBjb25uZWN0LgojIFJlYWRzIHNhY2N0IG9ubHkgKG5vIHNxdWV1ZTogc3RhbmRpbmcgcnVs
ZSkuIFJlcGxhY2VzIHJldiAyIChzaGEyNTYgM2ZiYzljYmQuLi4pLCB3aG9zZSA2MC1kYXkgLVMg
UGVybG11dHRlciByZWZ1c2VkCiMgKCJUb28gd2lkZSBvZiBhIGRhdGUgcmFuZ2UgaW4gcXVlcnki
LCBsb2dpbjM4IDIwMjYtMTEtMjMpLCBhbmQgcmV2IDEgKDE2YTJhNWNkLi4uKSwgd2hpY2ggY2Fs
bGVkIHNxdWV1ZS4KIyBDTEVBUiAoZXhpdCAwKSBvbmx5IGlmIHNhY2N0IGV4aXRzIDAsIGV2ZXJ5
IGxpbmUgaXQgd3JpdGVzIChzdGRvdXQgYW5kIHN0ZGVyciB0b2dldGhlcikgaXMgYSB3ZWxsLWZv
cm1lZAojIEpvYklEfEpvYk5hbWV8U3RhdGUgcm93IHdpdGggYSBudW1lcmljIEpvYklELCBhbmQg
ZXZlcnkgcm93IG5hbWVkIGNvdjJkKiBvciB0MmEqIChvdXJzLCBsYXN0IDE0IGRheXMpIGlzIGlu
IGEKIyB0ZXJtaW5hbCBzdGF0ZS4gQW55dGhpbmcgZWxzZSBpcyBleGl0IDM6IGFuIHVuZW5kZWQg
b3IgdW5jbGFzc2lmaWFibGUgbWF0Y2hpbmcgcm93LCBhIG1hbGZvcm1lZCBvciBzdHJheSBsaW5l
CiMgKHNvIGFuIGVycm9yIHNhY2N0IHByaW50cyBvbiBzdGRlcnIgd2hpbGUgZXhpdGluZyAwIHJl
ZnVzZXMpLCBzYWNjdCBmYWlsaW5nLCBvciB0aGUgc3RhcnQgdGltZSBmYWlsaW5nLgojIEtub3du
IGdhcCwgc2FjY3Qtb25seSBieSBydWxlOiBzYWNjdCdzIGRlZmF1bHQgbGlzdGluZyBvbWl0cyBh
IHBlbmRpbmcgam9iIHdpdGggbm8gRWxpZ2libGVUaW1lIChzYmF0Y2ggLS1ob2xkLAojIHNjb250
cm9sIGhvbGQsIGFycmF5IHRhc2tzIGhlbGQgYnkgYSAlbGltaXQpIGFuZCBjYW4gbGFnIHNsdXJt
ZGJkIGJyaWVmbHkuCiMgQSBjb25uZWN0IHRoYXQgcmVsaWVzIG9uIHRoaXMgZmVuY2UgYWxzbyB0
YWtlcyBhIGZyZXNoIGFjayBmcm9tIHRoZSBjb3YyZCBzZXNzaW9uLCB3aGljaCBjb3ZlcnMgdGhh
dCBnYXAuCiMgU3RhdGUgaXMgY2xhc3NpZmllZCBoZXJlIGFnYWluc3QgYSBjbG9zZWQgdGVybWlu
YWwgc2V0IChmaXJzdCB3b3JkIG9mIFN0YXRlLCBzbyAiQ0FOQ0VMTEVEIGJ5IE4iIGNvdW50cyk7
CiMgYW55IG90aGVyIHN0YXRlLCBpbmNsdWRpbmcgb25lcyB0aGlzIGZpbGUgZG9lcyBub3QgbmFt
ZSwgcmVmdXNlcy4gc2FjY3QgLXMgaXMgbm90IHVzZWQgKFBlcmxtdXR0ZXIgcmVqZWN0cyBDRiku
CiMgV3JpdGVzIG5vdGhpbmcuIE1heSBiZSBsYXVuY2hlZCBmcm9tIGEgL2Rldi9zaG0gY29weSBv
ZiBpdHNlbGYgd2hvc2UgcGF0aCBpcyAkMS4gQXQgZXhpdCBpdCBkZWxldGVzICQxIG9ubHkgaWYg
JDEKIyBpcyB1bmRlciAvZGV2L3NobS8sIGhhcyBubyAuLiBjb21wb25lbnQsIGFuZCBpcyB0aGUg
cnVubmluZyBzY3JpcHQgaXRzZWxmIChbICIkMSIgLWVmICIkMCIgXSk7IGFueSBvdGhlciAkMSBp
cwojIGtlcHQgYW5kIG5hbWVkLiAoV2l0aG91dCB0aGUgLi4gcnVsZSwgL2Rldi9zaG0vLi4vPHJl
cG8+L2NvdjJkX2ZlbmNlLnNoIHJ1biBmcm9tIHRoZSByZXBvIHdvdWxkIGRlbGV0ZSB0aGUgcmVw
byBmaWxlLikKU0VMRj0kMQpmaW4oKSB7CiAgaWYgWyAtbiAiJFNFTEYiIF07IHRoZW4KICAgIGNh
c2UgJFNFTEYgaW4KICAgICAgKi8uLi8qfCovLi4pIGVjaG8gInNlbGYtY29weSBub3QgcmVtb3Zl
ZDogJFNFTEYiIDs7CiAgICAgIC9kZXYvc2htLyopIGlmIFsgIiRTRUxGIiAtZWYgIiQwIiBdOyB0
aGVuIHJtIC1mIC0tICIkU0VMRiI7IGVsc2UgZWNobyAic2VsZi1jb3B5IG5vdCByZW1vdmVkOiAk
U0VMRiI7IGZpIDs7CiAgICAgICopIGVjaG8gInNlbGYtY29weSBub3QgcmVtb3ZlZDogJFNFTEYi
IDs7CiAgICBlc2FjCiAgZmkKICBleGl0ICIkMSIKfQplY2hvICJmZW5jZSBob3N0PSQoaG9zdG5h
bWUpIHV0Yz0kKGRhdGUgLXUgKyVGVCVUWikiCiMgc2FjY3QgcmVhZHMgLVMgaW4gdGhlIGNsdXN0
ZXIncyBsb2NhbCB0aW1lLiAxNCBkYXlzIGNvdmVycyB0aGUgNDggaCBNYXhXYWxsIHdpdGggbWFy
Z2luIGFuZCBpcyBhIHJhbmdlIFBlcmxtdXR0ZXIncwojIHNhY2N0IGFjY2VwdHMgKHJldiAxIGFu
ZCB0aGUgVDMgYW5kIGZsdXgyIGZlbmNlcyB1c2VkIGl0KTsgNjAgZGF5cyB3YXMgcmVmdXNlZC4K
c3RhcnQ9JChkYXRlIC1kICcxNCBkYXlzIGFnbycgKyVGVCVUKSB8fCB7IGVjaG8gIkZFTkNFIFJF
RlVTRUQ6IHN0YXJ0IHRpbWUgZmFpbGVkIjsgZmluIDM7IH0KW1sgJHN0YXJ0ID1+IF5bMC05XXs0
fS1bMC05XXsyfS1bMC05XXsyfVRbMC05XXsyfTpbMC05XXsyfTpbMC05XXsyfSQgXV0gfHwgeyBl
Y2hvICJGRU5DRSBSRUZVU0VEOiBzdGFydCB0aW1lIG1hbGZvcm1lZDogJyRzdGFydCciOyBmaW4g
MzsgfQp1c2VyPSQoaWQgLXVuKSB8fCB7IGVjaG8gIkZFTkNFIFJFRlVTRUQ6IGlkIC11biBmYWls
ZWQiOyBmaW4gMzsgfQpbIC1uICIkdXNlciIgXSB8fCB7IGVjaG8gIkZFTkNFIFJFRlVTRUQ6IGVt
cHR5IHVzZXIiOyBmaW4gMzsgfQplY2hvICJzYWNjdCAtWCAtbiAtUCAtdSAkdXNlciAtUyAkc3Rh
cnQgLUUgbm93IC1vIEpvYklELEpvYk5hbWUsU3RhdGUgMj4mMSIKcz0kKHNhY2N0IC1YIC1uIC1Q
IC11ICIkdXNlciIgLVMgIiRzdGFydCIgLUUgbm93IC1vIEpvYklELEpvYk5hbWUsU3RhdGUgMj4m
MSkgfHwgeyBlY2hvICJGRU5DRSBSRUZVU0VEOiBzYWNjdCBmYWlsZWQiOyBwcmludGYgJyVzXG4n
ICIkcyIgfCBzZWQgJ3MvXi9zYWNjdDogLyc7IGZpbiAzOyB9CnY9JChwcmludGYgJyVzXG4nICIk
cyIgfCBhd2sgLUYnfCcgJwogIEJFR0lOIHsgc3BsaXQoIkJPT1RfRkFJTCBDQU5DRUxMRUQgQ09N
UExFVEVEIERFQURMSU5FIEZBSUxFRCBOT0RFX0ZBSUwgT1VUX09GX01FTU9SWSBQUkVFTVBURUQg
VElNRU9VVCIsIHQsICIgIikKICAgICAgICAgIGZvciAoaSBpbiB0KSB0ZXJtW3RbaV1dID0gMSB9
CiAgL14kLyB7IG5leHQgfQogIE5GICE9IDMgfHwgJDEgIX4gL15bMC05XSsoW18rXS4qKT8kLyB7
IHByaW50ICJtYWxmb3JtZWQ6ICIgJDA7IGJhZCA9IDE7IG5leHQgfQogICQyIH4gL14oY292MmR8
dDJhKS8geyBuKys7IHNwbGl0KCQzLCB3LCAiICIpOyBpZiAoISh3WzFdIGluIHRlcm0pKSB7IHBy
aW50ICJ1bmVuZGVkOiAiICQwOyBiYWQgPSAxIH0gfQogIEVORCB7IHByaW50ICJtYXRjaGluZyBy
b3dzOiAiIG4gKyAwOyBleGl0IGJhZCB9JykKcmM9JD8KcHJpbnRmICclc1xuJyAiJHYiIHwgc2Vk
ICdzL14vc2FjY3QgLycKWyAiJHJjIiAtZXEgMCBdIHx8IHsgZWNobyAiRkVOQ0UgUkVGVVNFRDog
YW4gdW5lbmRlZCwgdW5jbGFzc2lmaWFibGUgb3IgbWFsZm9ybWVkIHNhY2N0IHJvdyI7IGZpbiAz
OyB9CmVjaG8gIkZFTkNFIENMRUFSIgpmaW4gMAo=
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
e8e5969f978107e45991164a16c84f1794694dee752cbf189eab00e3ddd54633  ibub_unit.py
1cc64564448277831dc4ac5fc888b4a3dd15a2c56badfab6325f83d962bcfed7  ibub_readout.py
62591f998f6d3c907bcec460c9399a419755d8f041b40652f37066074b3ab85b  ibub_lanes.py
507767798ed13edd7c896b0955fcf4090e5dfc0307e0067d9684df2d30c78928  ibub_overlap.py
bf0838c67ac5c3c0ce375ca7083623d3b44c8007d7de06d30e59ac9f7a02143b  config.json
ab0d7387e7b63605f5091342eea2b1a976b39dda7263b31099309e85c6195518  jobs/ibub_job.sbatch
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
grep -Eq "JobName=$JOBNAME( |\$)" <<<"$info" && grep -Eq "TimeLimit=$LIMIT( |\$)" <<<"$info" \
  || { echo "STOP: scontrol does not show $JOBNAME / $LIMIT for $jid"; finish 5; }
# Perlmutter records --qos=regular as QOS=regular_1 (receipts-cov2d/a2/bulk/complete/connect-complete-1.log.txt:78); the accepted set is exactly these two
qos=$(tr ' ' '\n' <<<"$info" | sed -n 's/^QOS=//p' | head -1)
case "$qos" in regular|regular_1) ;; *) echo "STOP: scontrol shows QOS '$qos' for $jid, not one of {regular, regular_1}"; finish 5;; esac
echo "scontrol: name, QOS ($qos) and limit as declared"
gs=$(git -C "$D" status --porcelain --ignored) || { echo "STOP: git status failed (after)"; finish 9; }
echo "porcelain --ignored after: '${gs}'"
[ -z "$gs" ] || { echo "STOP: the deploy changed (no exception: the job requires it clean)"; finish 9; }
finish 0
