#!/bin/bash
# HPSS archive of the small and medium at-risk inputs (Joseph's decision, relayed by the director 2026-11-11: zero_loops,
# cpl, s1_cmodel_cresp_tables, f0b, rpd_dumps, central and cstat, tier3_inputs, shared_inputs and prr; 1A is left to
# Joseph and Ben). One Perlmutter login node, 0 node-h, nothing written to CFS, nothing deleted on pscratch or HPSS.
#
# The list: the 8,846 FOUND rows of those ten groups in AT-RISK's stat output (fd/retention-20261110/receipts/session.txt,
# sha256 92fd8887...), embedded after the __LIST__ line as group<TAB>size<TAB>mtime<TAB>path, its sha256 checked below.
# No directory is listed anywhere: every source is an explicit path from that list.
#
# Access times. htar opens its input files itself and has no O_NOATIME option, so archiving the pscratch paths
# directly would set every source's atime to the archive time: a refresh of the purge clock, which the director's
# ruling forbids. So htar never reads pscratch. Per group, each source is copied by os.open(O_RDONLY | O_NOATIME)
# (EPERM is raised, never retried plainly) into /dev/shm, hashing the bytes read; its size and mtime must equal the
# AT-RISK stat, and size, mtime and atime must be unchanged by the copy, or STOP. htar then archives the /dev/shm copy
# (with the source's mode and mtime restored on it), and the copy is removed. Sources' atimes do not move.
#
# Per group, in exposure order, each step a STOP on failure (exit 8; nothing repaired, nothing deleted; archives
# already made stay on HPSS and are reported):
#   1 stage by O_NOATIME copy (above); manifest SHA256SUMS.<group> = the sha256 of the bytes read, as "digest  /path";
#   2 htar -Hcrc -Hverify=1 -cvf $H/<group>.tar -L members, run inside the stage directory, so member names are the
#     sources' paths without the leading "/" (restore with cd / && htar -xf); the manifest is the first member;
#   3 hsi hashcreate, then hsi hashverify, of $H/<group>.tar (its log must show "<tar>: (<hash>) OK");
#   4 retrieval: htar -xf of the manifest and of the group's smallest file into /dev/shm; the manifest must cmp equal
#     and the file's sha256 must equal its manifest line; then removed.
# Before any group: the HPSS target $H must not exist; hpssquota's HPSS free space must be at least 1.2 x the archive
# size estimate, taking free = min(hpssquota's quota - used, Joseph's figure of 2026-11-11, "HPSS usage is 449.3 GB of
# 512 GB", read as 62.7e9 bytes, the smaller reading), or STOP (exit 7). After: hsi ls -l of $H and hpssquota again.
# Writes only under $OUT (pscratch), /dev/shm/josephrb-hpss-atrisk and $H (HPSS); refuses if $OUT or the /dev/shm
# directory exists. Threads 1, nice 19. Launched from a /dev/shm copy of itself, whose path is $1; deletes it at exit.
SELF=$1
OUT=/pscratch/sd/j/josephrb/hpss-atrisk-20261111
H=/home/j/josephrb/mnv-at-risk-20261111
W=/dev/shm/josephrb-hpss-atrisk
LIST_SHA=@LIST_SHA@
GROUPS_IN_ORDER="s1_cmodel_cresp_tables zero_loops cpl f0b rpd_dumps tier3_inputs cstat central shared_inputs prr"
JOSEPH_FREE_BYTES=62700000000
PY=/usr/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }
[ ! -e "$OUT" ] || bail
[ ! -e "$W" ] || bail
q=$(squeue --me -h -o '%i|%j|%T') || bail
printf '%s\n' "$q" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ {f=1} END {exit !f}' && bail
mkdir -p "$OUT/logs" "$OUT/manifests" "$W" || bail
exec > "$OUT/logs/archive.log" 2>&1
finish() {
  cd / ; rm -rf -- "$W"; echo "removal of $W rc=$? ; present after: $([ -e "$W" ] && echo yes || echo no)"
  echo "hpss archive rc=$1 $(date -u +%FT%TZ)"; echo "$1" > "$OUT/logs/archive.done"
  (cd "$OUT" && tar czf post.tar.gz logs manifests archive_list.tsv 2>/dev/null; sha256sum post.tar.gz)
  rm -f -- "$SELF"; exit "$1"
}
stop() { echo "STOP: $*"; finish 8; }
stamp() { date -u +%FT%TZ; }
echo "node $(hostname) loadavg $(cut -d' ' -f1-3 /proc/loadavg) start=$(stamp)"
echo "script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"; cp "$SELF" "$OUT/logs/hpss_atrisk.sh"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
cd "$W" || finish 9

