#!/bin/bash
# IBUB connect O, the readout (IBUB-DECLARATION.md sections 4-6 and 8; the director's rulings of 2026-11-24 on item 4
# and --records). On a Perlmutter login node, from a /dev/shm copy of itself whose path is $1; it deletes that copy at
# exit. It follows connect R (the same fences and records) and COV2D's readout connects (the MAT environment, the
# private place, the copy-out).
#   usage: ibub_readout_connect.sh <self> <window_end_epoch>
#
# In order, each failure a final stop:
#  1. the window; cov2d's fence rev 3 (embedded, sha-checked); this lane's sacct fence (no job named ibub_, ibuchi_,
#     cov2d, t2a, rpd or msr unended). The fence's rpd covers RPD-RECO's P0 root and any other rpd_ step;
#  2. the job: exactly one sacct row for $JOB, named ibub_run, in a terminal State (COMPLETED, FAILED, TIMEOUT,
#     CANCELLED, OUT_OF_MEMORY, NODE_FAIL; classified here, no -s filter). Anything else is a STOP before anything
#     of the job's is fetched or read;
#  3. the root, config.json's readout.write_root, must not exist; it is made with mode 700; $N/readout must not exist;
#  4. the fetch: the job's records, read from $N by dd iflag=noatime into $R/records, with RECORDS.SHA256SUMS
#     (the readout verifies it again and requires the records it needs);
#  5. a fresh clone at M (clean, the ibub files at their sha256) inside the root; RPD-RECO P0's committed records are
#     in it (the readout's serialization after P0); the overlap check (ibub_overlap.py readout) reads CLEAR;
#  6. the MAT environment (the shared checkout's setup_salloc_env.sh, as COV2D's readouts) and a MAT preflight on one
#     real MnvH1D;
#  7. ibub_readout.py for G18 and then AR23, with --job, --job-m and --records; each tune's rc and verdict line;
#  8. the copy-out to $N/readout/<T>/, checked by sha256, then the records tar; the root is removed last.
# Writes only the root (/dev/shm/ibub-connect), $N/readout, $N/fetch-readout(.tar) and $N/logs/connect-readout.*.
# Nothing goes to CFS. Job states come from sacct only, and squeue is never run. No set -u. Any stop is final.
SELF=$1; WEND=$2
set -o pipefail
TAG=readout
M=94d81351c86de8efa6435e1358e4f0fa2ce7c971
JOB=61924744
JOB_M=d12c4f2a38a53001eb92bbefc8b2dc6001f034dc
N=/pscratch/sd/j/josephrb/ibub-20261124
R=/dev/shm/ibub-connect
D=$R/deploy
FR=$N/fetch-$TAG
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
PY=$HOME/.conda/envs/root_6_28/bin/python3
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
P0=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/p0-20261123
FENCE_SHA=7e81a721476da987a0e1262ab2054132bd8440cd49b0dc7a5c4f01d50a310738
PREFIXES=ibub_,ibuchi_,cov2d,t2a,rpd,msr
bail() { echo "BAIL $*"; rm -f -- "$SELF"; exit 9; }   # a precondition failed: nothing written
[[ "$WEND" =~ ^[0-9]{10}$ ]] || bail "window end '$WEND'"
now=$(date +%s); [ "$now" -le "$WEND" ] || bail "the window ended (now $now > $WEND)"
[[ "$JOB" =~ ^[0-9]+$ ]] && [[ "$JOB_M" =~ ^[0-9a-f]{40}$ ]] && [[ "$M" =~ ^[0-9a-f]{40}$ ]] || bail "JOB, JOB_M or M"
[ -d "$N" ] && [ ! -L "$N" ] && [ -d "$N/units" ] && [ -d "$N/logs" ] || bail "$N is not the job's namespace"
[ ! -e "$R" ] && [ ! -L "$R" ] || bail "$R exists"
[ ! -e "$N/readout" ] && [ ! -e "$FR" ] && [ ! -e "$N/logs/connect-$TAG.log" ] || bail "a readout already ran in $N"
[ -x "$PY" ] && [ -x "$PY310" ] || bail "no $PY or $PY310"

