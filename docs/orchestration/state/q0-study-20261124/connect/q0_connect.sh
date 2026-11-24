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
XSHA=9ef4a1f247726532c2c98c84de9f66af221db55a949006ce0d9ec43b38274255
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
IyEvdXNyL2Jpbi9lbnYgcHl0aG9uMwoiIiJUaGUgcTAgc3R1ZHkncyBleHRyYWN0IChQTEFOLm1k
IHNlY3Rpb24gMiksIG9uY2UsIG9uIGEgUGVybG11dHRlciBsb2dpbiBub2RlIHVuZGVyIHRoZSBk
aXJlY3RvcidzIEdPIGZvciBpdHMgc2hhLgoKRnJvbSB0aGUgNUQgQ1Ygb21uaWZpbGUncyBgbWNf
c2lnbmFsX3JlY29gIHRyZWUgT05MWSAodGhlIGBkYXRhYCB0cmVlIGFuZCBldmVyeSAibWVhc3Vy
ZWQiIGtleSBhcmUgbmV2ZXIgb3BlbmVkKSwgZm9yCnRoZSByb3dzIHdpdGggc2ltX3Bhc3MgdHJ1
ZTogdGhlIHJlY28gbXVvbiAocFQsIHB8fCksIEVfYXZhaWwsIHEzIGFuZCBXLCB0aGUgQ1Ygd2Vp
Z2h0IHdfcmVjbywgdHJ1dGggcTMgYW5kIFcsIGFuZCBxMApyZWNvdmVyZWQgaW4gZmxvYXQ2NCBm
cm9tIChwVCwgcHx8LCByZWNvIHEzKSBieSBpbnZlcnRpbmcgUmVjb1EzIChDVlVuaXZlcnNlLmg6
MjA4LTIxOSksIGV4YWN0bHkgYXMgTTQtVyBkaWQKKG00LXcvcHJvYmVfb21uaS5weTo2Mi03Nzsg
TTQtVy1SRUNPUkQubWQ6MTA0KS4gRXZlcnkgcmVhZCBpcyBPX05PQVRJTUU7IHRoZSBmaWxlJ3Mg
YXRpbWUgaXMgY2hlY2tlZCBiZWZvcmUgYW5kIGFmdGVyLgoKU1RPUHMgKG5vIG5weiB3cml0dGVu
KTogdGhlIG9tbmlmaWxlJ3Mgc2hhMjU2IGlzIG5vdCB0aGUgcGluIChyYyAzKTsgYSBuYW1lZCBi
cmFuY2ggaXMgbWlzc2luZyAocmMgMyk7IHRoZSBwYXNzaW5nIGNvdW50CmlzIG5vdCAyMCw0OTgs
MDEzIChyYyAzKTsgdGhlIG9tbmlmaWxlJ3MgYXRpbWUgY2hhbmdlZCAocmMgNCk7IHRoZSByZWNv
dmVyeSBjb250cm9sIGZhaWxzLCBtYXggfFcgLSBXKHEwKXwgPiAxZS02IEdlViBvdmVyCnJvd3Mg
d2l0aCBxMF9zdGF0dXMgMCBhbmQgV14yID49IDAgKHJjIDUpLiBBIHJlZnVzZWQgcHJlY29uZGl0
aW9uIChvdXRwdXQgZXhpc3RzLCBubyBPX05PQVRJTUUpIGlzIHJjIDkuCgogICAgcTBfZXh0cmFj
dC5weSAtLW9tbmkgRklMRSAtLW91dCBESVIgICAgICAgIChESVIgbXVzdCBleGlzdCBhbmQgYmUg
ZW1wdHk7IHdyaXRlcyBxMF9leHRyYWN0Lm5weiBhbmQgcTBfZXh0cmFjdC5qc29uKQoiIiIKZnJv
bSBfX2Z1dHVyZV9fIGltcG9ydCBhbm5vdGF0aW9ucwoKaW1wb3J0IGFyZ3BhcnNlCmltcG9ydCBo
YXNobGliCmltcG9ydCBqc29uCmltcG9ydCBvcwppbXBvcnQgcmVzb3VyY2UKaW1wb3J0IHN5cwpp
bXBvcnQgdGltZQpmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGgKCmltcG9ydCBudW1weSBhcyBucAoK
T01OSV9TSEEgPSAiYjZkMjY1MWNmZGJjNTI3OTBjYzdlZDYwMzJmMjA2MmEzZTBlYTUwYzEyZDYz
NzI1YmViYTI5MDk4ZGQ1MTc1YSIgICAjIHM1Yy9jb250cmFjdC5qc29uIGN2X29tbmlmaWxlClRS
RUUgPSAibWNfc2lnbmFsX3JlY28iCkJSQU5DSEVTID0gWyJzaW0iLCAic2ltX3B6IiwgInNpbV9l
YXZhaWwiLCAic2ltX3EzIiwgInNpbV9XIiwgInNpbV9wYXNzIiwgIndfcmVjbyIsICJNQyIsICJN
Q19weiIsICJNQ19xMyIsICJNQ19XIl0KRVhQRUNURURfUEFTUyA9IDIwNDk4MDEzICAgICAgICAg
ICMgc3RlcDAtdHJlZWNoZWNrLXRyYW5zY3JpcHQudHh0Ojk7IE00LVctUkVDT1JELm1kOjEwOApN
X04sIE1fUCA9IDkzOS41NjUzNiwgOTM4LjI3MjAxMyAgIyBNZVYsIG00LXcvY29tbW9uLnB5OjQt
NQpNX0JBUiA9ICgxLjUgKiBNX04gKyBNX1ApIC8gMi41ICAgIyBtNC13L2NvbW1vbi5weTo2Ck1f
TVUgPSAxMDUuNjU4MyAgICAgICAgICAgICAgICAgICAjIE1lViwgTWluZXJ2YVVuaXRzOjpNX211
IChtNC13L2NvbW1vbi5weTo3KQpSRUNPVkVSWV9UT0xfR0VWID0gMWUtNgpOT0FUSU1FID0gZ2V0
YXR0cihvcywgIk9fTk9BVElNRSIsIE5vbmUpCkFMTE9XX1BMQUlOX1JFQUQgPSBGYWxzZSAgICAg
ICAgICAjIHRlc3RzIG9ubHkgKG1hY09TIGhhcyBubyBPX05PQVRJTUUpOyB0aGUgbm9kZSBydW4g
bmV2ZXIgc2V0cyBpdAoKCmNsYXNzIFN0b3AoRXhjZXB0aW9uKToKICAgIGRlZiBfX2luaXRfXyhz
ZWxmLCByYzogaW50LCBtc2c6IHN0cik6CiAgICAgICAgc3VwZXIoKS5fX2luaXRfXyhtc2cpCiAg
ICAgICAgc2VsZi5yYyA9IHJjCgoKZGVmIGZsYWdzKCkgLT4gaW50OgogICAgaWYgTk9BVElNRSBp
cyBOb25lOgogICAgICAgIGlmIEFMTE9XX1BMQUlOX1JFQUQ6CiAgICAgICAgICAgIHJldHVybiBv
cy5PX1JET05MWQogICAgICAgIHJhaXNlIFN0b3AoOSwgIk9fTk9BVElNRSBpcyBub3QgYXZhaWxh
YmxlIGhlcmUiKQogICAgcmV0dXJuIG9zLk9fUkRPTkxZIHwgTk9BVElNRQoKCmRlZiBzaGEyNTZf
bm9hdGltZShwYXRoOiBzdHIpIC0+IHN0cjoKICAgIGggPSBoYXNobGliLnNoYTI1NigpCiAgICBm
ZCA9IG9zLm9wZW4ocGF0aCwgZmxhZ3MoKSkKICAgIHRyeToKICAgICAgICB3aGlsZSBUcnVlOgog
ICAgICAgICAgICBiID0gb3MucmVhZChmZCwgMSA8PCAyNCkKICAgICAgICAgICAgaWYgbm90IGI6
CiAgICAgICAgICAgICAgICByZXR1cm4gaC5oZXhkaWdlc3QoKQogICAgICAgICAgICBoLnVwZGF0
ZShiKQogICAgZmluYWxseToKICAgICAgICBvcy5jbG9zZShmZCkKCgpkZWYgcmVjb3Zlcl9xMChw
dCwgcHosIHEzKToKICAgICIiInEwIChNZVYpIGZyb20gcmVjbyAocFQsIHB8fCwgcTMpIGluIE1l
ViwgaW52ZXJ0aW5nIFJlY29RMzsgcmV0dXJucyAocTAsIHN0YXR1cykgd2l0aCBzdGF0dXMgMCBy
ZWNvdmVyZWQsCiAgICAxIFJlY29RMydzIFFeMiBjbGFtcCBmaXJlZCAoc28gcTMgPSBxMCwgYW5k
IHEwIDo9IHEzKSwgMiBhIG5vbi1maW5pdGUgaW5wdXQgb3Igb3V0cHV0IChwcm9iZV9vbW5pLnB5
OjY4LTc1KS4iIiIKICAgIHB0LCBweiwgcTMgPSAobnAuYXNhcnJheShhLCBucC5mbG9hdDY0KSBm
b3IgYSBpbiAocHQsIHB6LCBxMykpCiAgICBlbXUgPSBucC5zcXJ0KHB0ICogcHQgKyBweiAqIHB6
ICsgTV9NVSAqKiAyKQogICAgYSA9IGVtdSAtIHB6CiAgICBjID0gMi4wICogZW11ICogYSAtIE1f
TVUgKiogMgogICAgd2l0aCBucC5lcnJzdGF0ZShpbnZhbGlkPSJpZ25vcmUiKToKICAgICAgICBx
MCA9IC1hICsgbnAuc3FydChhICogYSAtIGMgKyBxMyAqIHEzKQogICAgICAgIFEyID0gMi4wICog
KGVtdSArIHEwKSAqIGEgLSBNX01VICoqIDIKICAgIGNsYW1wID0gfihRMiA+PSAwKQogICAgcTAg
PSBucC53aGVyZShjbGFtcCwgcTMsIHEwKQogICAgc3RhdHVzID0gbnAud2hlcmUoY2xhbXAsIDEs
IDApLmFzdHlwZShucC5pbnQ4KQogICAgYmFkID0gfihucC5pc2Zpbml0ZShwdCkgJiBucC5pc2Zp
bml0ZShweikgJiBucC5pc2Zpbml0ZShxMykgJiBucC5pc2Zpbml0ZShxMCkpCiAgICBzdGF0dXNb
YmFkXSA9IDIKICAgIHJldHVybiBxMCwgc3RhdHVzCgoKZGVmIHdfZnJvbV9xMChxMCwgcTMpOgog
ICAgIiIiUmVjbyBXIChNZVYpIGZyb20gcTAgYW5kIHEzIChwcm9iZV9vbW5pLnB5Ojc2LTc3KTog
c3FydChtYXgoMCwgKE1fYmFyICsgcTApXjIgLSBxM14yKSk7IGFsc28gV14yIDwgMC4iIiIKICAg
IHcyID0gKE1fQkFSICsgcTApICoqIDIgLSBxMyAqIHEzCiAgICByZXR1cm4gbnAuc3FydChucC5t
YXhpbXVtKHcyLCAwLjApKSwgdzIgPCAwCgoKZGVmIGluX3RydXRoX3BzKHB0LCBweik6CiAgICAi
IiJwcm9iZV9vbW5pLnB5OjEzLTE0ICh1MmQuaW5fdHJ1dGhfcGhhc2Vfc3BhY2UpLCBHZVYsIGlu
Y2x1c2l2ZSBib3VuZHMsIGF0YW4yIDwgMjAgZGVnLiIiIgogICAgd2l0aCBucC5lcnJzdGF0ZShp
bnZhbGlkPSJpZ25vcmUiKToKICAgICAgICByZXR1cm4gKHB0ID49IDApICYgKHB0IDw9IDQuNSkg
JiAocHogPj0gMS41KSAmIChweiA8PSA2MCkgJiAobnAuYXJjdGFuMihwdCwgcHopIDwgbnAucmFk
aWFucygyMC4wKSkKCgpkZWYgZXh0cmFjdChvbW5pOiBzdHIsIG91dDogUGF0aCwgZXhwZWN0ZWRf
cGFzczogaW50ID0gRVhQRUNURURfUEFTUywgb21uaV9zaGE6IHN0ciA9IE9NTklfU0hBKSAtPiBk
aWN0OgogICAgaW1wb3J0IHVwcm9vdAogICAgcmVjID0geyJzY2hlbWEiOiAicTAtZXh0cmFjdC8x
IiwgImhvc3QiOiBvcy51bmFtZSgpLm5vZGVuYW1lLCAic3RhcnRfdXRjIjogdGltZS5zdHJmdGlt
ZSgiJUZUJVRaIiwgdGltZS5nbXRpbWUoKSksCiAgICAgICAgICAgImNvZGVfc2hhMjU2IjogaGFz
aGxpYi5zaGEyNTYoUGF0aChfX2ZpbGVfXykucmVhZF9ieXRlcygpKS5oZXhkaWdlc3QoKSwgIm9t
bmkiOiBvbW5pLCAidHJlZSI6IFRSRUUsCiAgICAgICAgICAgInB5dGhvbiI6IHN5cy52ZXJzaW9u
LnNwbGl0KClbMF0sICJudW1weSI6IG5wLl9fdmVyc2lvbl9fLCAidXByb290IjogdXByb290Ll9f
dmVyc2lvbl9ffQogICAgc3QwID0gb3Muc3RhdChvbW5pKQogICAgcmVjWyJvbW5pX3N0YXRfYmVm
b3JlIl0gPSB7InNpemUiOiBzdDAuc3Rfc2l6ZSwgImF0aW1lX25zIjogc3QwLnN0X2F0aW1lX25z
LCAibXRpbWVfbnMiOiBzdDAuc3RfbXRpbWVfbnN9CiAgICBnb3QgPSBzaGEyNTZfbm9hdGltZShv
bW5pKQogICAgcmVjWyJvbW5pX3NoYTI1NiJdID0gZ290CiAgICBpZiBnb3QgIT0gb21uaV9zaGE6
CiAgICAgICAgcmFpc2UgU3RvcCgzLCBmIm9tbmlmaWxlIHNoYTI1NiB7Z290fSBpcyBub3QgdGhl
IHBpbiB7b21uaV9zaGF9IikKICAgIHdpdGggb3MuZmRvcGVuKG9zLm9wZW4ob21uaSwgZmxhZ3Mo
KSksICJyYiIpIGFzIGZoOgogICAgICAgIGYgPSB1cHJvb3Qub3BlbihmaCwgb2JqZWN0X2NhY2hl
PU5vbmUsIGFycmF5X2NhY2hlPU5vbmUpCiAgICAgICAgdCA9IGZbVFJFRV0KICAgICAgICBoYXZl
ID0gc2V0KHQua2V5cygpKQogICAgICAgIG1pc3NpbmcgPSBbYiBmb3IgYiBpbiBCUkFOQ0hFUyBp
ZiBiIG5vdCBpbiBoYXZlXQogICAgICAgIGlmIG1pc3Npbmc6CiAgICAgICAgICAgIHJhaXNlIFN0
b3AoMywgZiJicmFuY2hlcyBtaXNzaW5nIGZyb20ge1RSRUV9OiB7bWlzc2luZ30iKQogICAgICAg
IGEgPSB0LmFycmF5cyhCUkFOQ0hFUywgbGlicmFyeT0ibnAiKQogICAgc3QxID0gb3Muc3RhdChv
bW5pKQogICAgcmVjWyJvbW5pX3N0YXRfYWZ0ZXIiXSA9IHsic2l6ZSI6IHN0MS5zdF9zaXplLCAi
YXRpbWVfbnMiOiBzdDEuc3RfYXRpbWVfbnMsICJtdGltZV9ucyI6IHN0MS5zdF9tdGltZV9uc30K
ICAgIGlmIHN0MS5zdF9hdGltZV9ucyAhPSBzdDAuc3RfYXRpbWVfbnM6CiAgICAgICAgcmFpc2Ug
U3RvcCg0LCAidGhlIG9tbmlmaWxlJ3MgYXRpbWUgY2hhbmdlZCIpCiAgICByZWNbIm5fZW50cmll
cyJdID0gaW50KGFbInNpbV9wYXNzIl0uc2l6ZSkKICAgIHNlbCA9IG5wLmFzYXJyYXkoYVsic2lt
X3Bhc3MiXSkgIT0gMAogICAgcmVjWyJuX3Bhc3MiXSA9IGludChzZWwuc3VtKCkpCiAgICBpZiBy
ZWNbIm5fcGFzcyJdICE9IGV4cGVjdGVkX3Bhc3M6CiAgICAgICAgcmFpc2UgU3RvcCgzLCBmInBh
c3Npbmcgcm93cyB7cmVjWyduX3Bhc3MnXX0gIT0ge2V4cGVjdGVkX3Bhc3N9IikKICAgIGNvbCA9
IHtrOiBucC5hc2FycmF5KGFba10sIG5wLmZsb2F0NjQpW3NlbF0gZm9yIGsgaW4gQlJBTkNIRVMg
aWYgayAhPSAic2ltX3Bhc3MifQogICAgZGVsIGEKICAgIHB0LCBweiwgcTMsIFcgPSAoY29sW2td
ICogMTAwMC4wIGZvciBrIGluICgic2ltIiwgInNpbV9weiIsICJzaW1fcTMiLCAic2ltX1ciKSkg
ICAjIE1lVgogICAgcTAsIHN0YXR1cyA9IHJlY292ZXJfcTAocHQsIHB6LCBxMykKICAgIFdxMCwg
dzJuZWcgPSB3X2Zyb21fcTAocTAsIHEzKQogICAgY3RsID0gKHN0YXR1cyA9PSAwKSAmIH53Mm5l
ZyAmIG5wLmlzZmluaXRlKFcpCiAgICByZXNpZCA9IG5wLmFicyhXW2N0bF0gLSBXcTBbY3RsXSkg
LyAxMDAwLjAgICAgICAgICAgICAgICAgICAgICAjIEdlVgogICAgcmVjWyJyZWNvdmVyeV9jb250
cm9sIl0gPSB7InJvd3MiOiBpbnQoY3RsLnN1bSgpKSwgIm1heF9hYnNfcmVzaWRfR2VWIjogZmxv
YXQocmVzaWQubWF4KCkpIGlmIHJlc2lkLnNpemUgZWxzZSBOb25lLAogICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgInRvbF9HZVYiOiBSRUNPVkVSWV9UT0xfR0VWLCAibl9XMl9uZWdhdGl2
ZSI6IGludCh3Mm5lZy5zdW0oKSl9CiAgICBpZiBub3QgcmVzaWQuc2l6ZSBvciBmbG9hdChyZXNp
ZC5tYXgoKSkgPiBSRUNPVkVSWV9UT0xfR0VWOgogICAgICAgIHJhaXNlIFN0b3AoNSwgZiJyZWNv
dmVyeSBjb250cm9sIGZhaWxlZDoge3JlY1sncmVjb3ZlcnlfY29udHJvbCddfSIpCiAgICByZWNb
InEwX3N0YXR1c19jb3VudHMiXSA9IHtzdHIoayk6IGludCgoc3RhdHVzID09IGspLnN1bSgpKSBm
b3IgayBpbiAoMCwgMSwgMil9CiAgICByZWNbIm5fcTBfbGVfMCJdID0gaW50KChxMCA8PSAwKS5z
dW0oKSkKICAgIGNvbHMgPSB7InB0IjogY29sWyJzaW0iXSwgInB6IjogY29sWyJzaW1fcHoiXSwg
ImVhdmFpbCI6IGNvbFsic2ltX2VhdmFpbCJdLCAicTMiOiBjb2xbInNpbV9xMyJdLCAiVyI6IGNv
bFsic2ltX1ciXSwKICAgICAgICAgICAgInEwIjogcTAgLyAxMDAwLjAsICJ3X3JlY28iOiBjb2xb
IndfcmVjbyJdLCAicTNfdHJ1ZSI6IGNvbFsiTUNfcTMiXSwgIldfdHJ1ZSI6IGNvbFsiTUNfVyJd
fQogICAgYXJyYXlzID0ge2s6IG5wLmFzYXJyYXkodiwgbnAuZmxvYXQzMikgZm9yIGssIHYgaW4g
Y29scy5pdGVtcygpfQogICAgYXJyYXlzWyJxMF9zdGF0dXMiXSA9IHN0YXR1cwogICAgYXJyYXlz
WyJpbl90cnV0aF9wcyJdID0gaW5fdHJ1dGhfcHMoY29sWyJNQyJdLCBjb2xbIk1DX3B6Il0pLmFz
dHlwZShucC5pbnQ4KQogICAgbnB6ID0gb3V0IC8gInEwX2V4dHJhY3QubnB6IgogICAgbnAuc2F2
ZXoobnB6LCAqKmFycmF5cykKICAgIHJlY1sibnB6X3NoYTI1NiJdID0gaGFzaGxpYi5zaGEyNTYo
bnB6LnJlYWRfYnl0ZXMoKSkuaGV4ZGlnZXN0KCkKICAgIHJlY1sibnB6X2J5dGVzIl0gPSBucHou
c3RhdCgpLnN0X3NpemUKICAgIHJlY1siY29sdW1ucyJdID0ge2s6IHN0cih2LmR0eXBlKSBmb3Ig
aywgdiBpbiBhcnJheXMuaXRlbXMoKX0KICAgIHJlY1sicGVha19yc3NfYnl0ZXMiXSA9IGludChy
ZXNvdXJjZS5nZXRydXNhZ2UocmVzb3VyY2UuUlVTQUdFX1NFTEYpLnJ1X21heHJzcyAqICgxMDI0
IGlmIHN5cy5wbGF0Zm9ybSAhPSAiZGFyd2luIiBlbHNlIDEpKQogICAgcmVjWyJlbmRfdXRjIl0g
PSB0aW1lLnN0cmZ0aW1lKCIlRlQlVFoiLCB0aW1lLmdtdGltZSgpKQogICAgcmV0dXJuIHJlYwoK
CmRlZiBtYWluKGFyZ3Y9Tm9uZSkgLT4gaW50OgogICAgYXAgPSBhcmdwYXJzZS5Bcmd1bWVudFBh
cnNlcihkZXNjcmlwdGlvbj1fX2RvY19fLnNwbGl0KCJcbiIsIDEpWzBdKQogICAgYXAuYWRkX2Fy
Z3VtZW50KCItLW9tbmkiLCByZXF1aXJlZD1UcnVlKQogICAgYXAuYWRkX2FyZ3VtZW50KCItLW91
dCIsIHR5cGU9UGF0aCwgcmVxdWlyZWQ9VHJ1ZSkKICAgIGFyZ3MgPSBhcC5wYXJzZV9hcmdzKGFy
Z3YpCiAgICBpZiBub3QgYXJncy5vdXQuaXNfZGlyKCkgb3IgYW55KGFyZ3Mub3V0Lml0ZXJkaXIo
KSk6CiAgICAgICAgcHJpbnQoZiJSRUZVU0VEOiB7YXJncy5vdXR9IGlzIG5vdCBhbiBleGlzdGlu
ZyBlbXB0eSBkaXJlY3RvcnkiLCBmaWxlPXN5cy5zdGRlcnIpCiAgICAgICAgcmV0dXJuIDkKICAg
IHRyeToKICAgICAgICByZWMgPSBleHRyYWN0KGFyZ3Mub21uaSwgYXJncy5vdXQpCiAgICBleGNl
cHQgU3RvcCBhcyBlOgogICAgICAgIHByaW50KGYiU1RPUCByYyB7ZS5yY306IHtlfSIsIGZpbGU9
c3lzLnN0ZGVycikKICAgICAgICBmb3IgcCBpbiAoYXJncy5vdXQgLyAicTBfZXh0cmFjdC5ucHoi
LCk6CiAgICAgICAgICAgIGlmIHAuZXhpc3RzKCk6CiAgICAgICAgICAgICAgICBwLnVubGluaygp
CiAgICAgICAgcmV0dXJuIGUucmMKICAgIChhcmdzLm91dCAvICJxMF9leHRyYWN0Lmpzb24iKS53
cml0ZV90ZXh0KGpzb24uZHVtcHMocmVjLCBpbmRlbnQ9MSkgKyAiXG4iKQogICAgcHJpbnQoanNv
bi5kdW1wcyh7azogcmVjW2tdIGZvciBrIGluICgibl9wYXNzIiwgInEwX3N0YXR1c19jb3VudHMi
LCAicmVjb3ZlcnlfY29udHJvbCIsICJucHpfc2hhMjU2IiwgIm5wel9ieXRlcyIpfSkpCiAgICBy
ZXR1cm4gMAoKCmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CiAgICBzeXMuZXhpdChtYWluKCkp
Cg==
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