# 0. the embedded list
sed -n '/^__LIST__$/,$p' "$SELF" | tail -n +2 > "$OUT/archive_list.tsv"
h=$(sha256sum "$OUT/archive_list.tsv" | cut -d' ' -f1)
echo "list sha256 $h rows $(wc -l < "$OUT/archive_list.tsv")"
[ "$h" = "$LIST_SHA" ] || stop "embedded list sha256 is not $LIST_SHA"

# 1. the HPSS target must not exist (rc 124 = hsi did not answer in time: STOP)
timeout 300 hsi -q "ls -d $H" > "$OUT/logs/target-check.txt" 2>&1; r=$?
echo "target check hsi rc=$r"
[ $r = 124 ] && stop "hsi did not answer within 300 s"
[ $r = 0 ] && stop "$H exists"

# 2. quota preflight
timeout 300 hpssquota > "$OUT/logs/quota-before.txt" 2>&1; r=$?
echo "hpssquota before rc=$r"; grep -i 'HPSS' "$OUT/logs/quota-before.txt"
[ $r = 0 ] || stop "hpssquota rc=$r"
nice -n 19 "$PY" -I - "$OUT/logs/quota-before.txt" "$OUT/archive_list.tsv" "$JOSEPH_FREE_BYTES" <<'PY'
import math, re, sys
q, lst, joseph = sys.argv[1], sys.argv[2], int(sys.argv[3])
U = {"B": 1, "KiB": 2**10, "MiB": 2**20, "GiB": 2**30, "TiB": 2**40, "PiB": 2**50}
line = [l for l in open(q) if "usage on HPSS" in l]
if len(line) != 1:
    print("PREFLIGHT STOP: no single HPSS usage line"); sys.exit(7)
f = [x.strip() for x in line[0].split("|")]
vals = []
for x in f[2:4]:
    m = re.fullmatch(r"([0-9.]+)\s*(B|KiB|MiB|GiB|TiB|PiB)", x)
    if not m:
        print("PREFLIGHT STOP: cannot parse", repr(x)); sys.exit(7)
    vals.append(float(m.group(1)) * U[m.group(2)])
used, quota = vals
live_free = quota - used
files = [l.rstrip("\n").split("\t") for l in open(lst)]
groups = sorted({r[0] for r in files})
# tar: a 512-byte header and 512-byte padding per member; the manifest (about 70 + len(path) bytes a line) per group;
# end blocks and htar's index, bounded by 1 KiB per member plus 16 MiB.
est = sum(512 + 512 * math.ceil(int(r[1]) / 512) for r in files)
est += sum(512 + 512 * math.ceil(sum(70 + len(r[3]) for r in files if r[0] == g) / 512) for g in groups)
est += 1024 * len(files) + 16 * 2**20
free = min(live_free, joseph)
need = 1.2 * est
print(f"preflight: used {used:.0f} quota {quota:.0f} live_free {live_free:.0f} joseph_free {joseph} free {free:.0f}")
print(f"preflight: files {len(files)} source bytes {sum(int(r[1]) for r in files)} archive estimate {est} need (x1.2) {need:.0f}")
if free < need:
    print("PREFLIGHT STOP: free < 1.2 x archive estimate"); sys.exit(7)
print("PREFLIGHT OK")
PY
r=$?; [ $r = 0 ] || { echo "STOP: preflight rc=$r"; finish 7; }

timeout 300 hsi -q "mkdir -p $H" > "$OUT/logs/mkdir.txt" 2>&1; r=$?
echo "hsi mkdir rc=$r"; [ $r = 0 ] || stop "hsi mkdir rc=$r"

for g in $GROUPS_IN_ORDER; do
  echo "== group $g start $(stamp)"
  S="$W/$g"
  # 1 stage
  nice -n 19 "$PY" -I - "$OUT/archive_list.tsv" "$g" "$S" "$OUT/manifests/SHA256SUMS.$g" <<'PY'
import hashlib, os, sys
lst, g, S, man = sys.argv[1:5]
rows = [l.rstrip("\n").split("\t") for l in open(lst)]
rows = [(int(s), int(m), p) for gg, s, m, p in rows if gg == g]
need = 2 * sum(s for s, m, p in rows) + 2 * 2**30
st = os.statvfs("/dev/shm")
if st.f_bavail * st.f_frsize < need:
    print(f"STAGE STOP {g}: /dev/shm free {st.f_bavail * st.f_frsize} < {need}"); sys.exit(8)
