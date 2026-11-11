#!/bin/bash
# HPSS archive of RSN's three unarchived inputs (the director's ruling on RSN rev 2, 2026-11-11): pv-ladder's prep/
# (36 files) and products/ (30 files), and cpl_block.npz. One NERSC data-transfer node, never a Slurm job, 0 node-h,
# nothing written to CFS, nothing deleted on pscratch or HPSS, nothing overwritten. hpss-20261111's discipline (#1054,
# fd/retention-20261110/hpss-20261111/connect/hpss_atrisk.template.sh), with five changes, each marked [RSN]:
#   [RSN-1] it refuses unless the host is a data-transfer node (dtnNN) and no Slurm job is set;
#   [RSN-2] the list carries each file's committed sha256 pin (group<TAB>sha256<TAB>path: pv-ladder's prep-SHA256SUMS,
#           its receipts/SHA256SUMS products rows, and F0b's --extra-block-sha256), and the bytes read must equal it;
#           each file's size and mtime are recorded in stat.<group>.tsv beside the manifest;
#   [RSN-3] retrieval re-reads EVERY member from HPSS (htar -xf of the whole tar into /dev/shm), and each retrieved
#           file's sha256 must equal its manifest line and its pin, with the member count equal to the list's;
#   [RSN-4] no squeue fence: a data-transfer node is not a Slurm client, and these sources are read by O_NOATIME,
#           never written; the director's go is the fence;
#   [RSN-5] /dev/shm headroom is 2 x the group's bytes plus 256 MiB (the group is at most about 22 MB).
# The list is embedded after the __LIST__ line, its sha256 checked below. No directory is listed: every source is an
# explicit path from that list.
#
# Access times. htar opens its input files itself and has no O_NOATIME option, so htar never reads pscratch. Per group,
# each source is copied by os.open(O_RDONLY | O_NOATIME) (EPERM raises, never retried plainly) into /dev/shm, hashing
# the bytes read; the hash must equal the file's pin, the copy's size must equal the bytes read, and size, mtime and
# atime must be unchanged by the copy, or STOP. htar then archives the /dev/shm copy (the source's mode and mtime
# restored on it), and the copy is removed. Sources' atimes do not move.
#
# Per group, each step a STOP on failure (exit 8; nothing repaired, nothing deleted; archives already made stay on HPSS
# and are reported):
#   1 stage by O_NOATIME copy (above); manifest SHA256SUMS.<group> = the sha256 of the bytes read, as "digest  /path";
#   2 htar -Hcrc -Hverify=1 -cvf $H/<group>.tar -L members, run inside the stage directory, so member names are the
#     sources' paths without the leading "/" (restore with cd / && htar -xf); the manifest is the first member;
#   3 hsi hashcreate, then hsi hashverify, of $H/<group>.tar (its log must show "<tar>: (<hash>) OK");
#   4 retrieval of every member into /dev/shm [RSN-3]; then removed.
# Before any group: the HPSS target $H must not exist (nothing is overwritten); hpssquota's free space must be at least
# 1.2 x the archive estimate, taking free = min(hpssquota's quota - used, Joseph's figure of 2026-11-11, 62.7e9 bytes),
# or STOP (exit 7). After: hsi ls -l of $H and hpssquota again. Writes only under $OUT (pscratch), /dev/shm/$W and $H
# (HPSS); refuses if $OUT or $W exists. Threads 1, nice 19. Launched from a /dev/shm copy of itself, whose path is $1;
# deletes it at exit.
SELF=$1
OUT=/pscratch/sd/j/josephrb/hpss-rsn-20261111
H=/home/j/josephrb/mnv-rsn-inputs-20261111
W=/dev/shm/josephrb-hpss-rsn
LIST_SHA=@LIST_SHA@
GROUPS_IN_ORDER="pvl_prep pvl_products cpl_block"
N_ROWS=67
JOSEPH_FREE_BYTES=62700000000
PY=/usr/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }
case "$(hostname -s)" in dtn[0-9][0-9]) ;; *) bail ;; esac        # [RSN-1]
[ -z "$SLURM_JOB_ID" ] || bail                                      # [RSN-1]
[ -x "$PY" ] || bail
[ -d /pscratch/sd/j/josephrb ] || bail
[ ! -e "$OUT" ] || bail
[ ! -e "$W" ] || bail
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
echo "node $(hostname) loadavg $(cut -d' ' -f1-3 /proc/loadavg) start=$(stamp) slurm_job='${SLURM_JOB_ID}'"
echo "script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"; cp "$SELF" "$OUT/logs/hpss_rsn.sh"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
cd "$W" || finish 9