# ---- cov2d's fence, rev 3, exactly (embedded, sha-checked), then this lane's sacct fence for every prefix
mkdir -m 700 "$R" || bail "mkdir $R"
[ "$(realpath "$R")" = "$R" ] || { rm -rf -- "$R"; bail "$R is not its own real path"; }
base64 -d > "$R/cov2d_fence.sh" <<'B64' || { rm -rf -- "$R"; bail "fence decode"; }
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
[ "$(sha256sum "$R/cov2d_fence.sh" | cut -d' ' -f1)" = "$FENCE_SHA" ] || { rm -rf -- "$R"; bail "cov2d_fence.sh is not rev 3"; }
fence_out=$(bash "$R/cov2d_fence.sh" 2>&1); frc=$?
[ "$frc" -eq 0 ] || { printf '%s\n' "$fence_out"; rm -rf -- "$R"; bail "cov2d fence rev 3 not clear (rc $frc)"; }
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
fo=$(fence_sacct 2>&1) || { rm -rf -- "$R"; bail "fence (sacct) not clear: $fo"; }

# ---- the job: terminal in sacct, or nothing of it is read (the director's ruling: a missing row is never finished)
mkdir -m 700 "$R/records" || { rm -rf -- "$R"; bail "mkdir $R/records"; }
sacct -j "$JOB" -X -P -o JobID,JobName,State,ExitCode > "$R/records/sacct-$JOB.txt" 2>&1 \
  || { cat "$R/records/sacct-$JOB.txt"; rm -rf -- "$R"; bail "sacct -j $JOB failed"; }
row=$(awk -F'|' -v j="$JOB" '$1 == j' "$R/records/sacct-$JOB.txt")
[ "$(printf '%s\n' "$row" | grep -c .)" -eq 1 ] || { rm -rf -- "$R"; bail "STOP: sacct has no single row for $JOB: '$row'"; }
state=$(printf '%s\n' "$row" | cut -d'|' -f3 | awk '{print $1}')
[ "$(printf '%s\n' "$row" | cut -d'|' -f2)" = ibub_run ] || { rm -rf -- "$R"; bail "STOP: $JOB is not ibub_run: '$row'"; }
case "$state" in COMPLETED|FAILED|TIMEOUT|CANCELLED|OUT_OF_MEMORY|NODE_FAIL) ;;
  *) rm -rf -- "$R"; bail "STOP: job $JOB is '$state', not terminal: nothing is read";; esac

# from here every stop writes the records first
exec > "$N/logs/connect-$TAG.log" 2>&1 || { rm -rf -- "$R"; bail "the log"; }
RECORDED=0
finish() {
  local rc=$1
  if [ "$RECORDED" -eq 0 ]; then RECORDED=1; records || { [ "$rc" -eq 0 ] && rc=4; }; fi
  rm -rf -- "$R"; echo "root $R removed rc=$? left=$([ -e "$R" ] && echo yes || echo no)"
  echo "ibub $TAG rc=$rc"; date -u +%FT%TZ; ( set -o noclobber; echo "$rc" > "$N/logs/connect-$TAG.done" )
  rm -f -- "$SELF"; exit "$rc"
}
records() {   # the fetch, the readout's outputs and logs, copied into $FR with sums, then tarred
  echo "== records"; date -u +%FT%TZ
  mkdir "$FR" || { echo "records: mkdir $FR failed"; return 1; }
  local rel fail=0 nf=0
  local dirs="" x                # only the places that exist: a stop before a tune ran leaves no out-<T>
  for x in records out-G18 out-AR23 logs; do [ -d "$R/$x" ] && dirs="$dirs $x"; done
  [ -n "$dirs" ] || { echo "records: nothing to copy"; return 1; }
  ( cd "$R" && find $dirs -type f ! -name '*.sh' -print0 | sort -z ) > "$FR.list" \
    || { echo "records: the list failed (find)"; return 1; }
  while IFS= read -r -d '' rel; do
    mkdir -p "$FR/$(dirname "$rel")" && cp -p -- "$R/$rel" "$FR/$rel" || { echo "copy failed: $rel"; fail=1; continue; }
    cmp -s "$R/$rel" "$FR/$rel" || { echo "copy differs: $rel"; fail=1; }
    echo "$(sha256sum "$FR/$rel" | cut -d' ' -f1)  $rel" >> "$FR.sums"; nf=$((nf + 1))
  done < "$FR.list"
  [ "$fail" -eq 0 ] && [ "$nf" -gt 0 ] || { echo "records: a copy failed or differs, or none ($nf)"; return 1; }
  rm -f -- "$FR.list"; mv "$FR.sums" "$FR/RECORDS.SHA256SUMS" || return 1
  echo "records copied: $nf files, $(du -sb "$FR" | cut -f1) bytes"
  tar -C "$N" -cf "$FR.tar" "fetch-$TAG" || { echo "records: tar failed"; return 1; }
  echo "fetch-$TAG.tar sha256 $(sha256sum "$FR.tar" | cut -d' ' -f1) bytes $(stat -c %s "$FR.tar")"
}
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ; echo "window_end_epoch $WEND (now $now); fence prefixes $PREFIXES"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1); M $M; job $JOB at $JOB_M"
mkdir -m 700 "$R/logs" "$R/tmp" || { echo "STOP: mkdir $R/logs, $R/tmp"; finish 9; }
cp "$SELF" "$R/logs/ibub_${TAG}_connect.sh"
echo "== cov2d fence rev 3 ($FENCE_SHA)"; printf '%s\n' "$fence_out"
echo "== fence (sacct)"; echo "fence clear"
echo "== the job: $row (terminal: $state)"

