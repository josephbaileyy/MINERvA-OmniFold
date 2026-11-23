#!/bin/bash
# MSR connect B, the build (DECLARATION.md rev 4 section 8, with the director's rulings for B of 2026-11-23). On a
# Perlmutter login node, from a /dev/shm copy of itself whose path is $1; it deletes that copy at exit. Derived from
# connect P (msr_probe_connect.sh fd7957fa, run clean as attempt 2), with the same fences (cov2d's rev 3 7e81a721,
# embedded and sha-checked, then this lane's sacct fence), the same clone, sums and overlap steps, and the same
# records-on-every-stop. Job states come from sacct only.
#   usage: msr_build_connect.sh <self> <window_end_epoch> <fence prefixes, comma-separated>
# In order, each failure a final stop: the window; the fences; $OUT (fresh) absent; the clone at M, clean, the msr files
# at their sha256; the overlap CLEAR; the probe's three staged copies (msr-p-20261122/stage, this lane's own) re-checked
# by O_NOATIME sha256 against their pins (a mismatch is a STOP); then the build, one part per process, in order r5d, r2d,
# t3 (msr_build build --part; each refuses rc 9 with no product if its peak RSS exceeds 8e9 B; each rc is checked); the
# SHA256SUMS of the products; the clean-tree check. The records (logs and the products under build/, not the T3 stage
# copies) are copied with dd iflag=noatime, checked and tarred. Writes only $OUT and /dev/shm/msr-connect. Nothing to
# CFS. No set -u. Any stop is final.
SELF=$1; WEND=$2; FENCE=$3
set -o pipefail
TAG=build
M=68b9f96b917a890fb52d349c645bc4662097322e
OUT=/pscratch/sd/j/josephrb/msr-b-20261123
PST=/pscratch/sd/j/josephrb/msr-p-20261122/stage
D=$OUT/deploy
FR=$OUT/fetch-$TAG
SHM=/dev/shm/msr-connect
PY=$HOME/.conda/envs/root_6_28/bin/python3
T3=/pscratch/sd/j/josephrb/t3p-20261121
NPZ_SHA=07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f
BKG_SHA=2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955
BANK_SHA=60416384474d1a3b0644f1e09869cf09371382ecbf3c116b1ed110cd47341e2f
FENCE_SHA=7e81a721476da987a0e1262ab2054132bd8440cd49b0dc7a5c4f01d50a310738
bail() { echo "BAIL $*"; rm -rf -- "$SHM"; rm -f -- "$SELF"; exit 9; }   # a precondition failed: nothing in $OUT
[[ "$WEND" =~ ^[0-9]{10}$ ]] || bail "window end '$WEND'"
now=$(date +%s); [ "$now" -le "$WEND" ] || bail "the window ended (now $now > $WEND)"
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || bail "fence '$FENCE'"
[ ! -e "$OUT" ] || bail "$OUT exists"
[ -d "$PST" ] || bail "no $PST"
[ ! -e "$SHM" ] || bail "$SHM exists"
[ -x "$PY" ] || bail "no $PY"

# ---- cov2d's fence, rev 3, exactly (embedded, sha-checked), then this lane's sacct fence for the other prefixes
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
  bad=$(printf '%s\n' "$rows" | awk -F'|' -v pre="$FENCE,msr_" '
    BEGIN { n = split(pre, P, ",") }
    NF >= 3 {
      st = $3; sub(/ by [0-9]+$/, "", st)
      term = (st ~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)$/)
      if (term) next
      for (i = 1; i <= n; i++) if (P[i] != "" && index($2, P[i]) == 1) { print; break }
    }') || { echo "fence awk failed"; return 2; }
  [ -z "$bad" ] || { echo "fenced or msr_ jobs not terminal: $bad"; return 1; }
  return 0
}
fo=$(fence_sacct 2>&1) || bail "fence (sacct) not clear: $fo"

