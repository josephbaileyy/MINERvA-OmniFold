#!/bin/bash
# MSR connect P, the probe (DECLARATION.md rev 2 section 8). On a Perlmutter login node, from a /dev/shm copy of itself
# whose path is $1; it deletes that copy at exit. Derived from T3's reviewed read connect (t3p_read_connect.sh rev 1,
# 9c4b604c), with cov2d's fence rev 2 (cov2d_fence.sh 3fbc9cbd, embedded below as base64 and checked) and this lane's
# sacct fence for the other prefixes.
#   usage: msr_probe_connect.sh <self> <window_end_epoch> <fence prefixes, comma-separated>
# In order, each failure a final stop:
#   the window (the epoch the launcher computed from date, never typed); cov2d_fence.sh rev 2 CLEAR (exit 0); no job of
#   this user whose name starts with a fenced prefix or msr_ is in a non-terminal state, by sacct (rpd_ rows, which
#   limitation-resolver's flux2 run may hold and which may coexist with these login reads, are printed, not fenced);
#   $OUT absent; a fresh clone at M into $OUT/deploy, clean, msr_build.py and msr_overlap.py at their sha256;
#   msr_overlap.py CLEAR against cov2d's and rpd's sets.
# Then, all reads O_NOATIME (msr_build stat, find-bank, dd iflag=noatime): stat and sha256 of every declared input and
# of re1's 3D/4D npz (the inventory); the IBUKT bank located by sha256; dd copies of of_inputs_5d.npz, bkg_dump.npz and
# bank.npz into $OUT/stage, each at its pinned sha256 (every later plain read is of these copies); the timed probe at
# row fractions 0.02 and 0.10 for 5D and 2D (msr_build probe: seconds and in-process peak RSS), the two-point linear
# extrapolation to the full build, and the hard gate (every part <= 1800 s and <= 8e9 B); if the gate passes,
# C-DID-CONS (msr_build did-cons, the D-ID side and the IBU-1 side, each its own process under timeout 2400), with the
# four lists' sha256 compared. Then the records, as T3's: dd iflag=noatime copies into $OUT/fetch-probe/, checked, one tar.
# Writes only $OUT and /dev/shm/msr-connect (removed at exit). Nothing to CFS. No set -u. Any stop is final.
SELF=$1; WEND=$2; FENCE=$3
set -o pipefail
TAG=probe
M=0789e2aad16171b69ae962af427f5963c2fe1fe6
OUT=/pscratch/sd/j/josephrb/msr-p-20261122
D=$OUT/deploy
ST=$OUT/stage
FR=$OUT/fetch-$TAG
SHM=/dev/shm/msr-connect
PY=$HOME/.conda/envs/root_6_28/bin/python3
T3=/pscratch/sd/j/josephrb/t3p-20261121
IBUKT=/pscratch/sd/j/josephrb/ibukt-20261119-d
RE1=/pscratch/sd/j/josephrb/methods-paper/re1-20261022/out
NPZ_SHA=07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f
BKG_SHA=2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955
BANK_SHA=60416384474d1a3b0644f1e09869cf09371382ecbf3c116b1ed110cd47341e2f
FENCE_SHA=3fbc9cbd6c08d4c86c71aeeccf28b0b3d8a77393121ef23787c1d421b682171e
bail() { echo "BAIL $*"; rm -rf -- "$SHM"; rm -f -- "$SELF"; exit 9; }   # a precondition failed: nothing in $OUT
[[ "$WEND" =~ ^[0-9]{10}$ ]] || bail "window end '$WEND'"
now=$(date +%s); [ "$now" -le "$WEND" ] || bail "the window ended (now $now > $WEND)"
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || bail "fence '$FENCE'"
[ ! -e "$OUT" ] || bail "$OUT exists"
[ ! -e "$SHM" ] || bail "$SHM exists"
[ -x "$PY" ] || bail "no $PY"