# ---- the fetch of the job's records (O_NOATIME reads of $N; the readout verifies the sums and needs its list)
echo "== fetch"
for rel in IBUB-DONE units/refcheck.json stage/stage.json "logs/scontrol-batch-$JOB.txt" logs/refcheck.log \
           logs/complete.json "slurm/ibub_run-$JOB.out" "slurm/ibub_run-$JOB.err"; do
  src="$N/$rel"
  if [ ! -e "$src" ]; then echo "fetch: $rel absent"; continue; fi
  [ -f "$src" ] && [ ! -L "$src" ] || { echo "STOP: $src is not a regular file"; finish 9; }
  mkdir -p "$R/records/$(dirname "$rel")" || { echo "STOP: mkdir for $rel"; finish 9; }
  dd if="$src" of="$R/records/$rel" iflag=noatime status=none || { echo "STOP: fetching $rel"; finish 9; }
  a=$(dd if="$src" iflag=noatime status=none | sha256sum | cut -d' ' -f1) || { echo "STOP: re-reading $rel"; finish 9; }
  [ "$a" = "$(sha256sum "$R/records/$rel" | cut -d' ' -f1)" ] || { echo "STOP: $rel changed while fetched"; finish 9; }
  echo "fetch: $rel $a"
done
( cd "$R/records" && find . -type f ! -name RECORDS.SHA256SUMS -printf '%P\n' | sort | while IFS= read -r f; do
    echo "$(sha256sum -- "$f" | cut -d' ' -f1)  $f"; done ) > "$R/records.sums" && mv "$R/records.sums" "$R/records/RECORDS.SHA256SUMS" \
  || { echo "STOP: RECORDS.SHA256SUMS"; finish 9; }
echo "RECORDS.SHA256SUMS: $(grep -c . "$R/records/RECORDS.SHA256SUMS") files"

# ---- the deploy: a fresh clone at M, clean, the ibub files at their sha256, P0's records in it
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$R/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
gs=$(git -C "$D" status --porcelain --ignored) || { echo "STOP: git status failed (before)"; finish 9; }
echo "HEAD $M; porcelain --ignored before: '${gs}'"
[ -z "$gs" ] || { echo "STOP: the deploy is not clean"; finish 9; }
( cd "$D/2d-unfolding/ibub" && sha256sum --strict -c ) <<SUMS || { echo "STOP: the ibub files are not the declared ones"; finish 9; }
e8e5969f978107e45991164a16c84f1794694dee752cbf189eab00e3ddd54633  ibub_unit.py
4d3b5c0205c4d741aa6a0b0787fd21560dfe9c62051f212cac40b3db0cd8b45a  ibub_readout.py
62591f998f6d3c907bcec460c9399a419755d8f041b40652f37066074b3ab85b  ibub_lanes.py
507767798ed13edd7c896b0955fcf4090e5dfc0307e0067d9684df2d30c78928  ibub_overlap.py
bf0838c67ac5c3c0ce375ca7083623d3b44c8007d7de06d30e59ac9f7a02143b  config.json
ab0d7387e7b63605f5091342eea2b1a976b39dda7263b31099309e85c6195518  jobs/ibub_job.sbatch
SUMS
git -C "$D" merge-base --is-ancestor "$JOB_M" HEAD || { echo "STOP: the job's commit $JOB_M is not an ancestor of M"; finish 9; }
[ -n "$(git -C "$D" ls-tree -d HEAD "$P0")" ] || { echo "STOP: RPD-RECO P0's records ($P0) are not in M"; finish 9; }
echo "P0 records in M: $P0"
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
echo "== overlap (ibub_overlap.py readout)"
( cd "$D" && nice -n 19 env -u PYTHONPATH "$PY" -I -B 2d-unfolding/ibub/ibub_overlap.py readout "$N" --clone "$D" ); orc=$?
[ "$orc" -eq 0 ] || { echo "STOP: overlap rc $orc"; finish 9; }