mkdir -m 700 "$OUT" "$OUT/logs" || bail "mkdir $OUT"
LOG=$OUT/logs/connect-$TAG.log
exec > "$LOG" 2>&1
# every stop after $OUT exists still writes the records tar, so the fetch carries the log of what happened
RECORDED=0
finish() {
  local rc=$1
  if [ "$RECORDED" -eq 0 ]; then RECORDED=1; records || { [ "$rc" -eq 0 ] && rc=4; }; fi
  echo "msr $TAG rc=$rc"; date -u +%FT%TZ; echo "$rc" > "$OUT/logs/connect-$TAG.done"; rm -rf -- "$SHM"; rm -f -- "$SELF"; exit "$rc"
}
records() {
  echo "== records"; date -u +%FT%TZ
  mkdir "$FR" || { echo "records: mkdir $FR failed"; return 1; }
  local roots=(logs) rel src a b fail=0 nf=0
  [ -d "$OUT/build" ] && roots+=(build)
  ( cd "$OUT" && find "${roots[@]}" -type f ! -name "connect-$TAG.log" ! -path '*/stage-t3/*' -print0 | sort -z ) > "$FR.list" \
    || { echo "records: the list failed (find)"; return 1; }
  while IFS= read -r -d '' rel; do
    src="$OUT/$rel"
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
  tar -C "$OUT" -cf "$FR.tar" "fetch-$TAG" || { echo "records: tar failed"; return 1; }
  echo "fetch-$TAG.tar sha256 $(sha256sum "$FR.tar" | cut -d' ' -f1) bytes $(stat -c %s "$FR.tar")"
}
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ; echo "window_end_epoch $WEND (now $now); fence prefixes $FENCE"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/msr_${TAG}.sh"
echo "== cov2d fence rev 3 ($FENCE_SHA)"; printf '%s\n' "$fence_out"
echo "== fence (sacct)"; fence_sacct || { echo "STOP: fence"; finish 9; }; echo "fence clear"
echo "== rpd_ rows (printed; limitation-resolver's flux2 may coexist with these login reads)"
rows=$(sacct -X -n -P -S now-2days -o JobID,JobName,State 2>&1) || { echo "STOP: sacct for rpd_ rows failed: $rows"; finish 9; }
printf '%s\n' "$rows" | awk -F'|' 'index($2, "rpd_") == 1'

# ---- the deploy: a fresh clone at M, clean, the msr files at their sha256
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l) || { echo "STOP: git status failed (before)"; finish 9; }
echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
( cd "$D/nd-unfolding/msr" && sha256sum --strict -c ) <<SUMS || { echo "STOP: the msr files are not the declared ones"; finish 9; }
b3e31354292d167c2a1189eace40719af8e63190f4b74cad001f6f04f05ae9cc  msr_build.py
b8ad1e75c6610e7f2f05d26cee41e29de6ab42733ad78c0586eac9c541b8bc78  msr_overlap.py
SUMS
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONHASHSEED=0
RUN() { ( cd "$D" && nice -n 19 ionice -c3 env -u PYTHONPATH "$PY" -I -B "$@" ); }
echo "threads 2; nice 19; ionice idle; python $("$PY" -c 'import sys; print(sys.version.split()[0])')"

echo "== overlap (msr_overlap.py)"
RUN nd-unfolding/msr/msr_overlap.py "$OUT" --clone "$D"; orc=$?
[ "$orc" -eq 0 ] || { echo "STOP: overlap rc $orc"; finish 9; }

echo "== the probe's staged copies, re-checked by O_NOATIME sha256 against their pins"
RUN nd-unfolding/msr/msr_build.py stat "$PST/of_inputs_5d.npz" "$PST/bkg_dump.npz" "$PST/bank.npz" > "$OUT/logs/stage-recheck.jsonl" \
  || { echo "STOP: stat of the staged copies"; finish 9; }
cat "$OUT/logs/stage-recheck.jsonl"
"$PY" -I - "$OUT/logs/stage-recheck.jsonl" "$NPZ_SHA" "$BKG_SHA" "$BANK_SHA" <<'PYX' || { echo "STOP: a staged copy is not at its pin"; finish 9; }
import json, sys
got = [json.loads(l)["sha256"] for l in open(sys.argv[1]).read().splitlines()]
want = sys.argv[2:5]
print("staged copies at their pins:", got == want)
sys.exit(0 if got == want else 1)
PYX

echo "== build: one part per process (r5d, r2d, t3)"
mkdir "$OUT/build" || { echo "STOP: mkdir $OUT/build"; finish 9; }
for part in r5d r2d t3; do
  RUN nd-unfolding/msr/msr_build.py build --part "$part" --npz "$PST/of_inputs_5d.npz" --bkg "$PST/bkg_dump.npz" \
    --bank "$PST/bank.npz" --t3-run "$T3" --t3-stage-json "$T3/stage.json" --out "$OUT/build" \
    > "$OUT/logs/build-$part.json" 2> "$OUT/logs/build-$part.err"; c=$?
  cat "$OUT/logs/build-$part.json"
  [ "$c" -eq 0 ] || { echo "STOP: build $part rc $c; stderr tail:"; tail -20 "$OUT/logs/build-$part.err"; finish 5; }
done
( cd "$OUT/build" && sha256sum r5d.npz r5d.json r2d.npz r2d.json t3.npz t3.json ) > "$OUT/build/SHA256SUMS" \
  || { echo "STOP: product sums"; finish 5; }
cat "$OUT/build/SHA256SUMS"
gs=$(git -C "$D" status --porcelain --ignored) || { echo "STOP: git status failed (after)"; finish 9; }
n=$(printf '%s\n' "$gs" | awk 'NF && index($0, "__pycache__") == 0 { c++ } END { print c + 0 }')
echo "porcelain --ignored lines after (pycache excluded): $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }

# ---- the records (written by finish, T3's pattern: dd iflag=noatime copies, each checked, then one tar)
finish 0