# ---- cov2d's fence, rev 2, exactly (embedded, sha-checked), then this lane's sacct fence for the other prefixes
mkdir -m 700 "$SHM" || bail "mkdir $SHM"
base64 -d > "$SHM/cov2d_fence.sh" <<'B64' || bail "fence decode"
IyEvYmluL2Jhc2gKIyBjb3YyZF9mZW5jZS5zaCByZXYgMiAoMjAyNi0xMS0yMik6IHRoZSBDT1Yy
RCBmZW5jZSwgcnVuIG9uIGEgUGVybG11dHRlciBsb2dpbiBub2RlIGJlZm9yZSBhbm90aGVyIGxh
bmUncyBjb25uZWN0LgojIFJlYWRzIHNhY2N0IG9ubHkgKG5vIHNxdWV1ZTogc3RhbmRpbmcgcnVs
ZSkuIFJlcGxhY2VzIHJldiAxIChzaGEyNTYgMTZhMmE1Y2QuLi4pLCB3aGljaCBjYWxsZWQgc3F1
ZXVlLgojIENMRUFSIChleGl0IDApIG9ubHkgaWYgc2FjY3QgZXhpdHMgMCwgZXZlcnkgbGluZSBp
dCB3cml0ZXMgKHN0ZG91dCBhbmQgc3RkZXJyIHRvZ2V0aGVyKSBpcyBhIHdlbGwtZm9ybWVkCiMg
Sm9iSUR8Sm9iTmFtZXxTdGF0ZSByb3cgd2l0aCBhIG51bWVyaWMgSm9iSUQsIGFuZCBldmVyeSBy
b3cgbmFtZWQgY292MmQqIG9yIHQyYSogKG91cnMsIGxhc3QgNjAgZGF5cykgaXMgaW4gYQojIHRl
cm1pbmFsIHN0YXRlLiBBbnl0aGluZyBlbHNlIGlzIGV4aXQgMzogYW4gdW5lbmRlZCBvciB1bmNs
YXNzaWZpYWJsZSBtYXRjaGluZyByb3csIGEgbWFsZm9ybWVkIG9yIHN0cmF5IGxpbmUKIyAoc28g
YW4gZXJyb3Igc2FjY3QgcHJpbnRzIG9uIHN0ZGVyciB3aGlsZSBleGl0aW5nIDAgcmVmdXNlcyks
IHNhY2N0IGZhaWxpbmcsIG9yIHRoZSBzdGFydCB0aW1lIGZhaWxpbmcuCiMgS25vd24gZ2FwLCBz
YWNjdC1vbmx5IGJ5IHJ1bGU6IHNhY2N0J3MgZGVmYXVsdCBsaXN0aW5nIG9taXRzIGEgcGVuZGlu
ZyBqb2Igd2l0aCBubyBFbGlnaWJsZVRpbWUgKHNiYXRjaCAtLWhvbGQsCiMgc2NvbnRyb2wgaG9s
ZCwgYXJyYXkgdGFza3MgaGVsZCBieSBhICVsaW1pdCkgYW5kIGNhbiBsYWcgc2x1cm1kYmQgYnJp
ZWZseS4KIyBBIGNvbm5lY3QgdGhhdCByZWxpZXMgb24gdGhpcyBmZW5jZSBhbHNvIHRha2VzIGEg
ZnJlc2ggYWNrIGZyb20gdGhlIGNvdjJkIHNlc3Npb24sIHdoaWNoIGNvdmVycyB0aGF0IGdhcC4K
IyBTdGF0ZSBpcyBjbGFzc2lmaWVkIGhlcmUgYWdhaW5zdCBhIGNsb3NlZCB0ZXJtaW5hbCBzZXQg
KGZpcnN0IHdvcmQgb2YgU3RhdGUsIHNvICJDQU5DRUxMRUQgYnkgTiIgY291bnRzKTsKIyBhbnkg
b3RoZXIgc3RhdGUsIGluY2x1ZGluZyBvbmVzIHRoaXMgZmlsZSBkb2VzIG5vdCBuYW1lLCByZWZ1
c2VzLiBzYWNjdCAtcyBpcyBub3QgdXNlZCAoUGVybG11dHRlciByZWplY3RzIENGKS4KIyBXcml0
ZXMgbm90aGluZy4gTWF5IGJlIGxhdW5jaGVkIGZyb20gYSAvZGV2L3NobSBjb3B5IG9mIGl0c2Vs
ZiB3aG9zZSBwYXRoIGlzICQxLiBBdCBleGl0IGl0IGRlbGV0ZXMgJDEgb25seSBpZiAkMQojIGlz
IHVuZGVyIC9kZXYvc2htLywgaGFzIG5vIC4uIGNvbXBvbmVudCwgYW5kIGlzIHRoZSBydW5uaW5n
IHNjcmlwdCBpdHNlbGYgKFsgIiQxIiAtZWYgIiQwIiBdKTsgYW55IG90aGVyICQxIGlzCiMga2Vw
dCBhbmQgbmFtZWQuIChXaXRob3V0IHRoZSAuLiBydWxlLCAvZGV2L3NobS8uLi88cmVwbz4vY292
MmRfZmVuY2Uuc2ggcnVuIGZyb20gdGhlIHJlcG8gd291bGQgZGVsZXRlIHRoZSByZXBvIGZpbGUu
KQpTRUxGPSQxCmZpbigpIHsKICBpZiBbIC1uICIkU0VMRiIgXTsgdGhlbgogICAgY2FzZSAkU0VM
RiBpbgogICAgICAqLy4uLyp8Ki8uLikgZWNobyAic2VsZi1jb3B5IG5vdCByZW1vdmVkOiAkU0VM
RiIgOzsKICAgICAgL2Rldi9zaG0vKikgaWYgWyAiJFNFTEYiIC1lZiAiJDAiIF07IHRoZW4gcm0g
LWYgLS0gIiRTRUxGIjsgZWxzZSBlY2hvICJzZWxmLWNvcHkgbm90IHJlbW92ZWQ6ICRTRUxGIjsg
ZmkgOzsKICAgICAgKikgZWNobyAic2VsZi1jb3B5IG5vdCByZW1vdmVkOiAkU0VMRiIgOzsKICAg
IGVzYWMKICBmaQogIGV4aXQgIiQxIgp9CmVjaG8gImZlbmNlIGhvc3Q9JChob3N0bmFtZSkgdXRj
PSQoZGF0ZSAtdSArJUZUJVRaKSIKIyBzYWNjdCByZWFkcyAtUyBpbiB0aGUgY2x1c3RlcidzIGxv
Y2FsIHRpbWU7IDYwIGRheXMgaXMgZmFyIHBhc3QgdGhlIHJlcXVpcmVkIDQ4IGggZWl0aGVyIHdh
eS4Kc3RhcnQ9JChkYXRlIC1kICc2MCBkYXlzIGFnbycgKyVGVCVUKSB8fCB7IGVjaG8gIkZFTkNF
IFJFRlVTRUQ6IHN0YXJ0IHRpbWUgZmFpbGVkIjsgZmluIDM7IH0KW1sgJHN0YXJ0ID1+IF5bMC05
XXs0fS1bMC05XXsyfS1bMC05XXsyfVRbMC05XXsyfTpbMC05XXsyfTpbMC05XXsyfSQgXV0gfHwg
eyBlY2hvICJGRU5DRSBSRUZVU0VEOiBzdGFydCB0aW1lIG1hbGZvcm1lZDogJyRzdGFydCciOyBm
aW4gMzsgfQp1c2VyPSQoaWQgLXVuKSB8fCB7IGVjaG8gIkZFTkNFIFJFRlVTRUQ6IGlkIC11biBm
YWlsZWQiOyBmaW4gMzsgfQpbIC1uICIkdXNlciIgXSB8fCB7IGVjaG8gIkZFTkNFIFJFRlVTRUQ6
IGVtcHR5IHVzZXIiOyBmaW4gMzsgfQplY2hvICJzYWNjdCAtWCAtbiAtUCAtdSAkdXNlciAtUyAk
c3RhcnQgLUUgbm93IC1vIEpvYklELEpvYk5hbWUsU3RhdGUgMj4mMSIKcz0kKHNhY2N0IC1YIC1u
IC1QIC11ICIkdXNlciIgLVMgIiRzdGFydCIgLUUgbm93IC1vIEpvYklELEpvYk5hbWUsU3RhdGUg
Mj4mMSkgfHwgeyBlY2hvICJGRU5DRSBSRUZVU0VEOiBzYWNjdCBmYWlsZWQiOyBwcmludGYgJyVz
XG4nICIkcyIgfCBzZWQgJ3MvXi9zYWNjdDogLyc7IGZpbiAzOyB9CnY9JChwcmludGYgJyVzXG4n
ICIkcyIgfCBhd2sgLUYnfCcgJwogIEJFR0lOIHsgc3BsaXQoIkJPT1RfRkFJTCBDQU5DRUxMRUQg
Q09NUExFVEVEIERFQURMSU5FIEZBSUxFRCBOT0RFX0ZBSUwgT1VUX09GX01FTU9SWSBQUkVFTVBU
RUQgVElNRU9VVCIsIHQsICIgIikKICAgICAgICAgIGZvciAoaSBpbiB0KSB0ZXJtW3RbaV1dID0g
MSB9CiAgL14kLyB7IG5leHQgfQogIE5GICE9IDMgfHwgJDEgIX4gL15bMC05XSsoW18rXS4qKT8k
LyB7IHByaW50ICJtYWxmb3JtZWQ6ICIgJDA7IGJhZCA9IDE7IG5leHQgfQogICQyIH4gL14oY292
MmR8dDJhKS8geyBuKys7IHNwbGl0KCQzLCB3LCAiICIpOyBpZiAoISh3WzFdIGluIHRlcm0pKSB7
IHByaW50ICJ1bmVuZGVkOiAiICQwOyBiYWQgPSAxIH0gfQogIEVORCB7IHByaW50ICJtYXRjaGlu
ZyByb3dzOiAiIG4gKyAwOyBleGl0IGJhZCB9JykKcmM9JD8KcHJpbnRmICclc1xuJyAiJHYiIHwg
c2VkICdzL14vc2FjY3QgLycKWyAiJHJjIiAtZXEgMCBdIHx8IHsgZWNobyAiRkVOQ0UgUkVGVVNF
RDogYW4gdW5lbmRlZCwgdW5jbGFzc2lmaWFibGUgb3IgbWFsZm9ybWVkIHNhY2N0IHJvdyI7IGZp
biAzOyB9CmVjaG8gIkZFTkNFIENMRUFSIgpmaW4gMAo=
B64
[ "$(sha256sum "$SHM/cov2d_fence.sh" | cut -d' ' -f1)" = "$FENCE_SHA" ] || bail "cov2d_fence.sh is not rev 2"
fence_out=$(bash "$SHM/cov2d_fence.sh" 2>&1); frc=$?
[ "$frc" -eq 0 ] || { printf '%s\n' "$fence_out"; bail "cov2d fence rev 2 not clear (rc $frc)"; }
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
    }')
  [ -z "$bad" ] || { echo "fenced or msr_ jobs not terminal: $bad"; return 1; }
  return 0
}
fence_sacct > /dev/null 2>&1 || bail "fence (sacct) not clear"