# 0. the embedded list
sed -n '/^__LIST__$/,$p' "$SELF" | tail -n +2 > "$OUT/archive_list.tsv"
h=$(sha256sum "$OUT/archive_list.tsv" | cut -d' ' -f1)
n=$(wc -l < "$OUT/archive_list.tsv")
echo "list sha256 $h rows $n"
[ "$h" = "$LIST_SHA" ] || stop "embedded list sha256 is not $LIST_SHA"
[ "$n" -eq "$N_ROWS" ] || stop "the list has $n rows, not $N_ROWS"

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
import math, os, re, sys
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
rows = [l.rstrip("\n").split("\t") for l in open(lst)]
sizes = []
for g, sha, p in rows:
    try:
        sizes.append(os.stat(p).st_size)
    except OSError as e:
        print(f"PREFLIGHT STOP: {p}: {e}"); sys.exit(7)
groups = sorted({r[0] for r in rows})
est = sum(512 + 512 * math.ceil(s / 512) for s in sizes)
est += sum(512 + 512 * math.ceil(sum(70 + len(r[2]) for r in rows if r[0] == g) / 512) for g in groups)
est += 1024 * len(rows) + 16 * 2**20
free = min(quota - used, joseph)
print(f"preflight: used {used:.0f} quota {quota:.0f} free {free:.0f} files {len(rows)} source bytes {sum(sizes)} "
      f"archive estimate {est} need (x1.2) {1.2 * est:.0f}")
if free < 1.2 * est:
    print("PREFLIGHT STOP: free < 1.2 x archive estimate"); sys.exit(7)
print("PREFLIGHT OK")
PY
r=$?; [ $r = 0 ] || { echo "STOP: preflight rc=$r"; finish 7; }

timeout 300 hsi -q "mkdir -p $H" > "$OUT/logs/mkdir.txt" 2>&1; r=$?
echo "hsi mkdir rc=$r"; [ $r = 0 ] || stop "hsi mkdir rc=$r"

for g in $GROUPS_IN_ORDER; do
  echo "== group $g start $(stamp)"
  S="$W/$g"
  # 1 stage [RSN-2, RSN-5]
  nice -n 19 "$PY" -I - "$OUT/archive_list.tsv" "$g" "$S" "$OUT/manifests/SHA256SUMS.$g" "$OUT/manifests/stat.$g.tsv" <<'PY'
import hashlib, os, sys
lst, g, S, man, stat_out = sys.argv[1:6]
rows = [l.rstrip("\n").split("\t") for l in open(lst)]
rows = [(sha, p) for gg, sha, p in rows if gg == g]
if not rows:
    print(f"STAGE STOP {g}: no rows"); sys.exit(8)
total = sum(os.stat(p).st_size for sha, p in rows)
st = os.statvfs("/dev/shm")
if st.f_bavail * st.f_frsize < 2 * total + 256 * 2**20:
    print(f"STAGE STOP {g}: /dev/shm free {st.f_bavail * st.f_frsize} < {2 * total + 256 * 2**20}"); sys.exit(8)
os.makedirs(S)
lines, stats = [], []
for pin, p in rows:
    s0 = os.stat(p)
    dst = os.path.join(S, p.lstrip("/"))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    h, n = hashlib.sha256(), 0
    fi = os.open(p, os.O_RDONLY | os.O_NOATIME)          # EPERM raises here; there is no plain retry
    with open(dst, "wb") as fo:
        while True:
            b = os.read(fi, 1 << 24)
            if not b:
                break
            h.update(b); fo.write(b); n += len(b)
    os.close(fi)
    s1 = os.stat(p)
    if (s0.st_size, s0.st_mtime_ns, s0.st_atime_ns) != (s1.st_size, s1.st_mtime_ns, s1.st_atime_ns):
        print(f"STAGE STOP {g}: {p}: size, mtime or atime changed by the copy"); sys.exit(8)
    if n != s0.st_size or os.path.getsize(dst) != s0.st_size:
        print(f"STAGE STOP {g}: {p}: {n} bytes read, copy {os.path.getsize(dst)}, size {s0.st_size}"); sys.exit(8)
    if h.hexdigest() != pin:
        print(f"STAGE STOP {g}: {p}: sha256 {h.hexdigest()} is not its committed pin {pin}"); sys.exit(8)
    os.chmod(dst, s0.st_mode & 0o7777)
    os.utime(dst, ns=(s0.st_mtime_ns, s0.st_mtime_ns))
    lines.append(f"{pin}  {p}\n")
    stats.append(f"{s0.st_size}\t{s0.st_mtime_ns}\t{p}\n")