os.makedirs(S)
lines, bad = [], []
for size, mtime, p in rows:
    s0 = os.stat(p)
    if s0.st_size != size or int(s0.st_mtime) != mtime:
        bad.append(f"{p}: size/mtime {s0.st_size}/{int(s0.st_mtime)} != AT-RISK {size}/{mtime}"); break
    dst = os.path.join(S, p.lstrip("/"))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    h = hashlib.sha256()
    fi = os.open(p, os.O_RDONLY | os.O_NOATIME)          # EPERM raises here; there is no plain retry
    with open(dst, "wb") as fo:
        while True:
            b = os.read(fi, 1 << 24)
            if not b:
                break
            h.update(b); fo.write(b)
    os.close(fi)
    s1 = os.stat(p)
    if (s0.st_size, s0.st_mtime_ns, s0.st_atime_ns) != (s1.st_size, s1.st_mtime_ns, s1.st_atime_ns):
        bad.append(f"{p}: stat changed by the copy"); break
    if os.path.getsize(dst) != size:
        bad.append(f"{p}: copy size {os.path.getsize(dst)} != {size}"); break
    os.chmod(dst, s0.st_mode & 0o7777)
    os.utime(dst, ns=(s0.st_mtime_ns, s0.st_mtime_ns))
    lines.append(f"{h.hexdigest()}  {p}\n")
if bad:
    print(f"STAGE STOP {g}:", bad[0]); sys.exit(8)
with open(man, "w") as o:
    o.writelines(lines)
with open(os.path.join(S, f"SHA256SUMS.{g}"), "w") as o:
    o.writelines(lines)
with open(os.path.join(S, ".members"), "w") as o:
    o.write(f"SHA256SUMS.{g}\n")
    o.writelines(p.lstrip("/") + "\n" for size, mtime, p in rows)
small = min(rows)[2]
open(os.path.join(S, ".smallest"), "w").write(small.lstrip("/") + "\n")
print(f"STAGE OK {g}: {len(rows)} files, {sum(s for s, m, p in rows)} bytes, smallest {small}")
PY
  r=$?; [ $r = 0 ] || stop "stage $g rc=$r"
  echo "manifest $g sha256 $(sha256sum "$OUT/manifests/SHA256SUMS.$g" | cut -d' ' -f1) lines $(wc -l < "$OUT/manifests/SHA256SUMS.$g")"
  # 2 htar, from the stage directory
  cd "$S" || stop "cd $S"
  T="$H/$g.tar"
  timeout 3600 htar -Hcrc -Hverify=1 -cvf "$T" -L .members > "$OUT/logs/htar-$g.log" 2>&1; r=$?
  echo "htar $g rc=$r"; tail -2 "$OUT/logs/htar-$g.log"
  [ $r = 0 ] || stop "htar $g rc=$r"
  # 3 hashcreate, hashverify
  timeout 3600 hsi -q "hashcreate $T" > "$OUT/logs/hashcreate-$g.log" 2>&1; r=$?
  echo "hashcreate $g rc=$r"; [ $r = 0 ] || stop "hashcreate $g rc=$r"
  timeout 3600 hsi -q "hashverify $T" > "$OUT/logs/hashverify-$g.log" 2>&1; r=$?
  echo "hashverify $g rc=$r: $(cat "$OUT/logs/hashverify-$g.log" | tr '\n' ' ')"
  [ $r = 0 ] || stop "hashverify $g rc=$r"
  grep -Eq "^$T: \([a-z0-9]+\) OK\$" "$OUT/logs/hashverify-$g.log" || stop "hashverify $g: no OK line for $T"
  # 4 retrieval into /dev/shm
  small=$(cat "$S/.smallest")
  X="$W/retrieve-$g"; mkdir -p "$X" && cd "$X" || stop "cd $X"
  timeout 1800 htar -xf "$T" "SHA256SUMS.$g" "$small" > "$OUT/logs/retrieve-$g.log" 2>&1; r=$?
  echo "retrieve $g rc=$r"; [ $r = 0 ] || stop "retrieve $g rc=$r"
  cmp "$X/SHA256SUMS.$g" "$OUT/manifests/SHA256SUMS.$g" || stop "retrieved manifest $g differs"
  a=$(sha256sum "$X/$small" | cut -d' ' -f1); b=$(grep -F "  /$small" "$OUT/manifests/SHA256SUMS.$g" | cut -d' ' -f1)
  echo "retrieved /$small $a manifest $b"
  [ -n "$a" ] && [ "$a" = "$b" ] || stop "retrieved file $g differs from its manifest"
  cd "$W" && rm -rf -- "$S" "$X" || stop "removal of the $g stage"
  echo "== group $g PASS $(stamp)"
done

timeout 300 hsi -q "ls -l $H" > "$OUT/logs/hsi-ls-after.txt" 2>&1; echo "hsi ls rc=$?"; cat "$OUT/logs/hsi-ls-after.txt"
timeout 300 hpssquota > "$OUT/logs/quota-after.txt" 2>&1; echo "hpssquota after rc=$?"; grep -i 'HPSS' "$OUT/logs/quota-after.txt"
echo "ARCHIVE PASS: all ten groups archived, hash-verified and retrieval-checked"
finish 0
exit 9