mkdir -m 700 "$OUT" "$OUT/logs" || bail "mkdir $OUT"
LOG=$OUT/logs/connect-$TAG.log
exec > "$LOG" 2>&1
finish() { echo "msr $TAG rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-$TAG.done"; rm -rf -- "$SHM"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ; echo "window_end_epoch $WEND (now $now); fence prefixes $FENCE"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/msr_${TAG}.sh"
echo "== cov2d fence rev 2 ($FENCE_SHA)"; printf '%s\n' "$fence_out"
echo "== fence (sacct)"; fence_sacct || { echo "STOP: fence"; finish 9; }; echo "fence clear"
echo "== rpd_ rows (printed; limitation-resolver's flux2 may coexist with these login reads)"
sacct -X -n -P -S now-2days -o JobID,JobName,State 2>&1 | awk -F'|' 'index($2, "rpd_") == 1'

# ---- the deploy: a fresh clone at M, clean, the msr files at their sha256
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l) || { echo "STOP: git status failed (before)"; finish 9; }
echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
( cd "$D/nd-unfolding/msr" && sha256sum --strict -c ) <<SUMS || { echo "STOP: the msr files are not the declared ones"; finish 9; }
97a1f367e967e08742e9d886314507669f2cba90a5947b873dc1e5e93d21c3d6  msr_build.py
21287901b9dc4a07f144c87ca5bdf45bae8f9ade2da4c76b24fe2398c2207c70  msr_overlap.py
SUMS
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONHASHSEED=0
RUN() { ( cd "$D" && nice -n 19 ionice -c3 env -u PYTHONPATH "$PY" -I -B "$@" ); }
echo "threads 2; nice 19; ionice idle; python $("$PY" -c 'import sys; print(sys.version.split()[0])')"