# ---- the MAT environment and its preflight, then the two tunes (as COV2D's readouts: one process per tune)
echo "== MAT"
"$PY310" -B -c "import sys; sys.path.insert(0, '$D/nd-unfolding'); import fd_rpd_inputs as r; r.run_check_mat_setup(None)" \
  || { echo "STOP: the MAT pin check"; finish 7; }
for T in G18 AR23; do
  (
    source "$A/setup_salloc_env.sh" > /dev/null 2>&1 || exit 3
    export TMPDIR=$R/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
    echo "python=$(command -v python) TMPDIR=$TMPDIR"
    python - <<'PYEOF' || exit 5
import hashlib, os, ROOT
src = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_1A.root"
fd = os.open(src, os.O_RDONLY | os.O_NOATIME); data = b""
while True:
  b = os.read(fd, 1 << 24)
  if not b: break
  data += b
os.close(fd)
print("MAT preflight file:", src, "sha256", hashlib.sha256(data).hexdigest())
dst = os.path.join(os.environ["TMPDIR"], "mat_preflight.root"); open(dst, "wb").write(data)
f = ROOT.TFile.Open(dst); h = f.Get("pTmu_reweightedflux_integrated")
print("MAT preflight:", type(h).__name__, h.ClassName(), h.GetNbinsX(), "bins")
assert h.ClassName().startswith("PlotUtils::MnvH1D"), h.ClassName()
os.remove(dst)
PYEOF
    cd "$D/2d-unfolding/ibub" && nice -n 19 taskset -c 8-11 /usr/bin/time -v python -B ibub_readout.py --truth "$T" \
      --units "$N/units" --out "$R/out-$T" --job "$JOB" --job-m "$JOB_M" --records "$R/records"
  ) > "$R/logs/readout-$T.log" 2>&1; trc=$?
  grep -v '^Warning in <TInterpreter::ReadRootmapFile>' "$R/logs/readout-$T.log" | tail -25
  line=$(grep -E "^IBUB-READOUT $T " "$R/logs/readout-$T.log" | tail -1)
  echo "READOUT $T rc=$trc: ${line:-no verdict line}"
  eval "RC_$T=$trc"
done
gs=$(git -C "$D" status --porcelain --ignored) || { echo "STOP: git status failed (after)"; finish 9; }
echo "porcelain --ignored after: '${gs}'"

# ---- the copy-out, then the records; the verdict is each tune's own (main: 0 PASS, 3 another verdict, 4 refused)
echo "== copy-out"
mkdir -m 700 "$N/readout" || { echo "STOP: mkdir $N/readout"; finish 5; }
for T in G18 AR23; do
  [ -d "$R/out-$T" ] || { echo "copy-out: no $R/out-$T"; continue; }
  mkdir "$N/readout/$T" && cp -p -- "$R/out-$T"/* "$N/readout/$T/" || { echo "STOP: the copy-out of $T"; finish 5; }
  ( cd "$R/out-$T" && sha256sum -- * ) > "$R/logs/out-$T.sha256" \
    && ( cd "$N/readout/$T" && sha256sum --strict -c "$R/logs/out-$T.sha256" ) || { echo "STOP: the copy-out of $T differs"; finish 5; }
  echo "copied $T: $(tr '\n' ' ' < "$R/logs/out-$T.sha256")"
done
echo "readout rcs: G18 $RC_G18, AR23 $RC_AR23"
[ -n "$gs" ] && { echo "STOP: the deploy changed"; finish 9; }
case "$RC_G18$RC_AR23" in 00) finish 0 ;; *) finish 6 ;; esac