for path in (man, os.path.join(S, f"SHA256SUMS.{g}")):
    with open(path, "w") as o:
        o.writelines(lines)
with open(stat_out, "w") as o:
    o.writelines(stats)
with open(os.path.join(S, ".members"), "w") as o:
    o.write(f"SHA256SUMS.{g}\n")
    o.writelines(p.lstrip("/") + "\n" for sha, p in rows)
print(f"STAGE OK {g}: {len(rows)} files, {total} bytes, every sha256 equal to its pin")
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
  echo "hashverify $g rc=$r: $(tr '\n' ' ' < "$OUT/logs/hashverify-$g.log")"
  [ $r = 0 ] || stop "hashverify $g rc=$r"
  grep -Eq "^$T: \([a-z0-9]+\) OK\$" "$OUT/logs/hashverify-$g.log" || stop "hashverify $g: no OK line for $T"
  # 4 retrieval of every member into /dev/shm [RSN-3]
  X="$W/retrieve-$g"; mkdir -p "$X" && cd "$X" || stop "cd $X"
  timeout 3600 htar -xf "$T" > "$OUT/logs/retrieve-$g.log" 2>&1; r=$?
  echo "retrieve $g rc=$r"; [ $r = 0 ] || stop "retrieve $g rc=$r"
  cmp "$X/SHA256SUMS.$g" "$OUT/manifests/SHA256SUMS.$g" || stop "retrieved manifest $g differs"
  nice -n 19 "$PY" -I - "$X" "$OUT/manifests/SHA256SUMS.$g" "$OUT/archive_list.tsv" "$g" <<'PY' || stop "retrieved $g differs"
import hashlib, os, sys
X, man, lst, g = sys.argv[1:5]
want = {p: s for s, p in (l.rstrip("\n").split("  ", 1) for l in open(man))}
pins = {p: s for gg, s, p in (l.rstrip("\n").split("\t") for l in open(lst)) if gg == g}
if want != pins:
    print(f"RETRIEVE STOP {g}: the manifest is not the list's pins"); sys.exit(8)
got = {}
for root, _, files in os.walk(X):
    for f in files:
        full = os.path.join(root, f)
        rel = "/" + os.path.relpath(full, X)
        if rel == f"/SHA256SUMS.{g}":
            continue
        h = hashlib.sha256()
        with open(full, "rb") as fi:
            for b in iter(lambda: fi.read(1 << 24), b""):
                h.update(b)
        got[rel] = h.hexdigest()
if got != want:
    missing, extra = sorted(set(want) - set(got)), sorted(set(got) - set(want))
    bad = sorted(p for p in set(got) & set(want) if got[p] != want[p])
    print(f"RETRIEVE STOP {g}: {len(missing)} missing, {len(extra)} extra, {len(bad)} differing"); sys.exit(8)
print(f"RETRIEVE OK {g}: {len(got)} members re-read from HPSS, every sha256 equal to its manifest line and pin")
PY
  cd "$W" && rm -rf -- "$S" "$X" || stop "removal of the $g stage"
  echo "== group $g PASS $(stamp)"
done

timeout 300 hsi -q "ls -l $H" > "$OUT/logs/hsi-ls-after.txt" 2>&1; echo "hsi ls rc=$?"; cat "$OUT/logs/hsi-ls-after.txt"
timeout 300 hpssquota > "$OUT/logs/quota-after.txt" 2>&1; echo "hpssquota after rc=$?"; grep -i 'HPSS' "$OUT/logs/quota-after.txt"
echo "ARCHIVE PASS: all three groups archived, hash-verified and every member re-read from HPSS"
finish 0
exit 9