echo "== overlap (msr_overlap.py)"
RUN nd-unfolding/msr/msr_overlap.py "$OUT" --clone "$D"; orc=$?
[ "$orc" -eq 0 ] || { echo "STOP: overlap rc $orc"; finish 9; }

echo "== inventory: stat (incl. atime) and O_NOATIME sha256"
RUN nd-unfolding/msr/msr_build.py stat "$T3/stage/of_inputs_5d.npz" "$T3/stage/bkg_dump.npz" "$T3/stage.json" \
  "$T3/log-floor/SHA256SUMS" "$RE1/3d/of_inputs_3d.npz" "$RE1/4d/of_inputs_4d.npz" > "$OUT/logs/stat.jsonl" \
  || { echo "STOP: stat"; finish 9; }
cat "$OUT/logs/stat.jsonl"
RUN nd-unfolding/msr/msr_build.py find-bank "$IBUKT" "$BANK_SHA" > "$OUT/logs/find-bank.jsonl"; brc=$?
cat "$OUT/logs/find-bank.jsonl"
[ "$brc" -eq 0 ] || { echo "STOP: no bank.npz at $BANK_SHA under $IBUKT"; finish 9; }
BANK=$("$PY" -I -c 'import json,sys; print(json.loads(open(sys.argv[1]).read().splitlines()[-1])["matches"][0])' "$OUT/logs/find-bank.jsonl") \
  || { echo "STOP: bank path"; finish 9; }
echo "bank $BANK"

echo "== stage: dd iflag=noatime copies, each at its pin"
mkdir "$ST" || { echo "STOP: mkdir $ST"; finish 9; }
for spec in "$T3/stage/of_inputs_5d.npz:of_inputs_5d.npz:$NPZ_SHA" "$T3/stage/bkg_dump.npz:bkg_dump.npz:$BKG_SHA" "$BANK:bank.npz:$BANK_SHA"; do
  src=${spec%%:*}; rest=${spec#*:}; name=${rest%%:*}; pin=${rest##*:}
  dd if="$src" of="$ST/$name" iflag=noatime bs=16M status=none || { echo "STOP: copy $name"; finish 9; }
  got=$(sha256sum "$ST/$name" | cut -d' ' -f1) || { echo "STOP: hash $name"; finish 9; }
  echo "$name sha256 $got (pin $pin)"
  [ "$got" = "$pin" ] || { echo "STOP: $name is not at its pin"; finish 9; }
done

echo "== probe (msr_build probe; in-process seconds and peak RSS)"
gate=1
for part in 5d 2d; do
  for frac in 0.02 0.10; do
    RUN nd-unfolding/msr/msr_build.py probe --part "$part" --fraction "$frac" --npz "$ST/of_inputs_5d.npz" \
      --bkg "$ST/bkg_dump.npz" --bank "$ST/bank.npz" --out "$OUT/probe-$part-$frac" > "$OUT/logs/probe-$part-$frac.json" \
      || { echo "STOP: probe $part $frac"; finish 5; }
    cat "$OUT/logs/probe-$part-$frac.json"
  done
  ext=$("$PY" -I - "$OUT/logs/probe-$part-0.02.json" "$OUT/logs/probe-$part-0.10.json" <<'PYX'
import json, sys
a, b = (json.loads(open(p).read().splitlines()[-1]) for p in sys.argv[1:3])
def lin(k):
    slope = (b[k] - a[k]) / (b["fraction"] - a["fraction"])
    return a[k] + slope * (1.0 - a["fraction"])
s, r = lin("seconds"), lin("peak_rss_bytes")
print(json.dumps({"part": a["part"], "seconds_full_est": round(s, 1), "peak_rss_full_est": int(r),
                  "login_ok": bool(s <= 1800 and r <= 8e9)}))
PYX
) || { echo "STOP: extrapolation $part"; finish 5; }
  echo "extrapolation $ext"
  case "$ext" in *'"login_ok": true'*) ;; *) gate=0 ;; esac
done
echo "GATE login_ok=$gate (every part <= 1800 s and <= 8e9 B, two-point linear extrapolation)"

if [ "$gate" -eq 1 ]; then
  echo "== C-DID-CONS (each side its own process, timeout 2400 s)"
  for side in did ibu1; do
    timeout 2400 bash -c "cd '$D' && nice -n 19 ionice -c3 env -u PYTHONPATH '$PY' -I -B nd-unfolding/msr/msr_build.py did-cons --side $side --npz '$ST/of_inputs_5d.npz' --bkg '$ST/bkg_dump.npz' --out '$OUT/didcons-$side'" \
      > "$OUT/logs/didcons-$side.json" 2> "$OUT/logs/didcons-$side.err"; c=$?
    echo "did-cons $side rc=$c"; cat "$OUT/logs/didcons-$side.json"
  done
  for name in j_cells reco_cells; do
    a=$(sha256sum "$OUT/didcons-did/did_$name.txt" 2>/dev/null | cut -d' ' -f1)
    b=$(sha256sum "$OUT/didcons-ibu1/ibu1_$name.txt" 2>/dev/null | cut -d' ' -f1)
    if [ -n "$a" ] && [ "$a" = "$b" ]; then echo "C-DID-CONS $name EQUAL $a"; else echo "C-DID-CONS $name DIFFERS (did '$a', ibu1 '$b')"; fi
  done
else
  echo "C-DID-CONS deferred to connect B (the gate sends the build to a job)"
fi
n=$(git -C "$D" status --porcelain --ignored | grep -v '__pycache__' | wc -l) || { echo "STOP: git status failed (after)"; finish 9; }
echo "porcelain --ignored lines after (pycache excluded): $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }

# ---- the records for the fetch: dd iflag=noatime copies, each checked, then one tar (T3's pattern)
echo "== records"
date -u +%FT%TZ
mkdir "$FR" || { echo "STOP: mkdir $FR"; finish 9; }
roots=(logs); for d in "$OUT"/didcons-*; do [ -d "$d" ] && roots+=("$(basename "$d")"); done
( cd "$OUT" && find "${roots[@]}" -type f ! -name '*.npz' ! -name "connect-$TAG.log" ! -path '*/inputs/*' -print0 | sort -z ) > "$FR.list" \
  || { echo "STOP: the records list failed (find)"; finish 4; }
fail=0; nf=0
while IFS= read -r -d '' rel; do
  src="$OUT/$rel"
  mkdir -p "$FR/$(dirname "$rel")" || { echo "mkdir failed: $rel"; fail=1; continue; }
  dd if="$src" of="$FR/$rel" iflag=noatime status=none || { echo "copy failed: $rel"; fail=1; continue; }
  a=$(dd if="$src" iflag=noatime status=none | sha256sum | cut -d' ' -f1) || { echo "re-read failed: $rel"; fail=1; continue; }
  b=$(sha256sum "$FR/$rel" | cut -d' ' -f1) || { echo "hash failed: $rel"; fail=1; continue; }
  [ "$a" = "$b" ] || { echo "copy differs: $rel"; fail=1; }
  echo "$b  $rel" >> "$FR.sums"; nf=$((nf + 1))
done < "$FR.list"
[ "$fail" -eq 0 ] && [ "$nf" -gt 0 ] || { echo "STOP: a record copy failed or differs, or no records ($nf)"; finish 4; }
rm -f -- "$FR.list"
mv "$FR.sums" "$FR/RECORDS.SHA256SUMS" || finish 4
echo "records copied: $nf files, $(du -sb "$FR" | cut -f1) bytes"
tar -C "$OUT" -cf "$FR.tar" "fetch-$TAG" || { echo "STOP: tar"; finish 4; }
echo "fetch-$TAG.tar sha256 $(sha256sum "$FR.tar" | cut -d' ' -f1) bytes $(stat -c %s "$FR.tar")"
finish 0
