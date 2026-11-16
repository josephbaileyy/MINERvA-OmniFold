#!/bin/bash
# HPSS archive of RSN's three unarchived inputs (the director's ruling on RSN rev 2, 2026-11-11): pv-ladder's prep/
# (36 files) and products/ (30 files), and cpl_block.npz. One Perlmutter login node, as #1054 ran, never a Slurm job,
# 0 node-h, nothing written to CFS, nothing deleted on pscratch or HPSS, nothing overwritten. hpss-20261111's discipline
# (#1054, fd/retention-20261110/hpss-20261111/connect/hpss_atrisk.template.sh), with six changes, each marked [RSN]
# (kit rev 2, the director's ruling of 2026-11-12 after rev 1's DTN probe found no hsi, htar or hpssquota on dtn01):
#   [RSN-1] it refuses unless the host is a login node (loginNN) and no Slurm job is set;
#   [RSN-2] the list carries each file's committed sha256 pin (group<TAB>sha256<TAB>path: pv-ladder's prep-SHA256SUMS,
#           its receipts/SHA256SUMS products rows, and cpl_block.npz's output digest in CT-5B addition's
#           fd/receipts-ct/5b/addition/run/chain.json:626), and the bytes read must equal it;
#           each file's size and mtime are recorded in stat.<group>.tsv beside the manifest;
#   [RSN-3] retrieval re-reads EVERY member from HPSS (htar -xf of the whole tar into /dev/shm), and each retrieved
#           file's sha256 must equal its manifest line and its pin, with the member count equal to the list's;
#   [RSN-4] no squeue fence in the script: these sources are read by O_NOATIME, never written, and cov2d has reported
#           no overlap with any gate it fences; the director's go, and the queue check the launcher's probe prints
#           before it, are the fence;
#   [RSN-5] /dev/shm headroom is 2 x the group's bytes plus 256 MiB (the group is at most about 22 MB);
#   [RSN-6] every setup check runs before $OUT exists, so a setup failure cannot spend the one run: hsi, htar,
#           hpssquota, timeout and sha256sum must be on PATH; hsi must list /home/j/josephrb (rc 0); and the target
#           check must return hsi's own not-found, rc 64 with HPSS_ENOENT in its output (rc 0 = the target exists;
#           any other rc, 127 and 124 included, refuses); hpssquota must return rc 0 with one "usage on HPSS" line,
#           which the quota preflight then reads. A refusal prints its reason and exits 9, writing nothing.
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
# Before any group: the HPSS target $H must not exist [RSN-6] (nothing is overwritten); hpssquota's free space must
# be at least 1.2 x the archive estimate, taking free = min(hpssquota's quota - used, Joseph's figure of 2026-11-11, 62.7e9 bytes),
# or STOP (exit 7). After: hsi ls -l of $H and hpssquota again. Writes only under $OUT (pscratch), /dev/shm/$W and $H
# (HPSS); refuses if $OUT or $W exists. Threads 1, nice 19. Launched from a /dev/shm copy of itself, whose path is $1;
# deletes it at exit.
SELF=$1
OUT=/pscratch/sd/j/josephrb/hpss-ll5d-u-20261116
H=/home/j/josephrb/mnv-ll5d-unfolds-r2-20261116
W=/dev/shm/josephrb-hpss-ll5d-u
LIST_SHA=980bb95e20eac386a220bb7d0dbb16a5a3477248688f9a72bc07671a7ad5842d
GROUPS_IN_ORDER="null_roles toys extras sidecars"
N_ROWS=1759
JOSEPH_FREE_BYTES=62700000000
PY=/usr/bin/python3
bail() { echo "REFUSED (nothing written): $*"; rm -f -- "$SELF"; exit 9; }
case "$(hostname -s)" in login[0-9][0-9]) ;; *) bail "host $(hostname -s) is not a login node" ;; esac   # [RSN-1]
[ -z "$SLURM_JOB_ID" ] || bail "a Slurm job is set ($SLURM_JOB_ID)"                                      # [RSN-1]
[ -x "$PY" ] || bail "no $PY"
[ -d /pscratch/sd/j/josephrb ] || bail "no /pscratch/sd/j/josephrb"
[ ! -e "$OUT" ] || bail "$OUT exists"
[ ! -e "$W" ] || bail "$W exists"
for t in hsi htar hpssquota timeout sha256sum; do                                                         # [RSN-6]
  command -v "$t" > /dev/null || bail "$t is not on PATH"
done
PRE_HOME=$(timeout 300 hsi -q "ls -d /home/j/josephrb" 2>&1); r_home=$?                                  # [RSN-6]
[ $r_home = 0 ] || bail "hsi ls -d /home/j/josephrb rc=$r_home: $PRE_HOME"
PRE_TARGET=$(timeout 300 hsi -q "ls -d $H" 2>&1); r_target=$?                                             # [RSN-6]
[ $r_target = 0 ] && bail "$H exists"
{ [ $r_target = 64 ] && printf '%s\n' "$PRE_TARGET" | grep -q 'HPSS_ENOENT'; } \
  || bail "target check hsi rc=$r_target is not hsi's not-found (rc 64, HPSS_ENOENT): $PRE_TARGET"
PRE_QUOTA=$(timeout 300 hpssquota 2>&1); r_quota=$?                                                      # [RSN-6]
[ $r_quota = 0 ] || bail "hpssquota rc=$r_quota: $PRE_QUOTA"
[ "$(printf '%s\n' "$PRE_QUOTA" | grep -c 'usage on HPSS')" = 1 ] || bail "hpssquota has no single HPSS usage line"
mkdir -p "$OUT/logs" "$OUT/manifests" "$W" || bail "mkdir rc=$?"
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

# 1. the setup checks, already passed before $OUT existed [RSN-6]; recorded here
printf '%s\n' "$PRE_HOME" > "$OUT/logs/home-check.txt"
printf '%s\n' "$PRE_TARGET" > "$OUT/logs/target-check.txt"
echo "tools: $(for t in hsi htar hpssquota timeout sha256sum; do printf '%s ' "$(command -v "$t")"; done)"
echo "home check hsi rc=$r_home"
echo "target check hsi rc=$r_target (HPSS_ENOENT)"

# 2. quota preflight
printf '%s\n' "$PRE_QUOTA" > "$OUT/logs/quota-before.txt"                                               # [RSN-6]
echo "hpssquota before rc=$r_quota"; grep -i 'HPSS' "$OUT/logs/quota-before.txt"
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
__LIST__
null_roles	f709d23b6eef486a63e8cd69921472aae80c1d554355e6fc097c6d7ef0308db1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_2p2h_0.npz
null_roles	e0b44d6525089b1d72cac245b9eec4d970c1ce695636296cffa370693512919f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_2p2h_1.npz
null_roles	960b34955a33212d104c6511161a093ce4301db57aa2b14251fd72f0699def91	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_2p2h_2.npz
null_roles	1fd5362661854b205e456f3cb9be3e973f206302ed469d1b8b7c60672ab587f5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_AGKYxF1pi_0.npz
null_roles	de2a0331a0f28620c64db23c442201e3e1539a25380387157e321b1789cfe119	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_AGKYxF1pi_1.npz
null_roles	6687bd7a57cff37f1f982a722ab178a6b302184f485381e3e0569f48a838c5bb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_AhtBY_0.npz
null_roles	fc6410caebe94838a98dc22787341adb9e0d08df7f45df5c8aae9af942d46765	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_AhtBY_1.npz
null_roles	6a7872984109e191b7c9ce4850b769eaaed91df1283738e64ca7c77316769917	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_BhtBY_0.npz
null_roles	c63a944f49c20d2d5dd547a9a6657966fe612c060cfa7100fbfc05b7b1875734	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_BhtBY_1.npz
null_roles	3b95a36636b13e7881350ab4544adefc96410d7f3139c5c889696eeb7ee5b20e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_CCQEPauliSupViaKF_0.npz
null_roles	a722d3fb0b8d9c7dfc69442785748108db9059cbb55310ef59fd27a2ab17c0be	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_CCQEPauliSupViaKF_1.npz
null_roles	83ce513345a3a68b305d8c8946633cc56c2f3bccb0d2df5e2fe8eaf9ae5b2715	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_CV1uBY_0.npz
null_roles	c76e0115b9dccefa250d52bafc9e72371b917beb02735d7221fc1ba2b62eda48	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_CV1uBY_1.npz
null_roles	758844120e63dca0a823b3e66ed97de51a2ab359c02a09c885a95bbfbf90e246	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_CV2uBY_0.npz
null_roles	22fa8a708f434f43129e1a3ae94b79cb124b19becba9a8033d3ddcf085063028	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_CV2uBY_1.npz
null_roles	2e10ae120b5b157eff0c33cd646bcbe3f9700081faa40be7cd643505056947c8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_EtaNCEL_0.npz
null_roles	5be2f6b0c9d60f6069124d0639a9c71c4e332f1311f7346fff823e2507f0cf5f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_EtaNCEL_1.npz
null_roles	1255b4ee152a45fa056327fd51381325664d0c52a3f3aba27e6a4b12d32baf54	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_0.npz
null_roles	7ee756d79a2740d4a32500c9dc6255dc54ef71d01c49f94d8735a078e4e0db46	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_1.npz
null_roles	1c13f7ae3b085bfc1bf5488a4ba092e0d990b58abfaf6d4b06de7afcc06985f7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_10.npz
null_roles	79a956556e629e901035ec25ed9819f7165377e1253e703aa02a95ba42e07167	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_11.npz
null_roles	107f9fa45e8695fde2cec81c615d4f4aca5904e618e77b1a99cf0c3e2269cf99	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_12.npz
null_roles	c8c16dd74aeec740172ab1c5dbe8226269398f9d89f96fb11b47a89acc5821b0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_13.npz
null_roles	32759beca00efce685ef05b4ae34cbc9402863fdf8c50a0afbfe5fa79d323e55	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_14.npz
null_roles	bd6dd3aa54d85cb87cc88c9a006134bec932580b5998aba1ca7c1f537bc69100	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_15.npz
null_roles	9429e6c0b08da1ef8627f48feb3bdcd3dfbc9ed9e960d206d1219d61ce4f8d6d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_16.npz
null_roles	17642d12f59fd6ef58717fa3d50458844851f5a65d79122aac007bec810be963	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_17.npz
null_roles	0d8df34fcc103ec69bd0deb2df55d7df8d7249737420623bac2b4b7532677aba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_18.npz
null_roles	90a674bd446a2266f8990b0911ab8de7bbdf6e399af24ef67a0f331439233409	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_19.npz
null_roles	ef973eb8df418d31e4d22e07f8736943ce96ee5e12f483d66622dec1834cfb52	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_2.npz
null_roles	14fb98253c8ba96eb901fe1560dd2b36f4e5827134a3552239f2be8f9be817a5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_20.npz
null_roles	f78a5fe7ccd6cbc8ab323adecbc3c80684f46fb7abd5f279634847c8d8ef2497	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_21.npz
null_roles	c757d8905b001417349300c534d45a4c0d1387dc9ec8bd7c3342e22299618243	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_22.npz
null_roles	04d9c9d5a711f44b3856fccf2148effbcd50705f653a4ff263983461f95e0172	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_23.npz
null_roles	1100bd598958892955ce11aa26dd98e66596c897dd2a186d2381b8e165dc2713	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_24.npz
null_roles	c3d5c5cd2742eb7eb7a54ecd5eb737f26f5f60ffac4c6e5990b833b00b6a528e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_25.npz
null_roles	a2279cc8d92864852ce10137afc683e035366009d00d18c61e3752d457caabac	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_26.npz
null_roles	c7e7a9ed701e3240053501b7ec0b32b7b17ed3d6eb8fa60c6a20460fae9fc26e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_27.npz
null_roles	da5f3f4c5813c19a84d3ed5fbb9ec5d77a9fc877edcea40c1ad5895893dae3ca	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_28.npz
null_roles	5da9446294990563d3c9373696a939280d9ce15d3a21ababe9aa2c163cd3bb8c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_29.npz
null_roles	a1b46aaeb1a3cb31fdc00e37dbf460e5f787039c27bb18520270d9033000139b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_3.npz
null_roles	46390c4cffbe7662c5a5f181b6179567e3b1a42dfaa1777a4b6d45c7cb5e6675	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_30.npz
null_roles	8542034672dfa2b7a7c4ffa3737e7c6ca8d28bef16855eecf30371fecbdfc63d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_31.npz
null_roles	c2c9c87d2e078aecfc547d1b68546db17792d6d5fc06d339e12e0f3664843d31	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_32.npz
null_roles	fdb5381c65a41c64a45cf557523ffc6776ba309de3c3bd5ebdd4c20cbd6050b7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_33.npz
null_roles	7e80716e9dd220169dc5f280884ac81d7118ec89afc80a46cc61c410e4e88a23	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_34.npz
null_roles	03e09354bfa9464fe272121b5f90343a7350d03b153f3551671f0ea84588cdd2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_35.npz
null_roles	75055764a7e7adc3740f5876b9cee745b6308e3f98bf00822b78cd9366290680	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_36.npz
null_roles	5ab24024acedd419f08f56a76275ae6ed233436ff6256624731b942a028dc122	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_37.npz
null_roles	9ce032a334eb5fcbfe68b3b4cea26bac7fcdc7d7ce8dca4a94cfb5e90ace20e0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_38.npz
null_roles	738eb3e61dbabfdd04948099b7ed6941b118453fa28aa7c69864b45029af842d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_39.npz
null_roles	fb96dd022d80a6c09f6a1ab7a232cbe6e2e1c1d90087eb8bb17098b9e2a7fbd1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_4.npz
null_roles	d48ef4930912b1a789bccb0deaa838c30cb1c1f042cf8bf39ba04e7edd5ddd7f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_40.npz
null_roles	065addb5f7729b0fdcc7ec3380f8f57ba73337a9cc9a9e5e40cfeb466e12cadd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_41.npz
null_roles	19434093a8aac96f26c3574a0351b9ba22b33d3a9946753097db52dd71316376	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_42.npz
null_roles	5c30ff98eca61b1b6dc11939c94a4f90584f1ef1bec90876a7a5189ffd4f9af4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_43.npz
null_roles	470046beb1242783c603972f3b46a4c6c2dc6181cb956d5135a8feb2ae25864d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_44.npz
null_roles	89c77a2300013116ae37a0c78e9ff2ffd8ebd3ebf1cf5cac39f910a0cfdf2cbf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_45.npz
null_roles	a3c81e4db7def03e3ef5c12e9e65387b2c295a5e1f91a88e692958c25015f728	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_46.npz
null_roles	b003f0dec14c9ac479a0c421f3a41f61ac563d93a5c6d3225da600836824dce5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_47.npz
null_roles	9e805c0ac38252331b8aeda42eec27858f4cea2dc98d3d1c85b0492b0c4a5f2c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_48.npz
null_roles	4ee2aa0de6fabe10c5834482ef8f13d9a34feecb3a60de8292128bad29ccb7f8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_49.npz
null_roles	dc620ac9016f0fc07e394846559acdba71f7d7f48e4776518efe2d7da9496634	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_5.npz
null_roles	00d0c393c5e3af4dde83a77d07370c4c580f0b8eea009dc6d190eb0734048ce5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_50.npz
null_roles	27c7367c3f4b595f457231d06eccb19fe39c48de5c395a1bfa1de507e181b242	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_51.npz
null_roles	626ae0dbb2e339612b3a13adf2cea79dd82aad105eec089b9d11c7ed7cc09ee8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_52.npz
null_roles	052e6efa2ff49dbc9880fcb4c60e35716d6827e5b5e6626ae3c4462456031193	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_53.npz
null_roles	55ad1e4889f1b4963e620286ab396128173ae2fed16d5ccbcac0ded121616b1d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_54.npz
null_roles	06212a81ef6439e15025eaa1c0472da62e8901962b59cc6df246fa3de036a7f7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_55.npz
null_roles	64b42fd6bdda8500d806e1f0e0ffacba68bead63500c8a5e2be665822b7602f1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_56.npz
null_roles	f0ea8abac0d2885c21933ad0d649e9b2b140bc4afe97b268c7e55eadc0096731	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_57.npz
null_roles	f3426fc4f708c92fa8cef33b0875fea106db3f8871877a938e65000b55f8f159	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_58.npz
null_roles	d74fd7948c53753202d6b42089339abf5c71d747de800052bf63fcf590848895	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_59.npz
null_roles	4a4a2eef073589b0505f2030d8a2ea9c26a531c939061f0e594fda41db63638e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_6.npz
null_roles	3f2802b9e1588653e98f263a7b2f614885cd434de497d8d3b37df08d7673ddcb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_60.npz
null_roles	466ffd24c3c2afc33a516e289fc02f1efa730a5f8a763f595c56289542a12193	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_61.npz
null_roles	1de37c9af85a7a1d70a6b734e47adde41ea29bd1a1a1da3baae311d8f88ff064	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_62.npz
null_roles	2d09f31a791830fef5969f95ea7325d795777a2d7ae3ba1a281a46f3952cceb5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_63.npz
null_roles	d8dddd7766f16ff50b517f8062e691ec06d799690c6912ce54aa83faad2b073b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_64.npz
null_roles	557faff44c846332e27f1bb93408969f7a417c825222d6224d04c88851d46a89	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_65.npz
null_roles	0d02a5caf138cabdab722cef4397fc701238c7557107644650fb3682fc86861b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_66.npz
null_roles	cbd53a22f610492229af69a3699a755c9e90b68219a052a8f06a1b887b72f254	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_67.npz
null_roles	7f5534016d34e8ed43ac2720633c536ed31ca9da79a35b64a824a56c507215c4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_68.npz
null_roles	20f0fb41b4f9e45062ddcb26c8cf8f863cb875b46fc41c718029840336290cbd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_69.npz
null_roles	088e4aa6842732d289cd8d988b43dddc44a991b0ea81c8d54324cf67ac46c7d4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_7.npz
null_roles	003a7e85cca6470e10479b881aaa9c8463902145bb047b91cfbd4e40a3614eeb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_70.npz
null_roles	e13eccafeee479c501e3ba5b404da35174713042162f8e253e466c8ab03761b9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_71.npz
null_roles	e1506b6f6cff9ac0d578349db24a19050f740af0a738c9a9ae7394e2515cf306	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_72.npz
null_roles	cdf435aa5607c10298f919f6aed30b0763ecf8def5b7e4a77341dcc636f21f17	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_73.npz
null_roles	9234abda5bf8a710b93439bab6d5f96dd75d223d712dce9f157bce82cef6359e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_74.npz
null_roles	a689c79b3caddcf802f0bb774b849e2eb8ae8766a9eca2cd06bc4f3a5a47c4fa	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_75.npz
null_roles	a28fc05caf7586cf872c438706e99a5445c0e365bdd559caff5a36ce8619718c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_76.npz
null_roles	04db3f5eb4edbec1f3aea81cbfe32f96792a4c50325e1085d797dd3d2e16ccc1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_77.npz
null_roles	3c611f3701c5c4573c6c83885e85c62a2a40dc1e840b36d0e89a561f12838a66	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_78.npz
null_roles	d0bcecded32e33c5ce8b6bd32b5f68adf9325e4fa6a3215185cb7d8c97ee6b37	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_79.npz
null_roles	c99f3b2341268fd7262ce6795348fd55eeb54c9d8e86feecb402451c0c60e289	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_8.npz
null_roles	4c5e70fc0ec812dbf63034ec176c732613f95f0a32ff5a0bd1cb35bd00dd754e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_80.npz
null_roles	3f935bca58cc9308455e45a3fd7554c86d2aba0e7daa306f23cce37a4f9240eb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_81.npz
null_roles	cd0ad51da1c901b983ef67c409b904bd847e5df2f541cd86b94ec0b319c594a4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_82.npz
null_roles	796857c41a5ef07ea5186a9b3991d6aeedf464fd21cef2d49da9f0a0f2194eae	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_83.npz
null_roles	36fecf2baae83d0d82b9480d7cc3cb8af2b1c250bbdefdad7a84139f8fced4e6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_84.npz
null_roles	1f9f8c493f2eca973c03ad068f6f32ee425b47d1c7e5a172f121fc0ee58c1cd1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_85.npz
null_roles	b24d65caaaaf1251fa9970c1a415299dce48025696bbc5f651ae1c5cbfe650d5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_86.npz
null_roles	f81798f06919616b9458f60fad4aa86fb238fe06dda5dae688aea1fd12e580e3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_87.npz
null_roles	3c6f37c2aaacaba3136ea305c293f0eee26743178c9ea28e201332da637ada95	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_88.npz
null_roles	9444a588237c0c4b2020174ea9aa7375304aaea60e555e45018e840b6d0dd92c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_89.npz
null_roles	650daa3193852ab0ea04a8f0c62c8d3a278343f5f294a276e7e8521993966f51	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_9.npz
null_roles	5a9253b917b45c91fd2574cf0635b98f0a11f9d840597618eb6c177015613799	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_90.npz
null_roles	81aa431835d42367bb83bd89bc6890cbf95385d9ca1fd8482b5850929df438d0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_91.npz
null_roles	ef81d1213646fb98f08fba7254ddec2c3e00f2f6089173e5ed729b069242f784	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_92.npz
null_roles	528538e178d9811fbc1c1603da02159ef5cbf7f6cf55f7f98144a42fcb1fd7ea	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_93.npz
null_roles	07e226b40191fe3d584701b02c03e15ee81f87c06f1a05ca4cd2a275f0f9b8c2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_94.npz
null_roles	e301f6b8995e3b2e1596688e05d47d417dfc9d84df6edeb8cdfa1908081b2bca	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_95.npz
null_roles	ac6d34666f3b8b77c82aa5cba610159683a5bfc2351b34a381426989d0dfeda5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_96.npz
null_roles	b88075ae8dee74bf3cee818e5e36fd9c5ec09450ba6dbe6cf7f1b95fd0f9a0ef	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_97.npz
null_roles	dcdd8544d12dc493eb07814040549458e1eeabcc239609936a09b757af05e14f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_98.npz
null_roles	42437de58966154b1f4c23ca85197ce9c7002cb49fcb50e62b7fbe18c833e884	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Flux_99.npz
null_roles	396c93bc75cd68cf538c642dd157d26932834e3d2a29b1e7b63a8be61b694896	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrAbs_N_0.npz
null_roles	09ae6c72a77ff35a6507e84137088b05246ca3dbec7eb77bd3fa296e0cf955e3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrAbs_N_1.npz
null_roles	6c92dac201805bf73f670f411c9a8fbeab5cb5ebd2548fe6dad89bdffe4aed76	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrAbs_pi_0.npz
null_roles	8711d88f569e6accdab58757cd3e10250b5ee52ba4c9087de47a504c368c4e3f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrAbs_pi_1.npz
null_roles	4dd069a8e5914d7369d0f842bfca8e969fcc954aec49e849ea288854413c4472	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrCEx_N_0.npz
null_roles	19fc0c87317dcac77abf873844c44f17391df0e73dca2ab5cf2dd9eca06f3793	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrCEx_N_1.npz
null_roles	caf51691ac783bbb609897f259b58ae0dc05e0c91797c69e98dd071ef36ecf96	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrCEx_pi_0.npz
null_roles	fe6eee3286eafae41c9a67c337a678a8464d86b1eb95d4969f30f1657bf054cf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrCEx_pi_1.npz
null_roles	d0a0e6bc9710e4362fdaca0266e0fea64055a3a3f35bedcfbacd5b93c547d643	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrElas_N_0.npz
null_roles	c0ec76fc986973ce7375bd3024a55e99ac0a7c4ed0357478769241e435a57f83	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrElas_N_1.npz
null_roles	0e16ec715e5c0c53ed3de2f1f1470db12bc42ffa53091c5eaceb050d366849e9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrElas_pi_0.npz
null_roles	aa272301aa20f0a277777223a498771d86a6bf6084498229e3777d2facf2f65f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrElas_pi_1.npz
null_roles	c1d79397850031b3958952e464c77f40a525ba8ada8b4a7a3a0fbe1c764ec77c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrInel_N_0.npz
null_roles	342d33b209c68720553c026b9543076e14389494c36bb2317061d3dcba9bd3de	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrInel_N_1.npz
null_roles	32ec429013f0ced901e11fe51947284e6949d25031976e6eb984a3a30c5bc8c6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrPiProd_N_0.npz
null_roles	2fdeb3cfa38ad836529e92c66463cda58ba6d625d1a4ae8d30ae567957e2044d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrPiProd_N_1.npz
null_roles	cbbb6fa385b89885527dbf5ac6b7a940201bcc6f95c069ba01703d57564b49d2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrPiProd_pi_0.npz
null_roles	aab2285b1e2045266f1ce3e3eb42e5bd0086bfb824ca0f6d99c6c38fc86a1e1d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_FrPiProd_pi_1.npz
null_roles	31c7fe54f4e101301eb536d662155923ec934dc912fa97c0e01ba8a2fa8b0a71	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_GEANT_Neutron_0.npz
null_roles	b494f9f686cbb79b97665737696af4d50a8eda029b22b5313e29f0327a05708e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_GEANT_Neutron_1.npz
null_roles	82d96223768181a9a0b205d07036838505e143af6c8aca05b64f3c062e2c70f7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_GEANT_Pion_0.npz
null_roles	6d88363d83b06bb110f17a1479c389c076304ae1699140a43295bdb9f5e82add	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_GEANT_Pion_1.npz
null_roles	46d4499fd2d970de380c3ac84844645df43d747b63218794d98a1f9fb9a91ed3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_GEANT_Proton_0.npz
null_roles	9c9621ac97cf17c8de5e48c288d05612f32cd26d595a9b57bf89d6250b25ae8b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_GEANT_Proton_1.npz
null_roles	6e646efb273e6d4da28c07f9fd4d1ef39d5877282de8a961fef3c9d7f6684995	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_HighQ2_0.npz
null_roles	28c862e88f34441dae654c477b16de81ed77d5c296839e42a5169f2ece81baa4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_HighQ2_1.npz
null_roles	270f6ede4a06c19fd5993e73dfb0b6d11b79f9bd158913442681de20aeda99b1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_LowQ2_0.npz
null_roles	03c95fc3da708c47f639dd9b7ff8363c72718a8ffa938984f8f6dbf8634647a1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_LowQ2_1.npz
null_roles	3efbedcd443fb79316d083cfdfe55b1a6759dec6fd02ee961f8ccf8fed4207e9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MFP_N_0.npz
null_roles	4477d68e20d209a9e8e4db4c6fc3ed20e517d12a83945ed5f769fcbb6f5d8264	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MFP_N_1.npz
null_roles	157c41233dec9495b080201354d27cb61e7f0ffa671b10407cacbe6c99682f91	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MFP_pi_0.npz
null_roles	e2478982b44555029305ec1f248bb9e73d5c5ae54c2b6cebb6004574ea457b24	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MFP_pi_1.npz
null_roles	2f80852ec6c991465a9e1c3d1c84fedd76ae41784ff7494f9c5d192adc5dce36	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MaCCQE_0.npz
null_roles	771be0a9899080d4391dd100027527b5d9231bd9698ca4a19d13f249a698822c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MaCCQE_1.npz
null_roles	be2342095050170cbe97ebacb8240ce08f8a78b7411109b814220590ba85bcdf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MaNCEL_0.npz
null_roles	d96be84c117bdae540f2a2efa84f1a2b3fbe6bfeab2361656f1186ec33a091d8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MaNCEL_1.npz
null_roles	13092d8bbdf04021cb76aca879da83f8e14e3ea9cd00119561eb420137cffc4e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MaRES_0.npz
null_roles	154dd7ddbf6664bf0c818cb6399f1b43905f0a05172fed46e3787d00664efe03	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MaRES_1.npz
null_roles	141c9a09eb81dfed882af8591534e2fb42ef1a9a6f85f12306d6546d3111f1a3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MinosEfficiency_0.npz
null_roles	164dccac93bab80fd3e49da9103e486799feaae85e80f98221dd49cb6e626f01	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MinosEfficiency_1.npz
null_roles	22d6f6628f0c41b9a9c66c7db0fc188cf5a60f9dc4201dac09372c91290018f6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MvRES_0.npz
null_roles	fb48d419e89a4bd7d6b0512db7310d2b6fe632bd1851dae4fec7d4d1322d0743	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_MvRES_1.npz
null_roles	d87cf5453a2a85229c35d926bf9c623faa1fccb86b19b4dbb17c87c55a3ed30f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_NormDISCC_0.npz
null_roles	d7defc09b99bb62c00e25f9197715adcdca8e4d0598f1bab44d40504e9ad05d5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_NormDISCC_1.npz
null_roles	54f715a75e94d12952ce08ea1712f5c7709e0824ff0525ae282dedbf1af8e751	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_NormNCRES_0.npz
null_roles	be58ca79726d74bcd68c439e7b2c9bc89244915b9a70aa1b0596a86318156ef9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_NormNCRES_1.npz
null_roles	1b85b0349278c5307e156585771ecfc263cba69d7fec7e4a612c32bab75a57d0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_RDecBR1gamma_0.npz
null_roles	13f5461caca63cfc64942f4e474692a39096328020fe89a7a1c806fdc1845045	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_RDecBR1gamma_1.npz
null_roles	fadc62d65cbb12a7966b3747e79a882418f08a7a51189a339784740d912aebbf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Rvn1pi_0.npz
null_roles	ba80af7c78cf9de2a119e621a731207e745969244603dc3eabeb5f2dff1c7410	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Rvn1pi_1.npz
null_roles	51aeb598858eefcd72c4496bcc3e43096084a4ed8ca6b62547d6d6c8506b3bf5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Rvn2pi_0.npz
null_roles	fff0ebdfe950206e7c08d33231a6ec438eadc77459b6273860c84cbec1258804	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Rvn2pi_1.npz
null_roles	22859c47855371b45b9cdce68afd9f984f01aaf456f9f8b029cfd058bffc079b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Rvp2pi_0.npz
null_roles	ebdfc28815d6559319c0589271a5fc3a486b2b5079d1e9e0c06a566a1db46db0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Rvp2pi_1.npz
null_roles	f55ab8b880b39b49f9c6cb5fcedaab0eb66dede5e991dc91aa0824028aa4c737	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Theta_Delta2Npi_0.npz
null_roles	f28de28cb659f1f31abce5e349f6a6cedc95958b7d1d3058564fac1ecd23d68a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_Theta_Delta2Npi_1.npz
null_roles	42c805c169a722fe239d404fcf97447ccefdde67b867ffccd115554723efa452	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_VecFFCCQEshape_0.npz
null_roles	63679f4d6f1d63d2ddc9cc4e9b879aeea89a2fde60be1f3f674bdd2910f3fe59	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_block_VecFFCCQEshape_1.npz
null_roles	118202706ce81b5a49851a60f180445b40b116791b77224d49a6aefdb82def9a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_central_T.npz
null_roles	bda1467e1b6eab37e0e13cbf1bbdc6cf9f5dc80580dce27922f31443c42bee4f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_seed_T.npz
null_roles	1435357252f19777a8a35d49adb905d0fb8c585b4200e6e311a319df1155549b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_1.npz
null_roles	ac5974032a0e8b94c997534447b396cd0803a43fc3344affdb9cfa3a78ef2e5a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_10.npz
null_roles	aa24a2013fbebf053c77832f8ece833b6fa9f3f43cd615107847d3dc750ed16a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_11.npz
null_roles	1ff15efbef944cbca9278747f9e0253d93dfd2e458dc36280169390a977b8dc1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_12.npz
null_roles	bc58bf9664350d7729404e859af2fa376e44c8f1ade73bd998d19c48c1bd49e2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_13.npz
null_roles	940fc3bb2b236a4274399615046978556c679ac73962363fd03834e3efce1eba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_14.npz
null_roles	4d284401b107697866dd7e0b376d0411df0348bd957731ff5c087b364990846e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_15.npz
null_roles	18910421637185ca91846a95865674e5b3acb176f75eb5f4225ce35d8fe7a121	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_16.npz
null_roles	c4815ea1b88849d8caa576e64cf3af1009ccda1b77565345cfe9bc3f3b1a1769	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_17.npz
null_roles	96e04989fbeecce0b2f6c766434f17f02ae64c12bf8a8b06927973820f209103	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_18.npz
null_roles	91c1e940f758e5bdc874ecc44d4456aa7fd9a20cd14e04a9a7e51a5782e65c66	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_19.npz
null_roles	9c7b56fd8344eb71af83965cf5050cc4c58c398c1ca970ab640530ae0ae66bec	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_2.npz
null_roles	7547d63388203853ec137a4d9d5b200dc3616edc0c39fbdba0d9ec7513366201	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_20.npz
null_roles	812ca23aa069281bdd6743d60c003b4b6ce613de7e533f803788ab6b33c851c0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_21.npz
null_roles	a6272bbcfa7ed197fa20f82f1ec867cacbba8ffac741c6093df3710f7718f06e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_22.npz
null_roles	69f862c7d7761c128c735a0194aa05773171b216fdda2fc84bc45bd28e6b54ec	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_23.npz
null_roles	f4d26cdc65240b87021c8f393bdfb2ea854c29796a73d350c9192ed9043cfd26	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_24.npz
null_roles	208664969d38e72f3ce65f9e6b710c4421ffc782c607a3a057e4f3dedf98c026	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_25.npz
null_roles	556fd072471114ec6917615c68832e0a3f3332d3cead2bcce9929b98841f88ab	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_26.npz
null_roles	99dd5b036c5c37107a351a64024307c738f4d73814493f3c0bc9bcb50598bf2b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_27.npz
null_roles	006114840aeef02ac86fedad1d29e41fcf634f82dc2aeecb845708cc6133cd00	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_28.npz
null_roles	a4fd949b37cece4f7396063471cde9689df4cfdb157a5d8023735f830a043b9d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_29.npz
null_roles	0846f461eeba5b0f3a6d64d9d5cddfad93efb60f83c2b4b3d59f710a09aae12e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_3.npz
null_roles	81adce852931f091ae5f5cdaa8c7b55dca7403db389a1e0097038dffb3fa02b1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_30.npz
null_roles	6e2d57d08b32385174f169359812c5234d8a135e077917e90bcb30d9ef7fcd2a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_31.npz
null_roles	7a58fb49c679c2bfc0d8fe8a97bf0d2aa89a0d11815d7d66f458586a616557b8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_32.npz
null_roles	1807624d8025df0a99f8728b90160483df0b78e6f8da3739d510f50232efaf3b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_33.npz
null_roles	252651194284061a2221c36ae42f5fa3941f1a66c8195ee1b3deff860dfd056d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_34.npz
null_roles	a363f034aeaccb30b229e81b64c4c26d9a3ce4301241b23447085d35f24523ba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_35.npz
null_roles	36f59e2a54a2c4a24667dcfcdbbc07e20a5d24c6dac3102396ebc76d838dce56	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_36.npz
null_roles	09eabb8aaab382f1dc1d753d67201f5b4a3c6b7d6d9abff27d8eeae3696c7472	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_37.npz
null_roles	8bd1402a4d927abfdb883d30638e1ee31bfe018c0961d0f9bf652e9c3b674b54	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_38.npz
null_roles	5b69766f3e366e5265171197ad4485da2b71b5deb612eb7107eb4dcfe18094c7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_39.npz
null_roles	b823e664ef8435de8300bbc9eb1d069c668e975d313d133261b7bab65aefcb6a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_4.npz
null_roles	bd40276c1fbabd86f05cbe00913a3f01156de099b977a20e20b9187c54515ede	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_40.npz
null_roles	7ed78a1548c73adea0d0b114ddb6f7409d0004d420f03f5081bc7f216739dede	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_41.npz
null_roles	b13319f54d361f3e6bf9d171355ba5bbaf80c21d1a60a93c4c2468c0e0d1c9e8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_42.npz
null_roles	a30e5a89cfba31fce9c23099f2ecba165194cd102860973c5b33ade5cc19f821	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_43.npz
null_roles	e2840f712c15171a9974981dfc66046a38037ee64014fdb8db14247aba5ed5cd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_44.npz
null_roles	223a07e1c55673e59c58ca099e2bb6e70c255a1dabfac3a9a85caae5db4a0614	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_45.npz
null_roles	814d38f8994c369116cd26e1afff49303856786d2b860ac957b60408e60933f0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_46.npz
null_roles	b360bab42083aa29523f765013f98e453bb1536e3add330ecede7ab617cd784e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_47.npz
null_roles	098143964610c449ab84b356e2aa811c5ee3cd0112ad6168df56886a889a1e2c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_48.npz
null_roles	8307e40dc68551aeeca22c7411bdca98d32e6d2f090c436584964ad4adee5124	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_49.npz
null_roles	456803896eb8bfb465855000fac2693a0a93059975c8d70268cdc7386f356cd2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_5.npz
null_roles	8334c53b662054c61698a964a5bfe40477e9090a43faa02b91f999cdef6284db	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_50.npz
null_roles	4659bdf9c7fc84bf82c959d2bdd34cdf0bc09ad5ef4c7176f885a76da3ec5f8c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_6.npz
null_roles	73ba862663beec21d9c60f5fbd32bfb51798812ef70645333302b7f4cce8353d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_7.npz
null_roles	a66ca22a787baee2afc1adb9b5bd0b9e680165f4b1af34957f0cce0f884e3e09	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_8.npz
null_roles	1a19769d32e6510ab6dfd4b36bdd0064e802e2ba4ad8da8e0286e9bb398e1280	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_stat_9.npz
null_roles	2734fe4ceccc6562b1fa06019fa08b7118aae9168c1a403164e657ea35578afc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_2p2h_0.npz
null_roles	d785095c63a34c6b77220339fa83d9c6d77ae43c04e515c630c11c95d273650e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_2p2h_1.npz
null_roles	3816d3f2f9915fb9bc2a69a9e3caf2de97adc052b7019a78321070f01a7de987	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_2p2h_2.npz
null_roles	e865fd45714b7fc8aa975c9f832dddb30b572808ebcd693a37c49d7f088105e4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_AGKYxF1pi_0.npz
null_roles	143781e6e270d962021e028c6eaf4df713d694f73ba793ff3fd9775e884b5cf5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_AGKYxF1pi_1.npz
null_roles	07ccbf5fc3e577b577113e9277d26664ade372ec173df903a379b9ec8211bb7b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_AhtBY_0.npz
null_roles	6008534fe63283c0aacc3bc4ceeafc6795e536f634ecde9dc105c824a394aee4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_AhtBY_1.npz
null_roles	0aeef17973d87a913b24bba43f51a66e601bb1bac0a2e4f4b0932cb44c962d95	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_BhtBY_0.npz
null_roles	2223dd9446ece52c08c569cc1e0a85de4077d649928080587f24bd7e9f96c314	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_BhtBY_1.npz
null_roles	30cdeffedb00fb9ec555e0143aa699327da4b4b1fa007b8959f0d1ffb7b4e558	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_CCQEPauliSupViaKF_0.npz
null_roles	186386e44835d138e0603119a780ad17584d7bd6982a9544ebf8a447e80544b7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_CCQEPauliSupViaKF_1.npz
null_roles	095e7352a624f9b91c1052d4cb0eccd9cb70825c27bb1b6f5716a6243d9e78dc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_CV1uBY_0.npz
null_roles	9837f7e364ba0476f9d3f1d60999b5f974d56aec9424d2ce321d8b137c380e6d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_CV1uBY_1.npz
null_roles	df153f1b1090f912f8e1f2b2520526c24867e4f3a4d24e78f6a6dab7cca83287	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_CV2uBY_0.npz
null_roles	9f27007ffef340f60da92f7f4dde6c640bccbde9a4c3730ae9b30c45cf2cd705	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_CV2uBY_1.npz
null_roles	006d83683bd43d7596712f0ef069dc4ea223f6ce72c779a6897424c99210a9c0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_EtaNCEL_0.npz
null_roles	9239878673c59417621e5702c16d071a54b96b6f64e48bd87fc1d2df0ccdeef9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_EtaNCEL_1.npz
null_roles	d6d436acaa753a3457fe649d07d956c37a8fc9f08634ede12f655e646280fd46	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_0.npz
null_roles	aa71d8df95db825b7e6ded8f655ad15700896355ce90a30c5a702e976181f52d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_1.npz
null_roles	55abdbd400fecfd19f104b6617cf7943158f4bfd2b4b886551986a9eed16fd50	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_10.npz
null_roles	b4fbf4727dceb4f0ceee14bc332a9ec4e466b23280302f00d6a3b84b660ef76a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_11.npz
null_roles	3ee3c8a1a413d1470bd410f68c9d61a8a92e6db4c612635d6a2676136b146cd0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_12.npz
null_roles	907aebf2b169a2267eb3b0b3d43c0d1377a143676a57404fe9b4e7525f838515	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_13.npz
null_roles	12de9496849645b22ffdaa095400d7b7233b4ad63ff2265705f3f480e49c399c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_14.npz
null_roles	d33d1f3da8e653953c5dd79f2e80a98d4395400a7d09273908a417aee446d490	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_15.npz
null_roles	dc097184f5fcf131b621f946f3eeb0141972a613d5c95e9a9e46aa346ae4df25	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_16.npz
null_roles	355bb51332908d0e0856d63f9af5c20272315f9b337798f40783b36992d8979f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_17.npz
null_roles	db4fab93aaf7ac23153ab6e72d44aa7fe1a961605590b99b4bb8d95530b2efb1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_18.npz
null_roles	db6d3a2afa35413ba276812147cf4f02ab5de4e5654dfe75cf8bb123bc9bd0c5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_19.npz
null_roles	f704a099b77e75a0daeb7150240e67a36488a86dc45fa56cac74f3a65fa344da	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_2.npz
null_roles	d1db9017b84725f34117805ef3b5f11a370ad8491791010b0ca1c6347434cb6e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_20.npz
null_roles	c30ec14f4a97a8580567aaf104c40a885355543db35371198ef7db2bc33f29c1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_21.npz
null_roles	16b6a4d1974f6afcc13da32f9fe3a17c162d8399244dbeea291e26fdb8024468	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_22.npz
null_roles	2983e513f5654e960df587ecce44f1edb950dfdbc0fd7fed9fbf60c3ae0dc18c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_23.npz
null_roles	d94fbca0839418cb89ba63a1beb9583444ac66c96f124d75448043a39b1f427d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_24.npz
null_roles	0784a84571b7f2671d09c2049dcfa594d1e1c9d03dae4bf5ddd78ddaf50e5257	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_25.npz
null_roles	81c588c6bed30bc1fd5604d0a3c39f080506fa194d163a626dea8d43aa79f168	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_26.npz
null_roles	74d0ade24dc80205174862e865a1a65d3315a733bc4bccc789c8ea7fcf9b10a0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_27.npz
null_roles	7548de2e052e65c60e4284851f627ff50eea954169f6b2fd43b5414fca68cffc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_28.npz
null_roles	c2a8b5d7e6c3e44e47db301b53140825418a16439dbc563184e838d2ffab596e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_29.npz
null_roles	e558cc380384807d9e60288d7064a34b02dcf751485e94adda1dd1b408702e55	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_3.npz
null_roles	f5006da4c3c872ecf92995dde6eaf0a67f9563b869802b35f2dc2a969064f4e5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_30.npz
null_roles	706246831d9e4b9d1991a90f913d9bf98e26b8265a3b902e79506907db8d77e6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_31.npz
null_roles	9963a5fc64edc2dddd23cb1f1d1eddc7733a6f2304113fde9c87937ef4fd86a2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_32.npz
null_roles	b22552f3ba2d15049c9af4d08c90339573fc790ad9f51ad1408bea8f10ed86a2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_33.npz
null_roles	64689d119c914c4263aa889507bcf22121bbe8a722b6d4e0026f6c31064f1e20	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_34.npz
null_roles	0a42b735b6b63a2585a42626113a1d884391753d652e06ed050e313577bccc87	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_35.npz
null_roles	c5442c8817c22f8f269eb46f2c68b3f9323b8540ef8fb32eb1e8246559141b4d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_36.npz
null_roles	9f1f8fa50bb2580fd8eb3e5499a8db81ead35a171a69d114749c52b109ac2f19	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_37.npz
null_roles	0324129b7711ff2546fe4ac0e15172878e832495f7efbbf6fa505becc9d0b211	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_38.npz
null_roles	b92b5c0c62eef76fa5ee7133e337714edfeb427d47d9ebbab8556cc57ab47560	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_39.npz
null_roles	46ad4cf9c2bd3801d4a501c141e250f1de7255a5f4bea469d74f2ef43151c7e6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_4.npz
null_roles	35b3e670c415fb0bbf9b49ce08f98eece1d787c61e67cddcbe9ab8cb252a4d02	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_40.npz
null_roles	c40d0cdd2b2b63d3d9646b5644f75f7882f856534c983e2fd47c5ae29ac96435	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_41.npz
null_roles	88cefe88e9c2b48e626f307b6b3bd3d4bf7a324ab270132e59625f7555a2f544	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_42.npz
null_roles	ef118c7cd7498b19ff384da855280ba346213eb483c7652af8137ebda6dbd1d6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_43.npz
null_roles	1cc0e73d1d1213dadfa8650f7d8c1c7dac8d7a4f2f66591e287d9c851f31cb2a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_44.npz
null_roles	3bed5325af9e244859e42312f491362408e1c89e05cd2f12e8dc09316c6464e7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_45.npz
null_roles	941531d2af109b4c86f3d0d8404f2daeeb551fb01a3145d05851c44efe2c3da5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_46.npz
null_roles	57ceca33a7137f320cce4e27c5ec3843013268f35827f0e05cac6c45dda6cfdc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_47.npz
null_roles	ebdba9632d04e45526c02700ad816aeb2e511dc1bc6b310717cdbc262d522c45	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_48.npz
null_roles	fd8cf710305217e4f7be8fe562a48cb9d885b65784a8e7dad41dfc483ca455d9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_49.npz
null_roles	e34cdc59c63b848dd0c02c326757c60874037c81851bbc74e6cace6ae08907b4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_5.npz
null_roles	d5f5ceb9fddcbd26c525c2235a99035209a2d13b9162422f50f69e7ae8e96688	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_50.npz
null_roles	31eb9fdd286a3a27e02d2f1642dcf726adf47deb0106de46604b1d772561f35c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_51.npz
null_roles	93bb7d1681c9702e05929bd4a4813c5b4624a5f72240d78e4f2f76677795a8b2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_52.npz
null_roles	46e2f100c901043f87170ce39218de77c2b26cab9a95b3ce09a6b78228d81c55	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_53.npz
null_roles	f04805114568a6d6a449ff6601728d05a34c3a6536057d1a9786b4edcab76ce0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_54.npz
null_roles	d28067798b9d52c2276c9f5dbf01c0d1357a609258444e5db68964d49b56012c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_55.npz
null_roles	aef525fc7c5b4a009a73da52eaf05c2d8809e1268bbeb986e3ea9f56d3e1501a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_56.npz
null_roles	43588693dd0054416e6b58862e6b9b3bdb92dfee67e735f0b0998056fc22ebb3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_57.npz
null_roles	2ae37e3120596c22cb19208b7a95925229bf230154b72c6dbb8dc00d48849bf5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_58.npz
null_roles	d8184edadab67f3c15ff35de51fd2f0df11688db141f007e7b5e33269093e42e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_59.npz
null_roles	b2432ff5224eba410797ed5eaf0c93b0f32bb6405849a52e4ca6c83d9bc6252a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_6.npz
null_roles	3120c89b5d7b7f46797bf26002c357168b8fe881ebe02c34eee5fc7ac4c81417	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_60.npz
null_roles	33e676f368188841f5f626712f513601a9cefcd09f0d5aa6807fd440157f467c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_61.npz
null_roles	09ce4a022b4fa54223da320f883a3bc0a77a6faf0c5faa52ae81c80f64f09375	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_62.npz
null_roles	84eae6310c1279ae05079e2fe5cef6494347959288f0d684fea63a3e9f3bee43	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_63.npz
null_roles	d3d976dcad3d07ace2cee68f346079e82e94c857f501b8b0ef79eaff4c8af18f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_64.npz
null_roles	9761a2a8b96989d147f47b0bfde6f1e00a1ab68abdaeab43af96407b8b0027de	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_65.npz
null_roles	23dcd994fbfd3157c9b9ae92727cb3d07daff086bc8b17306c328293c6fe3289	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_66.npz
null_roles	895e936eada044a73f494fec4302a9d389251fb0be6cd2a06c85e04329112052	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_67.npz
null_roles	a79f538c086d19813f91f164541d276c6e8e5588200831e0a7585e8bf01cba8a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_68.npz
null_roles	39103ef44e384528766689cf463fc8ea51b15f457a5114c578a2e4c6c06f3b0d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_69.npz
null_roles	d0fcc300aa970c90b925fc329ab698293e3635f883e166367ac1866b4f88cf2e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_7.npz
null_roles	1b506e551da7736f070ded449728d9cf85547cf15f96a22c104a25acf94ac9e9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_70.npz
null_roles	6ca9ec8d72540995404211179d170cf229eb89509c05ce8a91206a495f42f10c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_71.npz
null_roles	4352ea5aaaf5fd08c1b63179b7804e3b9055e844e407ab63939b6fa8ea405c2b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_72.npz
null_roles	609506f6cb0998425fb41d15eb81bd954999c38e8f7f5beec89b430793ae41b5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_73.npz
null_roles	f94041d850ab6b1aab2f5999a638f5429f51b485e2316b5421831257813d35bb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_74.npz
null_roles	cc5fcbac8a6cca0de69c5f660416ca5fc7c07c6ff293d13fa12df518773e3e0c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_75.npz
null_roles	ff8b6b296c370e4fbe94035d2ac2ba0cf1fd4b0695fc6c0784e7ab8e54816221	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_76.npz
null_roles	7cee5733d3407b6fa48d150afe4bab70e05276861c3fe8d3efc89c6be327cd56	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_77.npz
null_roles	4894f060a8696e869dcae8fe9f9ab35f41d80809ce85545376d4b4a72b503902	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_78.npz
null_roles	dd0b8a1b5658a3bf988927c6ce743d5f17bfe9b2c0af93a5c4c90c993c2f9da0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_79.npz
null_roles	50c554f3212c3e070d8fd0eb0d436501c08560ce13f9b14f8f9a299da5b18804	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_8.npz
null_roles	392b3ecbc660ed71c6f125490ec40246cfbe4cf880d39b9395a4ff2813cdbdf9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_80.npz
null_roles	0d51f755051a64501dde10a4dc78b35299122536092a601ea312a06b100d5df4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_81.npz
null_roles	baafb646cc9a33fe61fc3d96a2467e5a2dd295f3a6fdd18a4118a0d3c5f3dca5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_82.npz
null_roles	df42385d2efc29b4f1c6ec8deabea067203a7deb34c6869cc98ee6542685a166	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_83.npz
null_roles	a99974ea335c72c58864785dce2e6e788d1dc57f8773914266997fbf63346ee5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_84.npz
null_roles	dcaefbe06c6537d45732d5fda1fa83ec2f732225a6ac5cd2699b3b8f0e83a7be	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_85.npz
null_roles	3b7fec30d4bfc7189ee50e9c6aacb481bdd3d4550b99b5f6fda463e4df2b28e2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_86.npz
null_roles	12c4987835d4a2702a2c09fe8a705f6dbb909ec37f38fd1a1d2508a1e855807d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_87.npz
null_roles	4930241c00826366bba2fe2d9bff7337023cbcf9680a77ba264f4f930fb6268a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_88.npz
null_roles	0d3837a5fed57926e048446d624d4905d9df9890de2291a50cb8613a4edc8f3b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_89.npz
null_roles	4d4ad6d2b0e610ae11caef07805519964b4734f28c195d5522c6b8b8df04b14d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_9.npz
null_roles	8d960d44e1030d8985e70ead1d551b59468dc7f56fb023a92cfbe14c96220109	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_90.npz
null_roles	a8dea2aa1b3be09c52adce3e7552cbbcd10b65e582bf01e17f92a3f459a47767	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_91.npz
null_roles	a8626b6cf0462955ec0e4301220c02e01df4a45c3c93db8fbe4cb5b8e4d72988	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_92.npz
null_roles	3cf82df5a762e613eacb9fe5155f1c063ffbeed9b5abee556291c58a12db4550	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_93.npz
null_roles	aebddeb2acf847df22f921268862f7b1af1ac04816cb4970de6fd747c3e52a4d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_94.npz
null_roles	5f393db561771957c2bd974601863111877febea857069d2bf59e36dcb5724c0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_95.npz
null_roles	a3dfb0be483947ce70628d4619ae0ed71539e06bacfc613b537f88e6d229bf7b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_96.npz
null_roles	1e85d00721572600113c9ed86a624aaa26ef468da661f1039466026ed589cac2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_97.npz
null_roles	8076c301c6c24646dc6c31488c604876cb3fc882b7a35ccff384cf376e34b201	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_98.npz
null_roles	2b435c56bbec44cd09e7f115f5ed90183a8ed1b8abecfeb91287d9614182288c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Flux_99.npz
null_roles	f72664fb57ab2c43fc1c012c1498b6ead1ae3505be2f9981b16f199738b10dac	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrAbs_N_0.npz
null_roles	5535543e241180e238b02c6294cc0ea0d30f11ddcc40802e949f66400b35acf6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrAbs_N_1.npz
null_roles	2ab8c7fa0f67ff3d03036a595ebc56886a0672ac71a0c02e46f0eb93250ab1b1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrAbs_pi_0.npz
null_roles	553b2fd1b65fddc77f57eb61ec27ee7f019e6bd5b17b45de9dbcad7ddb6d0e64	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrAbs_pi_1.npz
null_roles	bcdb4474b6b9dc9263dba168c4201e20a7f347a6d66226349eef66c0999fccc2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrCEx_N_0.npz
null_roles	277564da0f25dd2d571f2ba60636e897181e73f5f208a92fce6eddb542016844	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrCEx_N_1.npz
null_roles	f5690517c3eb2550f1a44afa288945b447f96904eb175aef2f28f2a0f752d8f0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrCEx_pi_0.npz
null_roles	a7d5a5a1c5c6e17647ee2e79f755ed890ae9487fdef9993e28fda71f1961eda4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrCEx_pi_1.npz
null_roles	9f246cb064f1d947872d3c4f2b80184d2ea3bb9135832130747e439062bd8a4d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrElas_N_0.npz
null_roles	f69da47ecbd85e21ac579dafba5e6ab0ec3f27d340db46acb7a3f9a6092e0c29	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrElas_N_1.npz
null_roles	3b06204811a8c2229a912f2bc4c2d10fc298f552cc9f3c79947a2d4cb134c20e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrElas_pi_0.npz
null_roles	72f795b6d247e8d9abf0dd165e6a65660c91c9a886643686e90e705cb75098ca	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrElas_pi_1.npz
null_roles	dd00eb7cab9c70212c7671040fb98c27f75d2be8bd66935ddc4e651c43306126	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrInel_N_0.npz
null_roles	06808b947372e9d7a2b21514c6e7e8701aa6643bb581b5b96d0de2c811b1c929	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrInel_N_1.npz
null_roles	0b1f39a49b9a65e6bbab117110f058f124abf1a79b03685227da3b0aca7465dc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrPiProd_N_0.npz
null_roles	6199461d4ce7aeebbe7ba41e156e34d02cfc36be28de262f760bbefd01bb5bca	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrPiProd_N_1.npz
null_roles	f2d1b82ca21f4973de10aa01d5299b8a2c538946eb9171c63c1e6c5d13327dc1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrPiProd_pi_0.npz
null_roles	3f485498c458e2db75e0f47d23ef50e5a18501b6621fb188d47f23e0be46774b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_FrPiProd_pi_1.npz
null_roles	2adbc4bc25f93fab6b6d198517080cd109187f876ebbd2ccc717098cd2db86ef	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_GEANT_Neutron_0.npz
null_roles	0230a4020d6b88b4f8b69718f8e27ec3373cf50d3fa4afe9856855f3df46e16f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_GEANT_Neutron_1.npz
null_roles	082b461f2a7002cb2c478ae0867707b0cd8fb60b1eb689ecda3df6fcf6e43272	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_GEANT_Pion_0.npz
null_roles	92c55b414548976b184177b187f6b3703c164cb7951518278782a081b02951fa	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_GEANT_Pion_1.npz
null_roles	efdb9dd5ebb34e34731370ef003d4c16590acf0abdb1dae209afa66412ada24e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_GEANT_Proton_0.npz
null_roles	163692f3967f56b687e07e3b1bb917f538ba4bf0eb2b65af4b9ff0592764a71a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_GEANT_Proton_1.npz
null_roles	877bcf3307fdc205154975f2f69d4915a8d7d02655f387ef3ec2bd38424d8071	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_HighQ2_0.npz
null_roles	3c17441d2f5d3fa1d135c0c7c2e0d081a3078a4c74ad6a62cbbc3d474d27324d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_HighQ2_1.npz
null_roles	b481886ed0be361bcbd55ae3a67e0f30c9af74c9a1031b95c104d4013ee42efe	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_LowQ2_0.npz
null_roles	ca95868b041a329d798340b4f70ad88317a58bccd0989a70150365785e4f2773	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_LowQ2_1.npz
null_roles	740276b3f3d03740be6de83d63eccc304c0f250cbe3e2fe547ca184e0e7ab3cb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MFP_N_0.npz
null_roles	a512eef9f38d51d9de89b9b55b165300999bd06d771895072e2327b1d226189f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MFP_N_1.npz
null_roles	9e651f4399e6f9970265bdf1bf1322d3bdfae8a26654da57ae3a5c29a51921d8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MFP_pi_0.npz
null_roles	d9d806593f42ec22aa53fea1b02735ecc7f529a93b9dbb5b1816ad22d4527fac	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MFP_pi_1.npz
null_roles	be3f4e84ce0d65237122b64762dc33e165fcd961b221de43c10ac93455dbf43a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MaCCQE_0.npz
null_roles	90f75e66c994e724fc8d03e2346e6167cc0815bbf3fb0652af920f7000e8089f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MaCCQE_1.npz
null_roles	705337769f47743a72f2bea4a9dfb71b3d9c77d48ad147afb40c6abc80ae4668	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MaNCEL_0.npz
null_roles	35dd399be86ff53bd8dc63826d5cf698499135a456de373502c519c658d02a00	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MaNCEL_1.npz
null_roles	e3cc8265783418a8c035c9b8e88497d70f46b46667c1de56631f872dd3186daa	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MaRES_0.npz
null_roles	716eed8bd37f36994289b209ecbb6ae188cc980f2c53549ed753753b64a5f2ad	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MaRES_1.npz
null_roles	abad8c4709752cc4233c629447c819220a87b5e4fb8bf78fdb442e8c6839bf12	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MinosEfficiency_0.npz
null_roles	5479836c7323f099afbb9f5194dab71615f494873c924e07730d451d1420659b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MinosEfficiency_1.npz
null_roles	8886b056783a9af9904496d40e2caa8674493ea04ad3569c411a5a9da31d9149	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MvRES_0.npz
null_roles	e6c9b3c36a0b06c53dc7d67053bf59ff2367fad715f0379d4d16c66b9f98af72	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_MvRES_1.npz
null_roles	4aa4b60338fe893832436bdb2b18c848d76d51c41c18967393d325a2739f62cf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_NormDISCC_0.npz
null_roles	8f6b931a95b9e7d6f00ee36022f9a5e07e29cb1526429d67309a9dbdde99e726	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_NormDISCC_1.npz
null_roles	f2a5fdb5a82013d1f55fe778c9b22037fac25e0bc80402720962815f12024a53	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_NormNCRES_0.npz
null_roles	6b86655c118a19775fc42254b5e0c11b31fe32859c1166db90d8ec6ab8cdda03	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_NormNCRES_1.npz
null_roles	4e574b2bd0d3a87cad6e676c3c5868956a1c1f3cca4780eb19225bc0bc0f8d4c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_RDecBR1gamma_0.npz
null_roles	8bed931f0f11c5be63137672e917f840de93e52124dc6f152a7101539bd755ec	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_RDecBR1gamma_1.npz
null_roles	22e3bba46d7c3cbe6d01e7d257ae32c25b2e267fec50dcc5c15f85f2970205a0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Rvn1pi_0.npz
null_roles	1c26e27ac9f7c4f83c991d78832e8919907be14855174880e435ff3fa0ad4357	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Rvn1pi_1.npz
null_roles	59ec45b2cdc6517f2fc325f36b70cc58d697ef803a88d59545ce965d509c9e46	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Rvn2pi_0.npz
null_roles	565969db2afbd5fdf4d10573b220a163225592f7e4fb111c865c2f6c3a00c896	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Rvn2pi_1.npz
null_roles	f3768fe76ed0e5ebe8ef93aa1fd9be9ab0ee5c779ba9e2233ddb0971e44071b9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Rvp2pi_0.npz
null_roles	853f74f856d9b2824412b1f8c6c20457dca50900f553e55331dcf461da3cb365	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Rvp2pi_1.npz
null_roles	29ffe6d76ca8c4af4df68ac6c296e84510195478b19ed696c32a40da1bf60bf4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Theta_Delta2Npi_0.npz
null_roles	a9cc91ae921166f567083725a77d6b1c678ce617fb1327fa642ed04d48379ed3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_Theta_Delta2Npi_1.npz
null_roles	72fcc448a47631b7070585f705904b586bfe05f54fd8f65f97c5b2b85b179db9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_VecFFCCQEshape_0.npz
null_roles	1ee568dca9598712da022d6520d889e59a5e513e6d4440f306f3940a151120be	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_block_VecFFCCQEshape_1.npz
null_roles	556e01f1ab81ed131b810920c7a7463349cf4e356ee1259d49249b60d12f8035	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_central_T.npz
null_roles	aa9c0450f6bbf440aedf94aebe76917c00cd38900a0f9402c65483c0498e1a40	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_seed_T.npz
null_roles	3f62f50cead2a8ed4c6a1fed37d79ca17b49bb1d4a66c0a8e9245bd15428eff2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_1.npz
null_roles	49a3440348ddd977b0beff94ea460fe3f86a231ecdc6a7da653ad168f2963a3d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_10.npz
null_roles	e0f23fb625fb675b2c5e7713f99d229c17a9ead8682cefe5e2a35ea5117fb307	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_11.npz
null_roles	6c7b7bd916ad9d4e357c8c9a98a8e323dc0d0789cd1e02ae3a5df405dac480ce	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_12.npz
null_roles	ec7a5d3089bbc0f5139bf578ea159d0b03a87ce8aa367e0e8079238b83c1834c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_13.npz
null_roles	6649b38d6365aa231022c1136a6f78e9ad1526096225911facd1fa443673270b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_14.npz
null_roles	8c45d95b09c9e677838ddedc2de122302ba3a91badaf669dac254e59a2ffb393	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_15.npz
null_roles	098acec6186cc6630982485f9985fd030cb520e1d85337c0cc740f4c97132922	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_16.npz
null_roles	568733b3c10153421174aba45f68c81a8b18f01d9540f008be8866d2af15ab15	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_17.npz
null_roles	2e3ae1716697df86e03e098ca9432d490a4223db8fbbef6d3640bcb16ef6326e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_18.npz
null_roles	994e79c17a067c82385e9e233ece3b7707d86d373a7476a91f59a89a37e1d613	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_19.npz
null_roles	167792924ccc9dc66438dfc0b1dc6c55a233e98c716ea7ccc16ce85248b67f6c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_2.npz
null_roles	e4219d525e537fbca41a44ae15f9c8e6365fea93a3f3711b10cab37dae0a15b3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_20.npz
null_roles	38ffb70e3e45752d2426f5d3f324741e82b92a537c432af4ee652abe4665d206	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_21.npz
null_roles	287f5703b9b775e04cac838fc25f809f43dd630161b46a78adfa1bae85d478cb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_22.npz
null_roles	03cbea2aa8aaa471cb0f7f69cb98075b42c2dbc5367d07e551ef1e327c261080	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_23.npz
null_roles	af0d038f3918417317b3673ae65eac6194a26013d0b9215bdf1f3774eba40137	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_24.npz
null_roles	238f83569f38a1870963bcfc591946a2aa5bf5cfb4c7d6dbbe72f421fef430c8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_25.npz
null_roles	6fb8f9105cb6f690f2fb255c6e0806ab96ad8d8d8ef865ca71517b68c0907fc1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_26.npz
null_roles	d15cefe648cabd4d6618f97506268a212be581b4b875b3c621fb740de199e711	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_27.npz
null_roles	c9dc4a229e4e7983bcfc2b1fd251e8120cc416815362d21183f7bbc1e5f6ba12	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_28.npz
null_roles	abf31e0ca8783ffbdf4a2aa869c4ca59693368e62a48353d8fb55988701a28b9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_29.npz
null_roles	53371f5215368d40498b01556ac8ae839b4155b8d74291b3ad31e8683c14b954	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_3.npz
null_roles	ef1d25fc5aa9248dbcb0464a60760fbee0a35358932e5a1c574d6bd828e8cfd7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_30.npz
null_roles	49b4317ee652ea0a28a81eb677a969522567a319e84acb36ebacc1625399076a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_31.npz
null_roles	fea7f568561790abcb7081d891e84cf6e38af2da14678a620f093f86c951a6af	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_32.npz
null_roles	7387fb6046ff288e57bc67157865c2ee74f1d6655669fae732813a432bcade36	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_33.npz
null_roles	eb78ea3aa3b976ebca9bc51acbbd9a1e7f24334849eac40aa271ed179e7aa2ba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_34.npz
null_roles	d6afdfd94a537813bd20e74ec3b0af48653efdb6b7594ee9712b2f7714fdb218	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_35.npz
null_roles	ccca71ed53b2e08e106d291b1be4231ed8fb3ffa683245a583539e3b06e6ee33	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_36.npz
null_roles	5e1cfca7e837fc29885fe42576819fcc545cf553fde5c1fb83f14f9d5e6a1846	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_37.npz
null_roles	d44bc7967fcb26cf16723a580da527b4fbd10aef6255d7c2d34a453ec4a5ae36	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_38.npz
null_roles	94ed03f4de8eed656aad553888e446a8db3f6a1950f03bc9aa7bb1cde2a4c4bf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_39.npz
null_roles	251a7c95039f0c98530e18f1e6eef59c2f7355c1e4d5ad2ac9f4fa8b98b3462d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_4.npz
null_roles	d260e5c372a8799d95d922fdb51324370133ca83fe7c7cec34f45ebf4bf38aee	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_40.npz
null_roles	351af54f552095d5fac22af96a052baf4409a860a8bdfbdc13144dfde80820dc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_41.npz
null_roles	ffb2c8b0c300a72682065953bc72695937b9f30838c924a17ee4784f648fed92	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_42.npz
null_roles	70cde9f672beab60b85294eb35011c1bb38fce0c02e809a8befd1b88f92f87e6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_43.npz
null_roles	a9dc7ef09c23bbc1b278575e84f5c2983089174f80d9451d5d485a083fa2a9ae	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_44.npz
null_roles	1beda7dd0504939e380bd034033fa8151f93d1029974add1cc40650b90e4167c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_45.npz
null_roles	75160521d05e3516c25c25cbabbf2fe4079aa68d81cae3c73d5546735e03a6a6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_46.npz
null_roles	b58d14b24f58f8ec1cf8e5e56fd46a04d30fa767a2b929d7078a44e92cee0dc0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_47.npz
null_roles	b5f0e2e85253ca0c187107185e87c75db6a764698e2b07cada279277715a2770	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_48.npz
null_roles	ffe823be9891a7e3801956eab8181775e7142759e042ad9656f877ccbff6d2d3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_49.npz
null_roles	4524e1f2b53b0a5adaebf4894205d616afd8199f251c5f2828bd656066e552d5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_5.npz
null_roles	e97fa6af8fa637299bbaec0ff5bf8c524a46deedc92805dfe8323df852c667f7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_50.npz
null_roles	a07b63d7cbfabde36840cdfbe8d887986fabe5e2865e4a37bf7d23095f045401	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_6.npz
null_roles	6209c69e74645e72359a86a44ca9359ac4dd2562a7467de78d230fd9f488a54c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_7.npz
null_roles	1599627b2615644b704e6fa069923ddd8184714da6a490b53335bb4dce4cb224	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_8.npz
null_roles	b1d56de003fd99823a621af0878001cfcd422e5be2b7085d97c8558e8e56591e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_stat_9.npz
toys	eb0f69de1b58849193278fb3c9b1cfc7bcd630bdb78b9d080226064c92216d90	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761000.npz
toys	9b75ef9113117d98c7bca0a24958bcbfaa397b8855f7e07193214784e46743ab	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761001.npz
toys	b83ec256b7f7bcecb4a658d1ffabdb0d62e51b6fbd682cc131ff660ac5f4b24b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761002.npz
toys	9023717782be0e84703a3cbdcc588fc1b48902a1a7926c54667f3ef9704ce6b9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761003.npz
toys	91eff598f61c284e5baa265faf3be243bf1514dea08a6c07c73c5c2582848d6e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761004.npz
toys	ad01b2daed696742b2081d2241d2994c19771f478fbcb4755eff1446ec5080f4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761005.npz
toys	07c889e4f612a024dc349b7be528f88701dba1f3b3518d9d5e8c87057e91238a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761006.npz
toys	c25f1fa40bf72c43aa3e9be39dda03f617a4bfb18646a79317b46fe3589236bf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761007.npz
toys	1a5f622149109ddd745e1d89991c7ac9bd29ca2e1f5ad4241ed82540a358d6f1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761008.npz
toys	9331aa6b3d168456d0885c9b12d88344b4c8b22e99b6f1925dddb0580505ddc8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761009.npz
toys	5696fd0e85ea8f3b1b3c0a7eec0020a5f4f5a9bd5384587eb7f505ce031ccf89	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761010.npz
toys	31bd1dcbec2ff36aad92e891a02decf29a162a2f8771481dc4eefc7ebaa44951	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761011.npz
toys	600a52c17d617d40fd1f287b05093d43caf1e3923da167d2eb4c923ee1e54f69	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761012.npz
toys	b1d002a202f4ed400a866ea1831926c3ac4eef86e86e3be5d023585fcc18cbdc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761013.npz
toys	6a40f87ee5cbe852e9a39178f165849a2583af5c894b04f22b2fc2ee75a829bc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761014.npz
toys	e3abf864f3744c5b43f1c59c7121ed6c88b295fbd20f6052fabc786d0f2b57af	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761015.npz
toys	0cc33171e59f31aa9809d77fde428d74476a391413d4e635fd47e4c9d4813264	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761016.npz
toys	39ee235151bcb6f22bcc4d0c6f402a926995a74a61f5089fc3720f0d8f8ae542	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761017.npz
toys	56244b58fc0542ddc1c4a1a24b61db73d8183280f4a0d20ef9dd460ffbb7e692	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761018.npz
toys	9f3ab6ff5f1e89e1802c57c0a72ea39b9c636933e3b39b217a11aa5ffaba304f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761019.npz
toys	2fa44bafadc4f4ada545a0f8fe254a3c624c9787b9005f1b1d36d66b31185c84	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761020.npz
toys	9253871ae0950e2b49f40539c815dbacf9802d00d4e4692d8503302804c5e904	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761021.npz
toys	94606c63cf78ab71cc9b850687a767a94dfad677bac0ba087ff354ccf171bf25	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761022.npz
toys	696de9fdfa5c85e78a0706179d2c2e46691ba5c1fd5549ba882df5ab00c56d98	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761023.npz
toys	c58d45ede578e5086ed516cfa88ebb8f410f099fc9723698d294d46123af7180	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761024.npz
toys	0ef38ce4eac399ccd437f2b47f20b9c2d61a1054c209a3cb2636b044f81fac6d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761025.npz
toys	23eb4091f734fb347050468a7e44ad8ea2d4ca0f651cd6c6bbfd10ac549a99c7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761026.npz
toys	69438b9fa3989deedb13e2f7ef2e3db6bb01baa410f07ea3027332e389694cd0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761027.npz
toys	de9b35847e7f679bb0be50bed860ef2d6fc755fdd46e5969063d8bc6c62c4dda	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761028.npz
toys	45c9b5bd34a84cdd8688ac89910182b185aeaeb65f948faaedb60dac476ff132	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761029.npz
toys	c4c911191102f4adb55df023cdb137c15f2ad13d3e9cae3aac1168209bfa58e1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761030.npz
toys	295f36684a0e3215c551aaf3a8adc261b48c6e5124a23ec23fdfeebb2ce99185	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761031.npz
toys	46da7e3a4ae2a23796851fc4fec17a89b1684b086adf10432759880196eca607	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761032.npz
toys	74571fb50f66c4ee2a65f9272c2c7a32bcbd2a97d48946f24bc28af36a0b746f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761033.npz
toys	823afaac72a34825b6699f2f2051d5e24edf9069c7c6ab49b738945d29f18a1f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761034.npz
toys	78afbafd1ba0ce1147b7fe3f598033be3dc292a6dbceb0e848b538263d19110b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761035.npz
toys	3c972948fb310edca94f5bba74339ca4f7a530a6d8b16d9cc3257f0c6b282a3d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761036.npz
toys	ac01e3284a77d185f92099657b708647f8e713d430458c64b576666c4b3165b7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761037.npz
toys	09df682d1a28d41a896bea926d796acfbe3bbc1eb908f9cfc00d8f610b4c7f18	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761038.npz
toys	d8a605b6685230de99731645beee1a6e6d136fd65e1b7306d883a0f52035f2b8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761039.npz
toys	ad5de47aff4048089fc041fae2f7fb7d70e2242e10dc01718e80ca6c941f5816	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761040.npz
toys	2b5a6dc39e35f019dc3b844168c48e1b80b13e5826021fff59a547a52a3b2b38	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761041.npz
toys	234a66ef58915345b3af8c840cb29a46af2b5adfbe6dd9852ae7d267d66c8262	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761042.npz
toys	d6b0427cca04603794e0f1c2716e960a3f2d1181cafb16f1a873eaed60da280f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761043.npz
toys	700aaf1ef7cfeffe04dcedf5f9a8b05be7d2c5848ab2ab4cbd1524d0365535df	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761044.npz
toys	6170811e253095ce215ae3b2aafc68e41f709cd60f3879a872b1aa9809fc3946	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761045.npz
toys	50953f7e7a265c1c85d80611bcefe482e8a9ceb32e665c0717eb604c9179b840	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761046.npz
toys	94b68ef165891c0eddc48577aa04d82b384055956f91faad53471349a297a6a0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761047.npz
toys	0e77ef820c9f273e33fa272a247d652c1890f2e5b3c52e1cac9298f6f4e5bf76	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761048.npz
toys	a96217c3f095f8abf8dce77094973d3ec48511b27931fa24a53ea481fc954a4f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761049.npz
toys	23211fb905aa2af90302c97b00aed5b6ae95031c2dbe325f16feca6ad7153a1c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761050.npz
toys	9f08a57fa0bd36eb1b6c9291562d3fecddedef21e49ffa908ecde1a0a3a3f824	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761051.npz
toys	3b45bdc1ac0a25ec68c0ef930dbc535092ee599570cd46cbff3bc1e1abd66f95	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761052.npz
toys	918f2fad9f939d3f7bb9e50c41b0957b86f3b79f6090c52bc1eff3dc1e1952bb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761053.npz
toys	aa4dcb3fd3ad4340464aa55103f7a4b25ab71e30aeb312a1fe1af4a8f22d45fe	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761054.npz
toys	27ac217ea7eedf4db4ec3508486b78f01c27ac173dcb00bbbfd548fe4d98ddf5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761055.npz
toys	93630d38656dfce8922916a9db6410951ad8c9fc07cfa13bd988e59f31db7662	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761056.npz
toys	1f604c213060efa2186e71ef009f6d693c080214135b8b13967ca424256f2ed4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761057.npz
toys	ccea153175cd0cc85a93dd035869ac3627aea57112426e70bfdaf03e39097482	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761058.npz
toys	bec429c68126515ddc2d7b648c84e8b3ad2fd479b31b88d2df17827da83e80ab	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761059.npz
toys	a6c926f94452e185b5539f4b42bb883405daf04524a1fe0873ff6e5bb23f9379	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761060.npz
toys	8e95059ccabfb736f090816c9ecfa5b064b7a6b132c13ed7d816e4dedba9ed0a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761061.npz
toys	78d7d780c3f9db9e5086c23c251fbfad3ea67ce1c724840f9d1964201810386b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761062.npz
toys	4836c9a5b50d448163e735786fab5cd237824ca18e9cb01ffaa7c3aaa7ddde5a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761063.npz
toys	ab5e080488df4cbafbf32dbcb60e2cd413d2171a3c481a7c778e5192a0399ea0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761064.npz
toys	08e2bb6311331ec40f90b12954a7e9daa61785c92355838e847a2034ebad8c2c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761065.npz
toys	086c6f9230b0501abf1d9cab546f97f11e62da48c2fb6b8378bbdb61e80aeb66	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761066.npz
toys	3858780dacf25ddb87460493532f9e1177d4d7d2c141b5d89dc90529b9d6dcb0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761067.npz
toys	d0c4122925c377e0268bed45245acaf8cbc4b9ee6a04e64007e0386cdb38e28a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761068.npz
toys	ef6dd1ac5343b980dd9058fbade20bb9875446fda5adbcdda9f07ba86d28fd4a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761069.npz
toys	55e92d954cfb7390f9f05f7e0e43ad4ad70602c7c28435d78328888521ec68a4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761070.npz
toys	34aa7dee75e73f90b33687af05cd8d5d710d5cc0ae17495ec0f1791dcce96c7a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761071.npz
toys	3c13f60b2e82a5b5b9f0bfd030da80613618cc9cbcc38ad8063fb6323ab8dca2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761072.npz
toys	3a7b8d8b1b65cb0f69c827fb398049750678c40c57499deac8c0938f693552ce	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761073.npz
toys	82173c0d81b5c06864fb5d603f18eceb78e4607a85df4f1f1801cb81ad5e71a8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761074.npz
toys	95c180f4015b608b92c496644b45eb3b5afc7d90964a12ed1376cbe4a215aa66	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761075.npz
toys	c83297e026c56d5350e5e0cdc59c79fd1cbada312e74cc5a767ed9615c48bcb8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761076.npz
toys	c4a4132942e5815122e9a3b2605d559aa010425295ff07e942f671ae5146943b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761077.npz
toys	3c3911a3e3e93330504b8a89e5c3d08b861dbc2e9e9a9d437d99fb4136207684	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761078.npz
toys	27c42c6a93e5cb06add87dadcad0f2b64f99edb027e33d14a4fcdd449bd2a7f3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761079.npz
toys	a637de73f300ddb5c839be59f17bcae1bfcf4a775deec9f8dc1323027d5d4cfe	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761080.npz
toys	17ea1ec59eeafd6137f278cc1bed72111e5d733e1321a4670ca1ef90eb7e3482	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761081.npz
toys	3a647fbdb41e395deec84f02b84029aae847d6d12161d9a1086a04c9669ae210	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761082.npz
toys	90a1218ad5ea2d2091bc350a907539ddc4b43b1d194314b9e21b35ab7df2b2d5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761083.npz
toys	1260131eb0e8acd0a19748bf6f40a0a637efa836314ab6c6ef80ca6ab94661cd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761084.npz
toys	15e5292c9127f5b05a0c2424c08abdb7e9d8b9c4eceb317f827a0fe2374874e7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761085.npz
toys	e07f8ed2d98eba4ce0b2dcc1455554509d3394073929afc5fae1d6d71517ee8e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761086.npz
toys	fdd37515ac6065d2ad14d45a98380f5f086d1028a4a468ef07cb86866b5090c9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761087.npz
toys	59426721c4d46e0de1aa1f2f2ded1e447609a84db6f84ed40e11241c0f15eeee	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761088.npz
toys	1637cde9650d3eb3d447d3812a8e9a0c3f2d5783f8b08c9a4574cd7506e8af11	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761089.npz
toys	af051f55c3ce3e68d66fbfeaf5230e86dabcdad2443637679ff6fb036d11c99f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761090.npz
toys	28f6ed21a6d8cc5ddf14d58734c33cefb37ba89dc4185f86a86a773d9e741e1f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761091.npz
toys	a3927b05a051cd3653e5a50afa78b2eab10d914bc50eb199077cd1cca8648705	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761092.npz
toys	8ac7cf486b9be9b57ab09cf3926ad5d05288b743b7d4c7297f8dd8b4b3e4a08d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761093.npz
toys	ec631e67a9ff7f75ccee49d71e8d0080e0b11a404d543a771aa29fe1995c840a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761094.npz
toys	abea011ece6b69a38f5ac2bd38caf453b6fbe9c391aa576e3dea553831389c2b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761095.npz
toys	fd76585741a2c06f09606c679bedb68e3c799c2112067307258597c1a9ff1ea1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761096.npz
toys	1e4b11186ba7545cd59528d36a4ff5a602a24ccbd45bc1d0178d28164cdc969a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761097.npz
toys	53d21f402e118b5d0430287825225f211111f52f053830a5534bbd1a2ca8f0d4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761098.npz
toys	fb9f5c1b64512481945f5a8dc6698d3db8347067815bf6db3c2ea1cdd6c974a9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761099.npz
toys	594fd4418cfea38626906ae8bc2a9428e02457b13bf7c315e26166f0c21f37f8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761100.npz
toys	d7b4e971c5a2d0f54eb05a5020f6666553ee934c50425f6d727f112b80d419f2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761101.npz
toys	8a5588aca4825ea9895393068bd4f7e8d38811f8dae8538fb483a82c0465d268	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761102.npz
toys	946124fc9797d5898e3c53273857c0d1ef54f6f820dc99dfc16b76d31a651d28	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761103.npz
toys	88a5c1ecfab6c4e85b8f2413cb9c24f97d42b52d8408f3c81d28c748e5f06124	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761104.npz
toys	ceaf3f1aefd1f6b40fc215f558d79189919e16b3a175556e782d8e8ce1dc8451	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761105.npz
toys	0c60657fba1bfacdf0f2cfdfa5f7e5413bd0c15bc21344b887bcfeb366f89f97	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761106.npz
toys	7cf20e24955817d63881fe1fdb0b47ccde51c7dce360e8586406c39322d28999	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761107.npz
toys	7b8d98be62dd42f652eb262d6e22f988f37e6ddb2f9dd26f69a01cebf117d5ef	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761108.npz
toys	d033b877c95fd138a68f6af235636c3144c6478a8573c32759845879fb85b27f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761109.npz
toys	c8adf1e2a3e91768fc3eb08e940dc8ff883546f335cdaebbb80bed5bb70990e4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761110.npz
toys	cbc90c907d18d8e5f68efb2de9563a94ce8d01658d1f6caafe96b9a87f56844d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761111.npz
toys	43a1abe450d3367fcef85c1211d62175790385816340c89c7d9e013b507d24a9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761112.npz
toys	4196de2511287056d7ebb76c423727ba396b642dab156d7c8d98d3528e411c12	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761113.npz
toys	4aaf2875d046c25bfad9f4d6ea6c7d4594fec74f389c5a51774d8feb3f048493	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761114.npz
toys	213fe39a13ed50bd1c9cf06595cdc3ea3ee08413a6dd1e5bf62e4f4f63be5d66	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761115.npz
toys	7467414ed2155925e950e5270bf88188ed9ff556a956df0986b4f70c570be343	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761116.npz
toys	131749bc62be6593f2ed2957b634484699129f6a95552bd5b0bd3588b342992c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761117.npz
toys	02b2ed46893b9ff7160ea51ae65a7b56b039a16c9ba455e0a556a3fce0bd3021	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761118.npz
toys	987658d3e2fb1961b035e38d98106a8cae786536746126ded42b9b731047abfa	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761119.npz
toys	979cd9217cdd14267e6fde0edac519f67f896c4b569530212cb237050c83667d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761120.npz
toys	d0d76ad1f2831218a52b4b808ff8afdc6f819127a2261156a7b417c2cbb288a1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761121.npz
toys	278a7ae93c586611e7810c9f0cabe613dfab72afd17b0761d5ecbf7d65e532db	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761122.npz
toys	5d116f1cd4100855711c08886cb2c0fde622af464a6aa438c1c6e18b46c31a7e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761123.npz
toys	92e3ea3745cd0143ac1ed2d2adaf48b84f82ae550e0a9fdb356d5da62186da28	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761124.npz
toys	dd429fc75cbac6981cf083d5cd6504b3ffd7ed45d637ea40f65d67ef134d299a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761125.npz
toys	07906584d4e00ff93c0dced8127f826aa7db03852502c9e3aecf4ce089fe9ced	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761126.npz
toys	f75e092606732b0ac1e069f91742ecfe4d1b4a057bb4ee914f899c367c282f3b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761127.npz
toys	0dd486cd11e8f13256895b45ad753e1eacd7c153207ce25dc9ab7a1258d5b03a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761128.npz
toys	c1915a1c82be102bd9fc6d07bb90bbcac0ccb9704a3772b9f24c31b03335c9cf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761129.npz
toys	1315e8ad4983e63de1be45201a296da29975832f48007db7527205a4aa91595c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761130.npz
toys	9f522894a565c06575d48f73734d6095d0d11345ef308d25536a62818c482a04	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761131.npz
toys	c13bcf4198be44ff43d29b91270764c1a591cbe3c8e40c673bf64deec20df2d2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761132.npz
toys	e09104ee389dd791fb295837eb56778b5117c1e4e651c32a8d198853299eb6cd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761133.npz
toys	e75193f0369cb37359961c1f2ba702244ad7f652855d0514ebad704d6d8e4ff8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761134.npz
toys	ff8f3cde82935f2356c81bbc3d3d853946f2e9489255aa0f3a22fa6a5c51a54d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761135.npz
toys	6829813a4675fe1a0b3b72f914d55cffc1d10fc0c739a648deec1d4d71908059	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761136.npz
toys	3d31e74a5b88a3de26d5c6d08c40600d01abd9708e8abb06c1bca31fc5466c83	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761137.npz
toys	eada964b3f515dfdedde2b1eee90db54bda784cb0630806cc25bfd83d09f7116	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761138.npz
toys	189f7333fe55060dad6f3d099016dfe86a4efcebb670b0189ef0b58ca94b0890	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761139.npz
toys	191b0c7a7013d0c200dbea66aea360cd857b25f8fd170976e5d062e33da4721c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761140.npz
toys	1a5540f1c19ac00b38e117d49b4a43576ea5eb14f6d648b1d04e2759214ef4a6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761141.npz
toys	1096bed250f1efbf686263a27d0e89f38fb58f3eff84b4b898eb580c589e0d25	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761142.npz
toys	60c47c29ca1f01735ba69f6c59200a7a1d78a5a7d8acd4fe401829c64bc5dfcc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761143.npz
toys	2aa3d75ba95090a48c5c6561908601ea99d6f3c373ef5f7fbf420bf8860c5398	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761144.npz
toys	0d70287e3456d5ae8fc28db1436d2a35e0b54024053bb249c0340ea592e2822f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761145.npz
toys	00ed801ce7fcdf014f0e27f71e5bdbe0a62668244193f751a19e80857edfe375	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761146.npz
toys	ffb0f833b61a5d1d75abba664a3d06bd133ca41e145d2c2e0bbffaf22075fdfe	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761147.npz
toys	7badfaa26a9608ea047e9b52bb86332927ad414b0c19a2d781912a413dd1da4a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761148.npz
toys	11393d6b1dc01e8c4009013d92dac58518e395883e34bfac2e404252bdaaee5c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761149.npz
toys	721466940942c4079c6cc6131c2412f14c70a34d58f54497c4ee2e015758244c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761150.npz
toys	3d06d04f5652f14bda4bef9f529219e174ca235b6ba2c9515bf9287030e7a8ba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761151.npz
toys	69bb4f3c47082b1750a12040b83bbe5fc4b9a4b2b5c0bc27555c0e7ac5c6776d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761152.npz
toys	9b545ab5358b7e3eb948517af1dfebc7185fe54d418196c2e6dcf5ac166a8919	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761153.npz
toys	2e9e88c335475546537eb0d52e8b74936344a6be2019916dc9fd59f0c54e170d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761154.npz
toys	374d4df698dcd6ce49c79048552becd7f1ccb8912e25a2804b2dcd216becb819	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761155.npz
toys	5474e7ccc344a6ddbae48437fe2ec7d4838696775dc82dd7611ef0a56c61c1ac	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761156.npz
toys	96eba6b43ee5985a674b6b89067728848280c5771149b211a53f2d48c50a5ea0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761157.npz
toys	d6b4d1739b4d4ccc3614a44df66c48911e049e65aaf352c895168a947f88fbee	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761158.npz
toys	9f7c70fd29f28026d1f400e8de1d3ce110aed6d90c0a761fa90985b0db8e4863	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761159.npz
toys	7df33842cf17287e76c368680fb178665b7db8b305ba50961bb5d34f8340b087	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761160.npz
toys	0fef8c3d8716bd459c2f45b7de4837f18afe589e840c13b64ee5348fa5fd5b01	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761161.npz
toys	32851b8f28046eef29c7c6cb9f40b546461efec38d3c8b525ce0a58ed9f4e2b1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761162.npz
toys	533ff5c6e27d12904ec3a424c305f0bac6aad618491fcd2ae3cc9bdd49c6cc6f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761163.npz
toys	0ec402aa7a11314ccd9c1ab3d0f3958847d616095f108a74113ac80fb5025e63	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761164.npz
toys	5469a11232e47709fac394e59bb98393cf8a978cdd64f6b684e4584a38fc3bd6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761165.npz
toys	c7222ece57d1d26ae07997d5b184a8f1fcc1b066a806516a606defe6ff0cb153	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761166.npz
toys	7626ef3ca224181636ee2ff0a310458ec227705e31c3d771e4df011fc97cba8a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761167.npz
toys	aa6717f5678d1f0e037cb9e7378a49f7c643fa1a1c8b56ddc537e9457dd508c4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761168.npz
toys	9dd7f3eef67b6f6c605a9fd935421845f3362bc2cfcdc2a1cc71d0c8dd781007	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761169.npz
toys	ee3a4fec997efebea471eb6fb3161aae00dff2d996a1d43470a97d4f5fcda83a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761170.npz
toys	0a4221247e6dc19896d0f5a20bb619ac01f405a02cb6b3a9cadd2e068696ab72	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761171.npz
toys	b37eac637515139f9d8abd04d4bf6a550d69fe4b43af0db68885742276acac05	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761172.npz
toys	187b65d20237f9f868619461b6ccc16f8a3190f022f6c7f16c79b2ca422b37e1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761173.npz
toys	b0e45a686300c83baa518976c35701668050fabc59f67398db096942249a907b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761174.npz
toys	62996c0134e11f908242f368e9f016136075e8ae133290ba5c969295b4a8ecec	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761175.npz
toys	688296e1d4a3fb96dac08668a5027dd7430d33a03416fde34721362d6508b450	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761176.npz
toys	fc4cf7fc3d4eae3296ee924c37d372d81db5ffb623bd0707953b48607efedc33	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761177.npz
toys	5ed70c25ecb5be2b9603dce77c089206a9746d4da3535d087a452695fb064f8b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761178.npz
toys	af5d5a2ab342021467931c1704594a2da6f1ee9f8bdad966598aee5ca13eca77	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761179.npz
toys	ad06717f2035494b90301d85b429d3919fc316d3842b9444e59d2024e0a95109	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761180.npz
toys	4b12a8d45e8fb36d9b6216831909b8e2e7d1ba40a0e89dd3afe63e3b554038fc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761181.npz
toys	761fdf62b1911cc8302f2ff42307dc7e6c16b18f6a08d8e806baf819caf680b9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761182.npz
toys	9e9ade490f62d8ab1b118b69559e5cc37e97d8f9d0e2cb1e112dfc8b8400b42a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761183.npz
toys	ac6e232b763a2f0a42d578469bacb8334740ccea4ccff1cc7593fde6723ece09	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761184.npz
toys	8cfd27708aa0a672116d0bae9fe311dc4301847ecef084045032f19af00c8afd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761185.npz
toys	08f7b3ae58203f2c0168601a00b1fb2db52f10ef3d36548163abcd95b495da64	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761186.npz
toys	b34068ca26287500aeccbc18fd346a980b343291aec626698698097ec288819b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761187.npz
toys	0b98854b472ae3631e88afa988c36c64d83f5b94c9b0f33dc3cc9f6aebff2120	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761188.npz
toys	198e80a86112b22db32426187db22dcecfb46d7433fea31e9539a05db12a0662	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761189.npz
toys	2aefc53379c3c69c311ecd5fcaea94da423a3ee3ff29b3fa3d6903f8e227845d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761190.npz
toys	e69d1b87549d6a1668ad1ebafce8ccc9cc09f749ffbcf69689da2de6b2017536	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761191.npz
toys	c8528614e997f432f82824e00bf40cf8990ef19b17260ff873f514dfb7763062	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761192.npz
toys	13cfd88452a115d71395b0937590eebad0d72aba87b9c3abbeec8ea3affaaf25	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761193.npz
toys	c963cb3e0d8f6f812066366dd888e395d60b4be4634503f15e654d35d01e2277	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761194.npz
toys	ba3741852c01849c467f220b1dd3b6ccfa5f371560685d307505b9ad998994f7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761195.npz
toys	c685ef171e62b6fdad8bde1c77fcdf4e53a10222ce233af4734ef7e2979bf45b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761196.npz
toys	353f1d128656ba3b066a4127148802b2d85a958442f889d1ab1d3e022f961ee3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761197.npz
toys	43c8c70c4a5b7bc54f13da0b4fa627e9440703a106e9b58a92ee5328a88a447d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761198.npz
toys	2e38ce0310c8bc24b5482bdba4327e21d84171a04fc05f5d5332a1d8c54f7514	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761199.npz
toys	fc13a196913d2df89c18206adc42aaae176da4e537d032b2d62105e25a73cb6f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761200.npz
toys	8c5d9c5d097b29a089798969dfbab1c214af2e0f91fb77d3f828573917742923	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761201.npz
toys	074ff1fb4cc7c3aafa5c2e22cee9f6b02ab3d195ee7978530d2c00431b9d30fb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761202.npz
toys	93e3d76a7ee84e86684c2d6b1dbc2bc26098f74f2cc5c518e3fb36842f2de553	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761203.npz
toys	40655aa5d76fb7c6e0b723b18c892b40f267a70b6d8be7d4afecf0bccb7dfe2f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761204.npz
toys	ad526ee0f63a0dddf37d4d4efc346e0d5c1bb2af6b299e5049818e003c107e66	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761205.npz
toys	07563fabe254838cebf75408b2b63381f8b1e191487ef5aca087b5bb6dd39fd0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761206.npz
toys	a23b1f3b14cd1d5b2019975e85cfe239377820ce7c986bbc2c21dfb9337f6bf1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761207.npz
toys	e621f6dcaf2a3001370e0d743ade7001fe483e90afbd6a078879cbfc348550f5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761208.npz
toys	2f03dceab528af3370879d195ce98c72c01d8c7661dc2fe4b59695f7335eae53	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761209.npz
toys	83a49efd65360067b7b7861b930165cc7e5b122f39e3dd534fd1034d68625d2a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761210.npz
toys	c93523bc1f134f208c727c09745ca2a43fe643d6e20e2cdf081be5dae88d4814	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761211.npz
toys	3e3d54bc6a1818124327c376397aaa850db8dc9936a02ecf9a68207524f4fbea	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761212.npz
toys	4383d31db02252b2214bf58cbf3ff340f22442ad11211f5b87ca310145fca516	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761213.npz
toys	f776b6d166cdeec678ec05343a17d0e97f7f71b2d67705600a98919c1c1f7355	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761214.npz
toys	acb4bc66843eea1a3158340db8525637f630bd36a23898fe8ee0440e476b6e10	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761215.npz
toys	a1fb7e2a018247ecf75d90cd09e6a2e2875eb70ceddec9b379cfa9cb62575769	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761216.npz
toys	daba62bb09d2f983ca9af920cb52c805c311291f9862b6092f9d4d97a3b7d4e6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761217.npz
toys	594547150d90e3751c2dafffb38474cb33bd10de38bc995f1c4cbb87a4f35456	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761218.npz
toys	40059639b47c664a67ccbaa766f3b4985389a296c9c403883deb06354e7381df	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761219.npz
toys	fec53b21c6c999bc4928b05dae9743f5f0f301279b0ad8718d9669fdd421c781	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761220.npz
toys	3ac980f37d0a996bec89151cd6421898f1a38a81b7b83cf577b79f2cfe43694e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761221.npz
toys	1bb40c16f9ea7e3cfbe74405901ae9c2ae8ef6365ef5017735510288be18a699	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761222.npz
toys	8296fe63f682347a926d5bfd5762705095eafbffcc9de6bb6702ce54190f10e1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761223.npz
toys	ef785b2395ba2d4f9907616e81a25897a3189b6027605cfdca2817aab5fcca80	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761224.npz
toys	218ca71615f49b06eb914131457036be14e692c71cb935dfae2c49b6a01df3f9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761225.npz
toys	1e6e07d734ef3afe53afdd5435f2bbc79a400426fd367119c62fddaef368e2cb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761226.npz
toys	f1f3ba5db5d8a59282aefc249e1557307d99fb9568b73da75d594e46f40911b3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761227.npz
toys	6f1230b14f33a2457b2490963a2ab535173694d575b5b7703be0923aa1d30daa	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761228.npz
toys	d41e6ac8895ea99df6468566a791522fb2733c0406fb74c538957381b0c1790d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761229.npz
toys	c16dd5d1607c01c8daea13bec24cc4903a0fa39940affc890c27ba89fa7103eb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761230.npz
toys	e276b6b21d15f197e5418fcecefd5bbfe0bac7c9e8e4854b7311c17a046defd3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761231.npz
toys	790434ccbee91d98a54eda8f44702c9569fe0d7fc672f8afcd9937087bab1627	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761232.npz
toys	f6abe5bf4da82d12030da7ca26d19e3f6fd1f789bb979b846c8eeafbd61f5c44	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761233.npz
toys	116d83edf4f2cfdd67ecbca0a3aac2106d16443d38cd1e2a2ca45d2d4a36e574	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761234.npz
toys	a46e397ede7aee959ae08f326b50ee3613f1bba2a0145ead90a3330370b07873	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761235.npz
toys	4cc8cbba696d7ce2b19f46846778064f9cb5fcdd8307fad3b242f613c87707b0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761236.npz
toys	4815edbb4e40717c009baf441db33a4875e1a1c6100bc50ee5589b9f8bd34798	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761237.npz
toys	6ae1fcf27227844aa3e68b1cc8386411407863a757a9ee6a003d25e77cdad4fd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761238.npz
toys	b9e1b6a10e51c2ae69cbd9f2e56abb3ddc1092d92973ef4de3264baa752489f4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761239.npz
toys	d372a9f1da195cb33109f5c881f80bfc3673db5f19a4424b2eeb3dda307db8ca	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761240.npz
toys	3d8133f73c7e4e320c26f3573dbd3f08088e8a6da4728837bcfc23a8b0457d32	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761241.npz
toys	a20e049f313442197fdd20d4c5cd60fce2a314dfb62f83ee55c04e083802361d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761242.npz
toys	0d832a57952e9b124ad77d17282c8577457bab3baba5523e4352631f619ad747	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761243.npz
toys	b64aae3b7ef0a95df9c9ac4fd20bda01895fb8580b63fea78ffdc9abea3c1dd4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761244.npz
toys	1cc59b8613857436e244440b83cc40d708829dd0fa368ed1aa83e89317d2b02b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761245.npz
toys	112cfd34240bd81aef284a4af7967ed3eefbc757d1fbea110b863237780d8db7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761246.npz
toys	0993bc1f90119e33aa59eb0979cb9a00eecba969102350321352f54202041431	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761247.npz
toys	ed5357ff32953df493e330daa7d4613ed33cb533aa13e1e8fec72ffc64458da3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761248.npz
toys	72f0c356ed9105e2aebbfa9df370aadaeb34ead91fed2267a480d942d699a2ee	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761249.npz
toys	fe8618e662377ecb878e9c9cf7db8bf989c68248f1d5d51d7a6597027d9fe54d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761250.npz
toys	ac5e41b4592d211163d1d383c730e75b75b58da7ba93080e877ca6710fb4e152	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761251.npz
toys	e7db019de78c5a6234681704c9d72cf3b080ce9d1afc3287b6f1bcab4cfe5fa5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761252.npz
toys	8eaaf422ab32f8a10345aefd41be2122712b1220bb2b8271c5225d78d9fdca7f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761253.npz
toys	2404a9e61f4399c1580e595399009a54742c9333538b4e99ad4dec0eceb1ad5e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761254.npz
toys	dc300a8197aa2a8f4aa9782b8c79bd6582924f9277f2ce9edfe8458904b21293	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761255.npz
toys	bcb4939badbb2679595cda60ea53a94a24327ee3643c7c7af70e002b7a7843b5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761256.npz
toys	a1518a121f5551ea1d92287260e3b296abfd7942d8eb6d8195fd8388672918e3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761257.npz
toys	f5e92a7815850c37b7988e5f2a4b81d40ea84b94cd2f8be7bef311f78cbfea47	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761258.npz
toys	865511d63c8adc2b096ec47c0ff01d4926701a0a0a362aef7c842f1740b42808	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761259.npz
toys	5a5737984db8ea67756c013f54e973e1c7c4fffee8102129ba67f663085bf044	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761260.npz
toys	5d4d92f460e377e92bdb9cc88579575b910a6ab2741c50cf4938cb0fdf9b14af	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761261.npz
toys	40d823a2a2c5dda9ed1c7b08787325be70f86a62783788a816b9da5ac5d558ef	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761262.npz
toys	b60ecef64496932881ea8567c9019cb1c1ff25da46b7d5317995dc4ac845359e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761263.npz
toys	392bfe3a7f7708def1043a67f9ac3bed12d8e2b9a0a3ba6fbcf191f868568d6b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761264.npz
toys	19b03a10a5ef2544cb53f13617bb43f2655e549d50b5cfa0c47449071a82d3ff	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761265.npz
toys	b9da366249774210efb3127be346fdaff3c85bb80f2bd4250236e04e0f208a8f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761266.npz
toys	e3af9ab115aac979e85a1d063d651af4c7d050e93a31a2c6626d20dc61295e94	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761267.npz
toys	8b692bc6bf5f95614f5bb3f817cc5e6cfb9e064eb6c2f4c7043a37a8b8de191c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761268.npz
toys	efa74d2415c209f6efd181df7fb0d06e991f119cfd67cf0d2e76c8e02d588405	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761269.npz
toys	94ad49af9715e52588c3444aa04f5ec8891bd1e7ef3d9acf26a83b6b004ba25e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761270.npz
toys	a5c10efed4ff4a2ff559523a575a28e6c259321e32c48ba5e762f966225d9985	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761271.npz
toys	25f90bb5a3817d6b5482878986027fd41980b0c4196aa6506d741745027ae8d4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761272.npz
toys	941a96b6523f64fa3650ffa38936f5fbd7ac0bff3eed362477da2ed1a84d7577	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761273.npz
toys	0d824cb14ef0cb58d9c3345675a400967739a09f88c9b4d1badb9d4de34e663e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761274.npz
toys	02b165ec1aea405d93e42a6820a638a216a2779257fd22c1a190985589ffd082	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761275.npz
toys	259990c21fc457b4e5dbe075d49b83c9b4e0e5da22b2c7613ed143e1f83decc4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761276.npz
toys	5c72743782b310d2f99e1769493347ad7c28fbd08ddeec4e988bd64723db777d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761277.npz
toys	e8994457ff051352913bc6f9f84ef9ef822710b766658f72c5af7bf161027f72	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761278.npz
toys	808521cd9f18bdce6a2eb9475dccab15fd8e695080abb327eeca992529c263ca	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761279.npz
toys	8dadc00e3789dd0a4a9e9e63fb07f29de3ab45d9705fe4898e4f9203bacbedc5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761280.npz
toys	99388048569390ce323590e71d207d8e6b477f79aa9fca4a4d01e413291d83a7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761281.npz
toys	26596a6ad3de9c3cadd84217794295c0528d9ef667a0b82d5510c99b54bc31ad	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761282.npz
toys	27fd4b40cf2ecf6a58df86fecca727cb1d2bb13a796fe1fc0658cea9911cb2ee	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761283.npz
toys	3cc7b1419a45bae2e4525b8b27f457470a73044da9b5875d791b5cfd681b55e0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761284.npz
toys	e54c95dfaa7752555bdb28ebbedebb39f9efe32f52942cfd84f3c265f184a924	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761285.npz
toys	8925299a0a5c53aa700568094233e2556d862b0959b7c9c504d67f418e79bb01	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761286.npz
toys	91cc0133d241730048878fb56a51fb8cbe04936b97a120144ae083a43660d909	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761287.npz
toys	470b99cee01cd3744444ea356e54461ccf87e98a834827e349cb9411cb2c9d7a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761288.npz
toys	5cceac3d3d561990e1a18c43ac5084aa7f76f4eb400e6c5dc31870268d90a9bb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761289.npz
toys	46659565737d15b740135b1b55ce2f7b13089d863264846e930ca23763acb616	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761290.npz
toys	82da307e25a77a902c0392d638011959090daee2f30cafd2d4d6d6c4e8df2163	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761291.npz
toys	e2bc2b42e3f74cd33f735f62645fce6b59dd3e01ceeef3dbef6b3eb15a5452a0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761292.npz
toys	6dc0ab5c6c9ed5accdaf21bbb1bf0705858819c37339dcb9fc09b93ab80aebff	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761293.npz
toys	b573629fd560fe73a897b3b1a77d671f02883047e2f949c57c60ecd69ebf45cb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761294.npz
toys	348905a04610104ad9ff61bf1936dd9803880766d5f40df8eb4a8b8c1b9c1c0f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761295.npz
toys	26cfe78e48241a3abd69bc4db08c9ffa44bcfe181bc86ca0048119b198e4c548	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761296.npz
toys	4607327bf7b1cb17cc32d7e0b8f3d2cfbeb9135410e3ea3a3a924d35fadacb3b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761297.npz
toys	cf6477320a15ee70a61361c16706af638d0e9ce4e3c334489a93c0d1f98aa11e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761298.npz
toys	926c512f864e32bc3b1c0c27520fb80fa819dd2b662722eaba6f57486a51ab6c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_all_4761299.npz
toys	524424806f547b99895212b1bfb86c3f5ccaecce7df0e9bfba4bbd12a96d7909	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761000.npz
toys	8e531f3e0d33cab5b569341a89810e07f37648f2df154dcc233172c7f90738e4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761001.npz
toys	5c642d9bcc174d59ad266f21978d77e7278ec5adb0f0bd445e2f08a5e8289f11	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761002.npz
toys	44707cdc89027f08c25a6bca9a2e1fd7e522c2f416f9e353fb1487884396b4c0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761003.npz
toys	682361e6f0192592d128346dd7458bfac1dde17afdb2a9817a59491c1a96ad9a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761004.npz
toys	c6b34adc74fb2ce0e64a547fbfd61bcea2b01f89116d2ea27cf521bfa12025e3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761005.npz
toys	3b9fe5f2b97710494c3e97281496887660cf2c37d993414faab7cecccf84df3b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761006.npz
toys	32a0ce2c35cd61da97233a91da9db2b1dd1da8fb9eb038d5350e50f8c065822b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761007.npz
toys	4ac6cd8b00fe1e31f89ec89b2cafb607d51047c07940bc88c3817bb0602effd3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761008.npz
toys	9b482b4a9704f9079a4d3d5c6c8fb6889f6107140f3bdada2381493484f38af5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761009.npz
toys	ff74d7b3bbf235a0a1a582e9c2b08f814c8c0bfa1aa17bddc1238ea17c8962af	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761010.npz
toys	34c2dc7738f2f6ff2549304e29e3392ce7dce545f8b1b7b62bd395d962ffb7d1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761011.npz
toys	99b0186cef0fd87442ca9352dd0f7f9490b59e91c2b19aaeb53a059a01157aa1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761012.npz
toys	cddb6fd89c0ec79c429601cce501562667988fbccbefb0ac8b1ec85080d83283	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761013.npz
toys	9161bcb925e1c4e00765f75aa450421f1b66a2aa111378f4c36157a2e2b646da	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761014.npz
toys	d07564fe970e319a429c1cb1004040166716b4bab502f19f1d7a844b67502496	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761015.npz
toys	fb9493d9f2ee9a3cfe9b944e8bcec48abc1f05be84d3f06b4609d4f3e038ecaf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761016.npz
toys	325fdff3ddca4be8909a8dcd6bfd3f40a7b8f4b3ed3a1567b8c2618de1697ece	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761017.npz
toys	1313b3de892af6581c2c3e92b91e617b1f3682932b5b43083085026549616eb5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761018.npz
toys	7f5c5466c29097b9535d9cefd13c2fc72ffaf0f77dab92b6109d9c72fb53fdfa	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761019.npz
toys	9d12ffb0ed580a11e74ffbf31c3749dfd36709e42db4e65075276600ff0e8284	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761020.npz
toys	42fb7db573c359daf4313dfbdb4a7ef828d598fa355facc092f5627b4ad62ddf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761021.npz
toys	ad966ed9c22c5a7f572e64e339ae49d55597c4b6409a19fcad3a5c344a14a1a0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761022.npz
toys	af2c4822318db4d8531f85c651df12fb71cd1e855c83e0fcdae845fb1f93ff8a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761023.npz
toys	d187357ef4cf792695c1e8610c48577ba08ac423d5528ce53dace249215b9e6d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761024.npz
toys	0caaf354a67864e6d024f9cde594f22687e4867389adc0553860b51e5946d2ec	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761025.npz
toys	b81375e476ec8cb409fb31b4d415feeb6537f679c82f03578b756eb1f4e42d3f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761026.npz
toys	fc5c6ac3aa2db4505c04da0b8c71a821fe34b109a3ab9667daac9d30b5faad50	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761027.npz
toys	15058d64a7bf6a1cfbb7a5081ab9e821befa25ab260de0546665c5c8cada4d4a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761028.npz
toys	c1675dae38955ef421a65e4cbdbb25440a32f8f89b3b9150d60e787a148614c5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761029.npz
toys	59748d0383382372f18a5d32b625e8f54026d10c2ac7758e18b5f4de5dcc73ac	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761030.npz
toys	ad93a00c85d3bb9760a9efb7316dda620940b217ca22967817398ae8e8b7694e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761031.npz
toys	79401c60c7d0617ceb87909aa26fbf457af8ebf693b42e815afbd4f97700c013	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761032.npz
toys	c739558a30922a03fe1fc981f3fcc207bd8eae399635542ce98f42834b153f94	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761033.npz
toys	3e436a3237b3d69bef6fed9f34c53dfe7aa3babf01784da16973b7aa1727efa3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761034.npz
toys	f60e30ae07fac70e0dc960830f8892552b94df0e9c1558ff83f2fe55b55740a1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761035.npz
toys	681f8f159fd33eda58ffc02545c72c33ce60469b60406c5cdc91d92fa567b078	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761036.npz
toys	d956becc884560949a2964b09d409540da475a0a2b4d0cf6f30ad4f8f2ff185e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761037.npz
toys	d6f4db17a616d012031ee56d9f6b7160f109b6cbdb107a79712c614317c0947c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761038.npz
toys	88929338e9cf603cb898c833f2925ef3cf401ccfccbda5fe973ddfb64f79aac9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761039.npz
toys	9ff81dd21a73a7ba9417020a9e94e920f338e670d8fdf2806bd191b489fcdc4e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761040.npz
toys	a4b596bd3bd210c748c31435cc03a23d65ccc17d7f574475a61ff0e9e91f9004	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761041.npz
toys	ac0b64fbdff81316002af4b9799487b51be1bb6d9ed4be0f8862ef14a74b6043	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761042.npz
toys	e9efeefb5285e07fe011d46055bd53f4607986b2d234206e85b9ba4c3c4ee2fe	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761043.npz
toys	863021e5925a9a5e23d38b1619e6bfe283d703c47cf17c189f1a2e0fe1dec5d9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761044.npz
toys	16174a99dc91df160f4fc2bfb5d98f23d7569eaff0943141a4bf9aabf84185f8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761045.npz
toys	1df42066b4fea65f5156061697352e80e755a720af72279933374c1e0ff426a4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761046.npz
toys	a5a0073382e8ec5e8f4ca5b64ced6f7cbde8770cf9cc0954d910eda79725b4c7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761047.npz
toys	ce160396e6eb1f660a07ace11af6d7728c880e0e47a48cb1fa7626e726f5ef38	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761048.npz
toys	3595adeb3dc7bc3501f6e5a6a448e1f9c7fdab2221824a9993269dc245890f67	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761049.npz
toys	d110a0afbce89df1f4337fc4e9c1892221656f29ef44eeec1ff64ec2794e9560	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761050.npz
toys	8dd06630bd1a062867d0827a5a30e4c4cb515c0d2e5f0b01f222da33674e32cc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761051.npz
toys	28f2f229c4ed8ef89049f37016160c7e245c958e5659fad9861c6a7972402c03	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761052.npz
toys	542afadf292f8678acdd387a77edc37ca0071452cbbf0b3eb1de10dfbc522600	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761053.npz
toys	bacdd12db08a5caad716e45dea90e5718c13b5946b5376457c515334e1f606a6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761054.npz
toys	fcac2c047afea39ebbf1a4ef2f6b429ca794dda6f07a13f3f2ad9f24be48cd74	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761055.npz
toys	abf9bae423b5908399da8d142428c341ba20b056af3f70a055ab951a8e932896	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761056.npz
toys	56fee6e4112e3df09ef05fbe2f15914a284d8233d565038ed8c4e33170b1128c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761057.npz
toys	ad4aed58a969f8d855f7aa8eb658cd447f96a4d9a220f4685f8999bf959a36ab	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761058.npz
toys	914f4d86047607f4396a31e51e065037a773bc1e42b85e5d77de5df03c3f8bb2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761059.npz
toys	db6b50dfac589fef1c2d31606aacf091dce76eb2fe75e07e003d464bc4360516	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761060.npz
toys	61d2e14b8bd319c0db1213e3b351bc112716fe71c109744a9e4901114c16780b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761061.npz
toys	89d07aead5a9d7fd24e28ba6f396241d395ce649b7dab822a6b34a8478d9870f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761062.npz
toys	5456e20e48ae3b341f0108032b20687487bc7e5b87c7c495a2ea17189118658d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761063.npz
toys	4bdd993dfac11c4747e3226978e952e6e34780d9365fe730dd76472e928f046b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761064.npz
toys	9a4da4e3a73f9ecf8e5d6076e4c3fe6d8fbd60e3adfb2aebf3e28cbcda1ef134	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761065.npz
toys	747734e61a8f31bc32c56a7aabca2817bff3bd7f25c8501eeb9ee6e47f09399b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761066.npz
toys	b21a068ec72d4a5e2b6a51c4811ada3101ae63221ea6d739ebafc270cbb1031a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761067.npz
toys	49e7918de744b66dbf3f6c11a225055a73f0fa1e83284937b97583621b5399d5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761068.npz
toys	fd3b2599d089a36fb4607a69cc2c4173886be20f563fdcef44b9baa644b4e88a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761069.npz
toys	b5380a2b94a9309563a28476646ceaf44de44bde5370d58c1b060d7a0d1773e5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761070.npz
toys	0f40aed81ab52063eb2a98fad7dcfbab4aa5e979b20ca6cd9fc8a1d5267c5a09	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761071.npz
toys	1738e616267ff30f2f555737847bc2107e36e51ebc675d2820811816c4a87906	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761072.npz
toys	30bc26a18c5f0d179cd6ab8c439ce66567abce77f904dc3bea41737db8558a46	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761073.npz
toys	dceb7b2839fecf779787cf761000af320cf05f3ce1c821ed11087eaf9cbfe059	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761074.npz
toys	ed0ca993c52756bc9d53f4edce7db161902f279b0c228d1a0483b21b7b3875cc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761075.npz
toys	3a05cdbf31e4ad681ab7f7affe87c484449486ea1d652c7b1d3666791bb59ace	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761076.npz
toys	f15c713d1cda6a3e8f4664b49f56b0532e1be1bfbd99aeeb7f077d6defce3417	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761077.npz
toys	37d528a983de050d0da15622b8612da74d64ed4ea072adae0c95bb76b92a08a8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761078.npz
toys	0d85fac2b8cdfc85aabe536b17055ba41ec0abd03310921c0cd3e705e7acd366	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761079.npz
toys	c49a9de12fe928a2602c6c7fc40f6d3af0de2944f038ce0c087546f7249f7b3d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761080.npz
toys	5d5958444a3834408849f4dbf99e5346bd3d06e57ec1c6cba9777b776cbcf972	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761081.npz
toys	4157ca406ea2193726910bd7c762a9780026c0e859b9e5d01c1c09ea85640bcf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761082.npz
toys	0ed630ae770781cce8f8aadc5c45b959fb7520832e21f84112243bb341ed7ad0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761083.npz
toys	fd86d42cb830f89afa138c6be45454305a444b54776cd0cffa2bbb37253fbebf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761084.npz
toys	a493f7f7088a892693d68774c7dc65ce1363ec398d631c2a7810df0710d59ad6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761085.npz
toys	bf51ca1f2cabe65c42b00d2032269bcca9a7da188623961bf9c8db80364df99b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761086.npz
toys	90a0a393be2badc097e9263ecb9bf4f105c5acea7b73b889677535fb3c126e68	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761087.npz
toys	3ff98435ef26608f04ac1f0f147c68b47cb0fe640fedc6ba4b739ed846d6c611	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761088.npz
toys	aead7ddabfef1fbded504f7139405d6e9b709322048bfc1cd975f9407c5e0d74	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761089.npz
toys	6ab66bd327234d7faf69a2c5b8c771cbfe55775fa8ce3e1381e1e95f103faa41	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761090.npz
toys	8dd18f9121204b1d0097d2b7d0f93274ab3ae8d38d1b3961c3aba65f65bcfe1f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761091.npz
toys	717524b0812dfd2a7dedd9ae680e83a361f041d8909e1e5fd4edb5d10b0ec41b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761092.npz
toys	cfccf132352ca23e27f026072115f88e9738a83d47d630e3bda8c2924348da60	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761093.npz
toys	b519a055b3ff9d674cec33d9e190e2ec856feff2b497efb18c2f1778b46a2748	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761094.npz
toys	08f0747e64b75f7e1cc838892be038c86a27c31fbedbf09ae895577391024c3a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761095.npz
toys	7d57766ebc4c5eacd4b824137da741b0393aa77b4305304eca165a334a2d39a2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761096.npz
toys	6da794e1914313f87bcf19e49aa0280ee580eb0bed444ceaa0c812b7f98a38d6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761097.npz
toys	747af2128849323deaef28899050e81304efc558cb43bafe4a2cc2f0b8c7570b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761098.npz
toys	3d5ef2db2d1ea8cbc307f553c3f8ed5623e28e97ce3b8355d0ef4eeee894bacf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761099.npz
toys	588788571cc6a65ec7d43a6616a8ce409b0fc5064a9d8e02a998b4fd7ec0fd5b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761100.npz
toys	cb8321e71b9b47cab4cfe55525b9bc4d7633829671c7a3a68d814f9ada447690	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761101.npz
toys	da98c8414a08feac39bf4ffcfdf4b53f6b371885bd92bf33991f15522b4f5582	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761102.npz
toys	972fcfb7503a65082023bd2eef724bcd9d51024ddceac5b13943fe22f6a01874	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761103.npz
toys	7e6eccfda1b301255cfe5f4b24ac74a10fec2b46e7659b5569fe1f480e10c99c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761104.npz
toys	45beeb0d924c798e0bb72568605ed44a7371a69ca9b5a0ce4cb9019e79a63cfc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761105.npz
toys	af223184d20ca43474d3177d645e26b442c6182d3f3d1aba7a96a2565e93ad01	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761106.npz
toys	dc4bc432d9478023f8e5e8f6c9c3b3f173c75958b637c1d72809c89e47729c40	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761107.npz
toys	cf556c951bfedcca6fba4cc506690e642fc6a84746df6850fd5e14615861230d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761108.npz
toys	59baceb8003c6f8ccbdf1f7143204ee1747c2b401cca9e592ff3ffb5b9e2488c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761109.npz
toys	729f35583490baa4c0fb8753a37f813fad3493ad8c77a3ba3952febb22ed2241	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761110.npz
toys	7f14ffb734ab27bb8904c4d2459671b472b00fbfb2769f174095816e4dc0fd55	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761111.npz
toys	55ee9800c05c669ce9fe942139b3a00c886fd161b244db4bca56a089d995dd77	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761112.npz
toys	5760ce1d2472e3b49f73798481204a2ae0d1370a708a0607229f0a3056b4e5a4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761113.npz
toys	7f672c743ecf6c54be6b6f5e1317cfc7711f27e6e059f0ccbe17c83ee9012582	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761114.npz
toys	f1849ddfb39483264ce4ec1dd2e8c39b20499ecb23b9f0268c6444605bbd5ed0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761115.npz
toys	f9e2fa43160334fc982c88fdf792c2263ad602270f34b8609b46e6d255dfc160	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761116.npz
toys	614e973248eb52574923d4d6a9968600895931069d203c71e012ce63f6dfd5ab	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761117.npz
toys	70a61dd3401b8fdfc633f7ab5a5862f5d6538ba5d82bcf86db9497087b32d2e7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761118.npz
toys	33710f9100751a4a568a4f5c406e0a933e522895b238383f128ac5169ba9bf5e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761119.npz
toys	bd140a1552c86666246c17cbeaf3df6219f497cb5f52fbe3ca5c536c43449a11	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761120.npz
toys	8382fff9dd961102c34ed60b7a1e608012fcb0c38011ac26b704b7be96d299ad	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761121.npz
toys	b5230249f393bd253cc7c12414742282e08423cec68a45468f753a06a83b7487	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761122.npz
toys	677e0c825a8dcb67bfec4a238ec980e0bb27148f96747fe67446c3f36fdccf28	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761123.npz
toys	4656997a81e93567ff69219f99c5d96fcf0847a97f8b732464f7dda0fd3babb3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761124.npz
toys	3157ba315d4efcd10ecfd9df8fe37b24f3872ba04eb70c6812c3726cac4cd352	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761125.npz
toys	e12c7f461c9922ed822f6eb6428cdf3551056f91157008e4eb3e6766f0db39ed	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761126.npz
toys	0dc218266534b3947e3f37973e19184dd165f21a64e9fafbce514d04d9ff7e85	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761127.npz
toys	da894e614eb0ca146b6923a5b12d7fffd4c28e4ad15dafb4cc440a9950ee4cee	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761128.npz
toys	150e6abc094b8915450990bb3147c0890100e345d7d95db938008d2ec2ccef74	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761129.npz
toys	26d3194a9b8e466a4236494ca40c58fd85689f5d08ceabc5f8dea28a8aee3126	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761130.npz
toys	d9c89479781cf66d56320f5496dd49adee29b0f08f1cfe1d28e737ad5295189b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761131.npz
toys	ca9e878c4314a7599d43d3cf179446325b300306c255a925cd35f33b62802dc6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761132.npz
toys	2032d72e42d3bf703accdef68a685ae4be9777b3d492fae128479a434cd89bf8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761133.npz
toys	cd41f0bbb2bd4afba4f37e6fb09d6261de089700765dd9ca37fd288b2a68f622	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761134.npz
toys	f965a2b621dda7d3f108ee95a8cceba139321cdeaaafd1fdeb16fff86c722fc8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761135.npz
toys	5fb9dee8667a7053c52999310387ff991229d7f91411866ecac77b96c2ceed11	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761136.npz
toys	5f924c14d5b87cc7b4b3c89d2f8d920e623935ee41c835730692fa5bd792d895	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761137.npz
toys	854cb7a1113b3c8f1f400ffa40109123010a74631ab78cddf4c4d92edc12b361	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761138.npz
toys	0aba6acc422551a74102301f5a9b14149c4cf012a8907525bdcf41f0be24f458	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761139.npz
toys	da67057b1e06d050df160e5fde2988364704d78327f467bc907f4a95560045b0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761140.npz
toys	c2f2a136522018db112d06ae962921996dd0e1b4aafd6c26c67407e01d3a56b5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761141.npz
toys	d58ab138337a1a4e73679295bb1872bd86d0520a3a054054f694f1a71baffe1f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761142.npz
toys	4c99b633aedec999c97d8d294840d4f0eedc95a096d2a6a14afb4df6b9f533e3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761143.npz
toys	7c266e6368fe252e861eaa5ce6298b92717aaec8e9f07c31c4b6d84b5dbc52b4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761144.npz
toys	480b8a8408819670046d6651912acd7d3224f458ea1b3c4960f928a4c350b375	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761145.npz
toys	e52b52436afe1ba819f8843a1d6881d5b45d45332d6a0e93008496813ae31850	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761146.npz
toys	3f9a3346e08e79e2e2b59b2334ef1917c0b598d1aff39148a9f9ace74c9bccf5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761147.npz
toys	92862e9539896d9b7975c3ddc871062d074e2521a5bae55a83fc32855a93c30d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761148.npz
toys	0e3927942048ff44ab83d314aadf89c8b7773c4130f475126aa4e9a61ef5405c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761149.npz
toys	a777ec614b0c308e0dce97d35a9cabbc0aa530fe4e6324697d36639efba017e0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761150.npz
toys	858e9e3a86c6f9372b3a3223f42bb45d8f22caa36c2d1b9a41b178711ace073c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761151.npz
toys	f4721dc846d93acc1198b210cf7acd21252716807442b0c787f1a30c336cd617	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761152.npz
toys	7f644096978d0a8b31163045ac66f95a029568ae5e45e2e6a2e58a80c46a8617	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761153.npz
toys	a4ccc557133c8366227ec94a31aef159ecb1c2b00f0a66ce4d6b45b31222c947	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761154.npz
toys	5245bf4f15c4b01257c21a6b5f828ce1526264bd14674b792849e68c092b7996	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761155.npz
toys	c62fbcf209b088c0a0f95cfaaa97ec39b9cd1f1ece581539c51c3ac898616536	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761156.npz
toys	9e82388c4b5f62f42fafc189ecfd43837131ab7cd9b966c1048631b084a18f59	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761157.npz
toys	c1cae594311ef41559e7eea542ef45c7d9b9992b70b93b1dea328f975fd0ccba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761158.npz
toys	1c8497a79338910c18486180c984f0e0860a3c872341ebe5877edc63f0f74551	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761159.npz
toys	4c23f8f178ca3d2cc4d199c5ed9cbe1a1ab6bfdfdceebb5a222805d27d38c5fd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761160.npz
toys	08d9d401b053d6bcdd0b98674e760185ee38a25d806658e01e28f3d52efd7859	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761161.npz
toys	787f66c7b4eb806dc2b148fc5e9f9ed2fda806243c022f6f1efd568e3e68f849	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761162.npz
toys	117d76bf5a334bfd6e6b7a786d7d381725afc217fa8bcd3a6125dc593fa4f4da	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761163.npz
toys	783586715a81f1f14d5e1842792cb48227e61ebed35bc2b379591dedd8709323	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761164.npz
toys	ca150baf22ea7e69999826873a9e5949d5567dcc6116b3299c10e2c780a00d4b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761165.npz
toys	b2e293781e53a41649345d27d125a45005362b6174fcd23938fba10a03f49fe5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761166.npz
toys	e86f7ecfb559ade983629ad8124126e95786cf6d4de39dbdf850d83e71d2b902	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761167.npz
toys	b06cf58c90f6b055c052487e1a41333357a5d678850ce432db4268090ca0ff20	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761168.npz
toys	f2717ee07b9d90941e809a0985ee004aadaec03e3b202d0d920b2032f26dd96e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761169.npz
toys	8677a61e8a61b69b97015c3d2f546149f6f505cf13977555e4f4835bc47249dd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761170.npz
toys	36b76e6e2173ecc34d6cc255e081fc2abf67a1beb8c2caf85b29b4a5dd9c988e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761171.npz
toys	fc0a4b313c0b42caa58a9c8610302b1064a3091659ea8da7240ed90851c8d3e1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761172.npz
toys	f928d3be1ec474c75daffbe6f84c9b9cba37e1c66ba5c26adf03c49c4e03426a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761173.npz
toys	40381ee8b288d298a9c25e09418859eecf70e070391e84ef830e686d1448ccaf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761174.npz
toys	4a3faded831c3c42c0d001988ac4b9b304db32dd7170e6ba33cee03338bccc86	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761175.npz
toys	ff04d18cb3ad7716e49601ccd5fc1d676c0b00e214da12e93a24796ed632a092	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761176.npz
toys	be920ab0a85fe6d3515bce5d475d1622facb5d5a8770e79e3c5ea92cfb40eda9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761177.npz
toys	7077798badb8d3a321e0e828028f14328944c3776af6f14e903695abd2711915	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761178.npz
toys	738f214ade7c1a3fa55e114864142ea2cb06f6f9f8b5b7240ddea7ba452c68dc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761179.npz
toys	4851f5613111a55cba05da2892e61564e9369bacc89f003c7986d435fb468522	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761180.npz
toys	8cd8bdfab10c7d4cf266653841edcd23d25d358ce65fc838a7ed9f4cbdfea77d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761181.npz
toys	ebdf81f2bee4ea209fa5e9022150b43e6cca5fa8265c34d20f513b4efb28ae65	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761182.npz
toys	7c8c67072a874f5c51b0dfa89233e7a49811dfa10018e4287f5c45aa3a665809	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761183.npz
toys	13bc847e376b6d77ac79b206142927e8306570fa35f7a3be471a09433c6aa6f4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761184.npz
toys	6fd5b83bdac016e77168779fa16c7ccabd4fb91630b5007d59494972d78bed6c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761185.npz
toys	7a8466754215ae464227a7e912d4e54c9547900e990032ef11e0d0f215207944	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761186.npz
toys	10a0e28731e42ce5496206753d1f7d6e79d9e01468a1a15d27a7260e73fa6997	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761187.npz
toys	e750091596d4914202a27776153ec174c6d9dcb425837359783f179284813e1b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761188.npz
toys	15c8fc22b381eed988b6d8a62007a7814f2a83c72df2d79c4e814772a6ae6788	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761189.npz
toys	f4547beb2ef40d16d5ae7f8ffaaf44b0168591a35b8781494e773e73d6db5140	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761190.npz
toys	d4958b085421af82bda20c7088d2be51027a8620928dcfdb2697c09aa5edca7f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761191.npz
toys	59075c31065456d0160352a6039ce4cd7b4622a12c4c630d0a96037861911d52	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761192.npz
toys	59e9a9406deb914df84b0629e3ef31633ebfd22c3c53e0eae17aa3a0eda66e42	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761193.npz
toys	4fbd92c92912aaa362302aef09088ab63e5d5630e4b88ecbe48906ac496692a0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761194.npz
toys	e44b438605c7c20215aa1c3f393c44e886418626a3e953cbb277695d14813f96	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761195.npz
toys	d39f4056b8cdc92043c6daef7b437f67f872a4288d263614366492d89694ee3e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761196.npz
toys	0b56313c53546be5c9b060a1d31001d730e26775a400f9eb85115999ef64ed5e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761197.npz
toys	4e5512feb790b42eb668cef0a4966d08285c75dcc477e87ab5c2f0abe2bb4abb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761198.npz
toys	80129197c52f27b3a788c266d459eea7c9629d37c610980b78a54090ff55615f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761199.npz
toys	a4b38e0d9b28e0bda89988a91f0922e5a4fa8406b9fba816a1a5fdf9155ddc6a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761200.npz
toys	b73a28653d02c15442647e8156fa19132263fa52ad17913d8e97d57f44d78d90	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761201.npz
toys	f0d8187fee961790866f09c3b0e07ae69619d1d66ae8f402161f98957854bf9e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761202.npz
toys	a1976ba8a0aca4738a596c9d97fda33c0c35dbd54425c08c05948695c4ba4681	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761203.npz
toys	51ab6e88fe07cf529ad12300ae3b2ee9f9f2337cece24ff0c4f223b124fdbbbd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761204.npz
toys	74356d4ec314647720ce8f53245a2e9c5528cd43b090b1b32b968482b4cd4931	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761205.npz
toys	28892cf3369d11b69ec5f5ec8086492e6caa7230b6c644cd909c49789db2ddac	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761206.npz
toys	d135865e5f5fb282e3debaadbc6930a529528726ccbe5bcc739d0cef3b616068	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761207.npz
toys	885f3e966f303ae75e5ab6c0a0980cef19158dcc9866f29bdf42af2f3319204c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761208.npz
toys	4cfb1bf914dbbb13aaa10672160102c2437bdaceac1c02a08f2874dde258dcae	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761209.npz
toys	1a33cdb9f858526546430898740bcc5ffeccdd82b2122978052979eb092164d9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761210.npz
toys	7b55c13b308081746fb03765ea7bc3eac2aad8f6b828dc9224c3eeb2ba98d28f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761211.npz
toys	925458e1d820f24357ee5351558afba29e1da514b61b4e624375c86044a0e6c6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761212.npz
toys	7e5696969544e6a6ffe51c9cd712f7be29d6cbd1ec37feafa59ec90596994527	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761213.npz
toys	d180a5257c38915e4bf87a8f7cd60238e13886c03d2c5e0201f06c58a545a095	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761214.npz
toys	9f862e2684e242010674f4f7eca0b515b85f26a5372f962d3c612ada06c611bb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761215.npz
toys	4141ff415690365a5876a90b1f37d7e4c1099ddc5c11fbbd677342a512c5ef4f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761216.npz
toys	d93833fe038350ac3b7393a9d33c18f092913cd91c34a12340c6ac074a40e426	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761217.npz
toys	25ea4c0b3565bff3a06dc75b39f45a92d314b246438f9eb9153a7cde4f2659a5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761218.npz
toys	5f5adfaab364d25064f0ef178f319d4efc7ec68cc7e63110b4db031b16af9880	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761219.npz
toys	540d099367d4d3c48ca667f871ef45e50df19d07491fa65628c35ffa89680a22	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761220.npz
toys	3157ddacc918e5c5cea92ff9755167f443f2d554222e941c2056bd4f57bc3749	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761221.npz
toys	3743063ab70318d1589555a525705b7900390dc2bcfa3ed205f09b6e8086f422	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761222.npz
toys	b6d7dba033121a0235e1ef25bb6dff4ba95264f04f59cc377257e492c4cf5726	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761223.npz
toys	04dd961ce1b4a8caceb6142aeedd17edad6afd7375169a8a08492a63bcebd5cd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761224.npz
toys	713ed8f2a7ecc9009f129ad2289c6918f5fe0e37fc228eae2005544b08951fb2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761225.npz
toys	3bfea8d034a58d88ea79731b9cf68f9b55d2aa3f0504e4ac0cbb9367b2fe89fd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761226.npz
toys	f8e2d6c991d552dd03c1b7ddbd73fc3c6470a8698935c8b61bddc5e515072a17	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761227.npz
toys	ff405eb7df84a913a2e101f1c3e085d2ca2c191b2039d25798234ea223c4b220	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761228.npz
toys	fb599b281b63fc9a3e007c228b7c6e050ab52bd390ff3204a2a3f1201e163aa7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761229.npz
toys	df82697d81a8fe6cf8f127af305ed0de6e1c89e3858e6e2dfed70fb59d02128f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761230.npz
toys	ecdbf7b17288225d58d2ffbaa4a846216965b05e98a9516e36e4edaf695a4595	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761231.npz
toys	c9e48f11f710f9881157582246ac615f52b2960ff2aca44c4d824396757b1a95	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761232.npz
toys	8b5dceb6f9a39345468fd6ef778e7a03d951b1cd671784e5f32f6386e67b9036	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761233.npz
toys	dc4274b1a3fa9d9ac050acd3305fe156a5d120b104e7cd98ff87b4e39aee5394	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761234.npz
toys	7595dda1dc574c44cb3463784e3131d08a8d6db81c98aad8692b536523b70a83	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761235.npz
toys	d07268fa02b5675d79d93b54e72f62a7ec5983461ee27aa5115f9c6c7b81f90b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761236.npz
toys	2f614d94788c12d7a174d3b9dc5a9f64edaf92d933d904b53539cb4a056580fa	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761237.npz
toys	73959aa0a154d30c2e3a79652a493df3e6b6ca14de94337eb91879806ae8e2bb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761238.npz
toys	1e5ad60d39a30f852cdc3f489bed467244bb60077213fdb63ce38b0dbb006cee	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761239.npz
toys	798ea3804ad0a4d1de5dcd0fec19ba8c3b4b2d6c29401172004febad79557312	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761240.npz
toys	483eea4036f87d174e72bb720a8cef7e1dc2c2c539881ab6db97344cffa3c6d9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761241.npz
toys	0579da40026a07f0ba85219931c7dce0af7f161a201aae336dbad579d709367b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761242.npz
toys	728253a14364e0f294a9e5dc786708b3187146af4c294b2c1e5b9d1083ee13c4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761243.npz
toys	03c7d54324781de95af6b168424a6bd26292e0e88831db8876b759c58dde8873	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761244.npz
toys	58e7852bc2ff1127882e5e18e4dec7f25f701455dedcd5a4eafd8d8fc7071449	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761245.npz
toys	c1684b825782c294fada43da6eed36ed788d405f0b62b0912f3b242ca4afc001	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761246.npz
toys	e77bd78f4099b6782ca24fd19af829da7ad630cb69e5c64bcc6616d5ba3d6d2c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761247.npz
toys	fa4a04321955a79f36c16c89d55060714e4e9681e48238446f8cc2959627bbe3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761248.npz
toys	85412cd790e947b2e31ebdd834c08131bf37b8b35a56aa9f2b42f49f21cb7674	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761249.npz
toys	8f5de5752b134d8fa01fe14073829d8960bd83f91b330121dc80387fa9a8b5ff	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761250.npz
toys	3bc12dfc67fddd75c862c924190404fda235f59689439aecb7750072e7e56460	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761251.npz
toys	6a1ed81b71be4e2a961999905487904cb9907accc0d75fcfc4736356834d5f21	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761252.npz
toys	6e33433bf50aa4dfa8ba1994a3e5b8fa614ff24bb2d6adb3a575caab877a6f9d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761253.npz
toys	ff0a1a1df17acc69a91fec234c45914a3249b25772179859a7e34f75b5c11278	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761254.npz
toys	860d2ba14ce7403bf49ccf886443663bb5822241b566c0b582bc06f3700c4719	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761255.npz
toys	00a68927fc660c8098c9c89a9c9e800106f7e51fe310af22006887de541e021a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761256.npz
toys	74c66f6a599209565e0e809e50e27674a34dc7aca78fd37de41a807fa7bc925c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761257.npz
toys	6d178974b329bd37cf33ed017245666fae75d29d6508bd3c9f5fa446cb97bfff	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761258.npz
toys	4f65a6fda850bb5aa35d0c4f960e94c7d117bd29d7a0b81f8a147828590c4d34	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761259.npz
toys	b0f40194882db5bfb0978736d64a8d3ee5ac3e19b231fab860a5a59a4c5dea29	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761260.npz
toys	2343e1fff0a3686a9d4c3406f86fa99d4f44ce75dd8203dae3b9054675d73608	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761261.npz
toys	8cd321d5838b5ba7010f1d6232c5829da9d89e83f3f6c2cf36195204d751d2da	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761262.npz
toys	92f24a16832e4866b531a7d13cd59f4b026db23fa611457b587e7653c0d9dddc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761263.npz
toys	b90d2924057eee7894d6aa42799089a6403a2d9a03901921c50582411f26599b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761264.npz
toys	6f0f95a8db7a14d0528b3a78bcd74bf9649ef817686ed10a1c7ef91bd38b6fe9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761265.npz
toys	835c15348b5c50d04d2784555743ba22afc9916bbd04a7b7a0c254692108c11f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761266.npz
toys	1b7740f2e93620bbd6d521f1c4e2d66bf228b9251f87af0126eba056c5f70ff5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761267.npz
toys	4be967df01ce736c3cf9685c839160c0b0816bfc22cc046ab8ebb4b499514b1a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761268.npz
toys	1ff30601037cc6b73b8a7c16d2c4776ff01adf7e3a19fba6a2233ba9c1dd09ac	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761269.npz
toys	6872202bda7745b0f3081553e9978a192ed9e55353902e2a7ed32535696f19c5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761270.npz
toys	546d264e6051606c98da86beb6ec77378809e31b658fddfcfb7bf120a940cc96	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761271.npz
toys	64285ee3ab5b9584dc285b8958966bfec2d534ad462a1abb289bf30f713bcc34	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761272.npz
toys	6940268a0f195eca633916bbef061a4b5cca9783572fd8e1329451e17b0bb4fa	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761273.npz
toys	06554255633c5c3b15c396abd903ccdf5b21a7a57b1645d7427c3e863248d020	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761274.npz
toys	e764f6926d78f874e5a6616ae922aee8eb5eced2be65970c87fcd546de4d3560	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761275.npz
toys	3e8af85e12218f71f6c2df1d7b46172023168c1232f14c77143f7402ac59062c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761276.npz
toys	1e0e54f66501cf31d653b572d95a4ca5ea2e7d745c4742d57da38b4ea675dc0f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761277.npz
toys	afc7bb063323c5df032d4ebe149a54ed23933b7b6b99dc41a5f671fe19a4fdb9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761278.npz
toys	4ee7d71be722dd568d0b4f5f455caacaf4fcaa97a8af150e3343d994a62b142e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761279.npz
toys	170e8a105ed988918e1f79541248242edec9637519324f1370403360997e4598	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761280.npz
toys	d7315f7ed5ae930557109b726f419e6410f6463853f5e3f8c6d580445327e227	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761281.npz
toys	537b9378146898bce5ad2a7c3b03b879eb9370d2c0ba1b67cdace1f5a2752cb1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761282.npz
toys	0ad17cbb7dd35d3a2fdfce66a724f5f071b791211d1c623bc2e81c92ac2186d1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761283.npz
toys	53f54d7c76f61ef683b6352b93d3666ceb60ff109fea5741e94ac70be6fab1b4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761284.npz
toys	f88f7b696fa8bea6dc29956a339d69203fceba796ba3941f36260301f4fd309a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761285.npz
toys	b08459e6d6e1dcffdd24b0ff875f48309ac94c405c7d940cbf340dd34da5b83c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761286.npz
toys	e7f4ae76d9041c8724ed5921291148da192797295cf816ce71c1dd3baaef4453	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761287.npz
toys	bd719c2b778fe236d554c5ffcf440b1135fe810f49d26e8d175f6117fffca48c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761288.npz
toys	2e339a8c998bcbf081d3c96a5bdcff2f693c7cdde1f9945345bc942f17ac2012	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761289.npz
toys	f60f0bfe6fedd52e93797d73e058280e608d32ea7092c5d0a3772d3e9f88c015	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761290.npz
toys	13a20b417e167ac1984629e451b441cfbf2d1332152d310a9e765bd70d08d008	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761291.npz
toys	6d67f54a57c450283eb41b10f473a1054c6a2afb19d8bd2ae18f1eb6de0dbad9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761292.npz
toys	6e04f1f29992b9ac80376ebd07fabeaa3b51b5d4f6f78c3243af5805fe78bca6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761293.npz
toys	b6dd010bb47a9051cd5aea2967893e62b06ee760e39a7222ed7d4ee889bb1f60	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761294.npz
toys	c2b176c99a52e61e677ae72a2ab78b2cbafe8b1e1bb1b592bb0ac3257fc0e876	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761295.npz
toys	0f1e2c2c04b1141a1e445525978b608c4251a0598f4c843cd5c0cb274143c3c2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761296.npz
toys	c597421dd107551780d76ace32b342a784ae73bef37fa8e5e9b29ac5ed7cfc8e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761297.npz
toys	ebffda82fb066037093475420a2d64d8eddb5fbeac52129c111a4259736454c8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761298.npz
toys	53fb9ed94c22760269fa1327330399190b6de8a911fb20bef877f0e5eb398efd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_toy_minus2_4761299.npz
toys	0d532166e24c70de3ef192dd0e969f5f1c3a040af2dcc516e9d216e3377f2df6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751000.npz
toys	db88763b033ef75285970efb6d237b0390bbfced974959be281c08e640d7587b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751001.npz
toys	d9212dadf3bd941691eaa9e1d68d1d9c2a825e0e01584af815360ef7b17bca47	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751002.npz
toys	8a76838c73d5a0d971e3c3b5cac9d16ffe80a4d49a8701c292f42befa880368b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751003.npz
toys	6ca20615641e22d187a91d63e194bb9c9a02e5450fdba2ef3dda314f36ffe514	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751004.npz
toys	b05ab56917ee11d61c3f478cc0ab7d51a091bd2e763c9ff8b51e77fbea76d3a2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751005.npz
toys	f6047b204aeedb10e365bf4975aabaa54d8ba69c83579d49fbdb874fafa7201b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751006.npz
toys	51e3d20009ca916c418e983d796698a6979eaf91cb9cc2f73d4fd1100b2c5b90	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751007.npz
toys	5ad512b976ac447e12cd0694d177815e0efcdae8341db9970459e7032f4bb3d0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751008.npz
toys	ff7e937fac87c0f56a87d2810c04c56c7e3645f281b6b17a90a2687052d2a774	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751009.npz
toys	a52545e3ebdd95c9ae344a462bc6af55fbfab2e92d9dd046421253db401141d7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751010.npz
toys	82570052c769624d632f8d2f487728fff270514ba60e65f8260f6547bfb37a83	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751011.npz
toys	e19fd955ec9ad834701b843f97e49a644d9a52bfe30f05be5e0c3ec2b36ddbff	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751012.npz
toys	2dbccf42c635173e3a86362c5242545c99a8ca9355962dfb2cedd7718a7edc29	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751013.npz
toys	2514331432aec34fdba144b31812cd75ddec54fa0b656f3ec4bc80a4c2b40194	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751014.npz
toys	f56ab79e2585dbcbdd5a3de8e5fddd1917c6d4f43a610080caa5a12edb1592e9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751015.npz
toys	3ae937529bf51ec3192f1d5c35704b2f016f9b741a54391d6db2bdc79c545de0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751016.npz
toys	b545b539741540fdf0a4c9e43052159a46b70fe8991f6a9e14fef02626830cd0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751017.npz
toys	036e45a5623cc6090946446c3ec34f54fb875577afaee17b8a3787d8bdb27b0e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751018.npz
toys	f93a7090c8b51b21b5f94181cbe49689449c64df1e242a8743564ee2bded5d64	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751019.npz
toys	6d1f125adeb1d19a83a1f641df10dda29b8b4a8bbb627aa763a419d4d67141c6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751020.npz
toys	c0f1920848d03ae2299636aff2b35ed90e40e1c87362777948def15c7a3d4773	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751021.npz
toys	452296579c0af9c655dda7c229c3aec91f16ec277488830784f25976bc61dce9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751022.npz
toys	7e6508c52d5bf854e933d5213d8ac4f1ab28d0891c2386e3d650e9c2a7fd055a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751023.npz
toys	e2fdf1ecb96727acdfcc99fa34cc95cb0ff6e433bf8892de11c612ebeb336bf4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751024.npz
toys	72ef8a9640c8d55c424b63e4421cdbc7dec59e9ec3f3320071b19fd24965316d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751025.npz
toys	9538dc2011fbeea0a4ca0e133f31fafe77cd0dd74e1b8f769d955909ef17c7cf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751026.npz
toys	8a3ba259480e8850fc8fee001a4f5ef8d9117f77c9cd9c9b296ae285427ca072	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751027.npz
toys	0ca7616433b36fbbdf1512cb04a793726440cd8e1942ed57858839ba1e341fe0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751028.npz
toys	3337c57d1198333a300e9534334bf16364257c48fca2d1f9beaa31516a0c9ace	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751029.npz
toys	0c9e4da94d58d0fb51cea758ed61d0d0bf495b595b42061fe77b67a55a1b5015	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751030.npz
toys	9354e28ae75c8a52356d7765d9efc1ad24db173efd754f211e9cfed82739b2cc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751031.npz
toys	8654f57edf83d30d247fea4439796210d2355ff99dcba0870d911cbc4f843390	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751032.npz
toys	d74de8f168085c9998e28d7a2bee11cb8f7ba6ea19279565abfebfa3f60be9db	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751033.npz
toys	0776688cb90345f3d41fe39df28d5418cb8786194f7c3f47e88c94663cb0932c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751034.npz
toys	3b85be2ccbb564d969133c10e29cd62ef118d862b102103a35a3369032fe45ba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751035.npz
toys	498f2725ad6bfe468a55e8bcd6cb1237e0a01d7eec9894a93d58e95e14b00cba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751036.npz
toys	78306a0315344dbc3b8805cdd47a5343eaa3293467fc88620b34113229324417	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751037.npz
toys	54215f5e7154b9870dde65936aa20fe9f4c7d4854ca66ec4f529aeea1bd4c919	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751038.npz
toys	2ca9d9a006c236424685764991ca9b6aa0c16d35a30f071a8a78754e93ad214b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751039.npz
toys	4d4f66068e66199c5bb3c7a0bfe251e136933c446e7262c65a2e9df74945b6b8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751040.npz
toys	0e49d854c8d1fb32ade91c7886216269fa686beaef21994b4be11b95cb5c57a8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751041.npz
toys	b72f13a53bf9e8db645c06a5d137c02511661220121be9a142efe45617a83b26	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751042.npz
toys	609fdb8cc288b59c61f057c98661c13b2e7ca0177f94f66130ead43d920b9be5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751043.npz
toys	5a7dc97b3c4b1ff23a724be0f56e2e21549decba0c1c91be5b7e168b2dd34c2a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751044.npz
toys	17462234ee3bb51732fea3daf89cd138d18b99ccc3477fed475cd0c45f97e8a4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751045.npz
toys	4e341eb2915e10b46a2e44bc970704a087215866f18d1a8b7aeea926b6873512	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751046.npz
toys	e8ad942eeb78514b5043614be7d3fffc346ba00c9278df29b15134ace1f9b264	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751047.npz
toys	92b03260655bd39bc1482e80ece7124cdef90831d7f841846eb7ed8145022872	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751048.npz
toys	590568ba2e571d4faaff6f7fb921785300b9e827d549cfc099da8d283cc0aa46	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751049.npz
toys	7d47d3afbc0501057a47b2ea6dc2ecca2cce2bb0febca4be35af3320fc6774d3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751050.npz
toys	8c1017de6dc0004d2bc5d06a59fd0b9aea09a66150874664d8e81536454b3b89	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751051.npz
toys	8e003fbf2c037e761b4dd2f2812a7385f91e67015ea453354e4235cbdc3675b5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751052.npz
toys	efc3e43bbd4d89b06475cb301acdd3e9c045b72a0ec976092b36f42beb5f3378	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751053.npz
toys	75936bc898efcc4d300630d14b75f395ad9aac27d419c09066311c94758efdef	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751054.npz
toys	d62230c934790f828cbca2525a2dad738ba7084c2573800b0fcecd3d55d50292	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751055.npz
toys	e92408d72c79d23488b1edccca3a48674a929311b911d75f7319e05bc9edd9d6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751056.npz
toys	e427aedc8340ed9d633528b1ef2954fa0194d0a98888ff26331fbcbc54a9f384	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751057.npz
toys	7291a40f7f198f23116e6dd2eeb99f4a7885104cd8720039c69de9b9267bb21a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751058.npz
toys	852eb7cdf3a4632ffa30b3ae9c6ccadcfa2b6f106515b7a1151ba40743738b37	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751059.npz
toys	f7e725e5c76983c3537450d0b6db4ea58857449a6d17241e128351ac65f399e6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751060.npz
toys	08e85857c5d7ec97b2928e2c116b81a67a07f6428539ac12cb5d2f57d9ab182d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751061.npz
toys	efb81a3de9b29de13e54cbaccb044d75f3e64326e8ed7e280b320df728435862	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751062.npz
toys	53213c8542b6774524235d61aecdc18f4595ecd5ab6d29f5aab85fd34cbaadff	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751063.npz
toys	c196fe47ca3cf38dfb76998dcbefa12b2eab847ffea50279df3ffa3138bef26c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751064.npz
toys	7acf8237ae5c9e7ee170422e8df0a1e2d54b1f0353d2034ce4bce005a25955fd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751065.npz
toys	da11934383b9d3967b91a3b0be4f1c2caccef67933ec854c1781398bcec2ee7b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751066.npz
toys	9ad4bf20f4132d8c440c58f044ea47a20f7a8d254db2f62cefaf9e2edb784924	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751067.npz
toys	431642e61ad84b7328ee7b8f13b902f0dc7842905bdda65be95da0ae3db60932	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751068.npz
toys	5543dffb3f8ba23c857a9e40c3673c484e669cb89971da0b9457a0e6182eeb06	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751069.npz
toys	98ef427f07c7672bd66bdc1a64a698ce24fd2a71299a3749dde8b2e1a53c316a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751070.npz
toys	9d3404d0613d7016e6fb145f022d15d18f496f0224da19acae205f4bb41de86b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751071.npz
toys	74c8b5d7a9901b8816377f2c484d8541f52aff5946b03136b7e2cacd33477596	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751072.npz
toys	ce7f74de22b3810954b94f46f76ed6d864b2591ec37818621074dc8b57ad56c1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751073.npz
toys	578c6cca875fb4113aad1012e1e5f171b7546f3bc2973fdc1424ac05a07c35da	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751074.npz
toys	ab51fcd0faab00e7fb98de0fbdb07eeddb03b07d7e591dcc0560323a17f98299	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751075.npz
toys	e5b4998d2ab8f94f9e961f31a4e1df156e8be4ceeab7b56bad5037fac4499780	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751076.npz
toys	90f489e318e57a4b5dd9eb359fde9dfc2565a93323d91772907498ac22f2e63a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751077.npz
toys	a0e390c413f66327a52057eec3a451f3a9c04b594ca0e9123149e91c23d4efba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751078.npz
toys	afd9d7c0e47f28cc851e74b1471e85fc4e7bb65f59a726103954057487ec3d64	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751079.npz
toys	60a32ac3430610175086c05eb4ff354b3d4c99da865c5ac6c26d374e19ccab65	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751080.npz
toys	79458a6bd046de1c3dfded07b21643e77e68ac77ec8c7ead9a99b255e1de6fd8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751081.npz
toys	75df05e0730822cea21ae27aa35af93b62a3fadfaa942385f23ca624b0c568e8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751082.npz
toys	a369689a60449ce81634d6c76d9f1b7796e3cbaf33ef9bbb900d575cc1f199e8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751083.npz
toys	a245282580e121c6246df77b5231828d6d7c190ef1b238dd712a0a7c50af5e44	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751084.npz
toys	c55a7d056bd1563155e9e7e76554668212b561ee01c64aa6a3ecd934d6656cab	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751085.npz
toys	f42cea472d157c7d7da7487649321cb21e45376e89ea6d707239ae0bb024703f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751086.npz
toys	17809a6c97b400e03d4bd8809d683c6df356221dc93626a6c23a3dc1beeeb4a2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751087.npz
toys	f1241aacbb1c6ee08560c1afe07cab6e5ef63155e9ad0837ee727cdfc324a8bb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751088.npz
toys	062d20b7227736a334f8f653ad256f0b0bd713ed7750ea485e742665ca4975b5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751089.npz
toys	c2f2f073e9dc13dfb93283d2eaa3017b1f3e89a4ea52e442b1e25ac05f89d2eb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751090.npz
toys	8594c056f61f767ca3dc8b6d98043455212d96fe774242e0ad60083a879a8d99	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751091.npz
toys	c934990a3eb446b4fa54f73cee89143c5ee45ba09a40d9afdb7a64673965bc52	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751092.npz
toys	b5456bbe84bc41d52550b920b28f65548ca9355b5ad3acc3b091bde7829903ca	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751093.npz
toys	30f34b02cabf4aaf45054867ec9020ff7f7bd3fddb8d1918f8d55b2341f171ba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751094.npz
toys	c76e84641aa9f4f7ffba2a221e2e41480effb8ff0f77d576d353ff65e701bfef	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751095.npz
toys	c5418d8312180096aac64ae6955ede0ace633dd94321f1880243f1d54a85c638	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751096.npz
toys	1c1ddd112da1022d0fde8b13abf1e740289c62de682d5fd8438cd7c69eb9a6cc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751097.npz
toys	91d3495bd66cbf324c368257d78b3b27ad85df930b08558f41a071e570e4e26a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751098.npz
toys	e713b020e8c0f48b1db47a0458125a62024ec8d8d90d13482e38823cbd19ae7b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751099.npz
toys	8eb839559746ae761cbe6e16a21e0c75709e625c4089b18beac143f1150794a0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751100.npz
toys	82886ccce950ea6a861b736e3b3ed1c480a5d65e052772df047aa8050d6910cf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751101.npz
toys	05a11af87bf38cf2456eb6797e66c90c9a5516c20a6ee6195185bd036c7e5250	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751102.npz
toys	2e06d16a48ac426c7b60097cd3db26087fbcf43bc627b8910afea9925104bf5f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751103.npz
toys	6ce8accc492834fefcb0b03e612256ccc6c584935599b461d70585cc7eda1a2e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751104.npz
toys	44b17f367d4924f02f0528420bad408d6fd5c1f896078d70fe073e3d54a14e96	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751105.npz
toys	6500b93c406de61ece104bfb0bcfa2c7ea81c21e8c2791bb178870e0f93d178e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751106.npz
toys	d56a23e12bedf591fe85aa303de57176446b17eae4a3d8662a804292b812e824	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751107.npz
toys	448faeea3f1d5dd26e18b1d2ecfed9850b33851beef3a9abdfbd560f1ed90aa5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751108.npz
toys	ed9a15b78b0c9ed325d2319ce2614be84297eaa405f7d03d710db5757db82848	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751109.npz
toys	b54775299627fb8cff06d5fd4d03c287114d19bf8c95d836ff7b9d63497d4508	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751110.npz
toys	9d659567b3614841b4c7b64482ffb9d45200227878e584543b7a4c99a5e2fbe3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751111.npz
toys	c808dcb5c57fa9d68762656887ce3cb58005e37b331db45d4935bcd68dffcac3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751112.npz
toys	c5413cc8c9bd5aad93203bd3c66c1d89d2e114d0598e7eb13f342ae3fffed607	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751113.npz
toys	e03334381bd0601b0081af9cf21c68fc19767a5db6f2f6edb2414a0a8e9b18b5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751114.npz
toys	ebf25aa74e4ef802248a2e899664c725676372c7fd07037f68a345f3118327d2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751115.npz
toys	1ea13e1c63fc369b848eed3114bd09b4f9ad3bc5e42935687a557db530cc384a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751116.npz
toys	d75907ca295de92251efec073a64578c43a330da9b22ff63e21ef209800a18a7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751117.npz
toys	09f210f0478ccff4a2d4e13230cf80ed3e917de0e8cee029839c46fc484b0980	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751118.npz
toys	55029b57f83aa890b182446108ace1dd1189f683b68d4dc144c300972665f8df	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751119.npz
toys	a4b21b75cad28afa0f9f87b9490a1a57a39303285768929feae76f727ea2ee3a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751120.npz
toys	cbe9a2aaef72c6c7fb51e40ba4bf8218495fe3c6475f7ce68150dac0f1725334	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751121.npz
toys	3de5657832e63ec916d2ecb30ebd93899e03b8d1157537540833aba38711ced5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751122.npz
toys	9c191cf600239bc8dbaea3c9eb6c84dc90724b3c4070cb63eecfa2ca61bb43a1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751123.npz
toys	a54b19b77d77fcb9fe73340d0226d5299ea2f725d96b08937cafa82b65ab1f7a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751124.npz
toys	3261cafcc34019767e31516d21f9c2f73447acdeac3439a4bd364a6a24e78826	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751125.npz
toys	c4045eedd08dc3dfcdea77ef55ec36ce5923cf25111d8798e0a278d6fd1ba6f2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751126.npz
toys	3c985f6e82ac7c06df06632223fd9fb50f50f0eab5642a71440445cebb198a94	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751127.npz
toys	1cb5456c802a08755f92d0a6627b9e831d6e1840f32cb67cc84f40b61a4eca25	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751128.npz
toys	509cdd8684fe1273f5883ff52c88fd2e1327bf7c0cbc1da3fee9556f63eebfde	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751129.npz
toys	7131bf3e359690f93b342d014f1950dc1b61faa63bab96120894b6f5de5e59bc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751130.npz
toys	c898cfeb77d8035a999823186130c3aee4cc00458c8a758c9724a2e88250562a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751131.npz
toys	a5d7b394870f0b298b63006a939ba2a497cd0bbdbb69f33a6347ffa4d26d6ac5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751132.npz
toys	9cff1986591dab7494c56e9d6582c03cbe59667eb673c94a39d6923c7049cabe	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751133.npz
toys	0ee2f03c65263f5f098bfecaa1eecccb32e0efeb43694513cf5ea4eb99ece7d4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751134.npz
toys	90b5b22e0ebdf327039c36727e77977c77bbe9f5d6fd5a8c0ca340adad1261ae	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751135.npz
toys	ba3a29e37b1ba50196ee39256e1aa4f659427a734af0d2e8c3b1c7c315215f26	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751136.npz
toys	0a7136977e970a3e575797bcb52efeed130d42c233cb90ef5182b910e205d64e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751137.npz
toys	1af7499e819f5f7f7c477ec324c331ce3bbd4a9ef30ebca3210186eda4786609	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751138.npz
toys	d7cfaa5e92cc3ef32525da1d180d429aa02f081d9faa5e29c648196172302db2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751139.npz
toys	ae352447d1f1ce0d9f1f094d3507f77c5d30ea93068d6c1e03daa74f6dc1d9cc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751140.npz
toys	6f75275fe74624e1286f66764c93a1d7af8e2b17cb57ba7ed845992f5a43e377	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751141.npz
toys	ca1c8b5c1120aa2c34ece5cf5b2fe4ec40375d7c8e792296c3a1e7c9119c55ac	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751142.npz
toys	e892e3d5ba268ed9be9b70426478da1e472f0ee1cef3ac8e169e93f92dbfe4af	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751143.npz
toys	f6cc7683f2314bc9b93a8a95c0d876bd256a1b2e95dde6324e5d157305ff3866	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751144.npz
toys	5abf131e307143e939ce1d99ce8dfaa2e01f13107a2d9a7be5f512567585b131	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751145.npz
toys	963e63db9d86567ca033273509d7f6db78b58fa3eb31161e3affe41ccc9637fd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751146.npz
toys	9854fce8eb3b0c98e2f179c738d683cb165f56f7ea36f1881b5ec748cf3a8e82	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751147.npz
toys	90683bf98693d367156ff8e3e28d9563a672b284d99dc28f1f8ca73e5d09073e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751148.npz
toys	9039d9a6c7336e6e32ed3916809e7c613c078700373dd6e51ab47b35c496b8f4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751149.npz
toys	b440d13c1a14adc36ea8ff48ac629d1bf8cdfd9e6bce5bf961b81bc323d2b3d7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751150.npz
toys	ac1549361f28b5d420bcbe7e8e9bd3d81ebe0ee99f1671c0418415c338765514	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751151.npz
toys	6e45b261661bd82bcd068b5e4f07bc179babc6f5dfd492d70fda6f571fdb9252	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751152.npz
toys	abc627015b0388b921e6ccabeee390c1106f3464127418843034197a413b9c5a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751153.npz
toys	18fb867ef13f872a0736638f141cb6cd7a2e16ebad6db94e3ec724f05b107af3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751154.npz
toys	fcadea76c60c325849bcf38e28830b8ac7ebd118fd798c94f4c92f2754ab8797	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751155.npz
toys	265d89765670e5a21b7d4c61679b37b2c1e3f98f16b3a4467cc65cd9c72d1823	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751156.npz
toys	a6e1850032b6d4e645a3aab72231e4f75d16f8102428ed75537d050c9237964a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751157.npz
toys	9ea7b8fb91f8fd236088d907085ba56c2908a2d653f28203f7d1f7c3357cfe6a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751158.npz
toys	79628e727406aa443383f8247f5e695a0f80392135edc71a598fd01e4c9b4187	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751159.npz
toys	cca2e0dd1d915cdaef4ff77d4b72ab9e34e441ed1e06122a328fd63675c5583a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751160.npz
toys	788c5876f520f2233bd7eed312f90204c3898d575c3185ffebcffb7581a4b296	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751161.npz
toys	246b5522ff6a635e1a96e00a035f028b4c45d63024901e6fa171320a3a2cfdbf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751162.npz
toys	92309739d5a8fdc290451f93c76304755a8ab402a417769355e55c3340c4b167	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751163.npz
toys	4fa224417b3960e7c7f29175e42828a7dc49ef0e531832a10265d56cfdd417d3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751164.npz
toys	ea57f713919ecdf57b28c1dd03cccf8d2e667d57ed0670807c4f45e7a02e276d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751165.npz
toys	a3a70da7ac3fecfbff00c496ba8df894d6337126af964da1a42118c6860a113f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751166.npz
toys	18cf14d06ea0a3009732271af6e2de5b0cf9cf517fca59d7329b24203704473f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751167.npz
toys	93f4e7ac7d434e753d99d11d6440249256902d9b5d0af41e3bf36f7aee2353ed	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751168.npz
toys	ff569f436e0e71473c23fbd84bab8b46d2927da63895fef16f6ad878b01bdc37	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751169.npz
toys	db4c4bb1f8fe738363043e9afcfc588a3fe2aedfe96cc7f867d1f45e18e6194d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751170.npz
toys	c66c878da41ff06ee7485f741d8caa9dccb9160ecbbf0f0d326e73863e8be1f6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751171.npz
toys	4149264fb1642e823beb007c7d41c88ba2584ef7d197a6dd754a7d2b5de6336e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751172.npz
toys	9548be328963ed4f7311a5a432dd12a91552f328ed75b5db5b18a85bbf05a938	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751173.npz
toys	e2f5f2e70eac1275abee40ccd8f8c57bfcbc6d2f5e8983f04e1fdeb2b791d901	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751174.npz
toys	8a704dab5787f6277b159a441774cc450214d72bd15572bef06745d8625a1636	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751175.npz
toys	e7047ca77a558b4b4fa16191ce9497d72d670c440d559562ecdcce05350b193c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751176.npz
toys	1fb8811b85f1c6a88497f74d474db7c1f66f869bbbe6dd75deee78733dc283cc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751177.npz
toys	779cfd219bde3a2d6a567c698f241003afb8e659e91e508fe2fbfc841152dca7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751178.npz
toys	7473401bbe5decd4699c758330e9cc8b0b1bde78e49f722466ea253b49f1c461	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751179.npz
toys	0fdd5b3f199a994f23afef45ddea72c659e425a77bfa63ccaca0780ff6ce13eb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751180.npz
toys	f15f8299fca7bce056b27a7005b0ba95010a04c2e1d263cf1f71a17e0c206be3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751181.npz
toys	d7f7eafbe1778566c1b86bfdf85c4c2681bb6c4aed0f589d5ef788ea78c1936e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751182.npz
toys	d146c9a1bbfe5dac7d41ee0638fd775d4ad15dc5478dd6ba7d6d78ae0d5d57fe	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751183.npz
toys	9b8ac6ad3323693c30aac1c38f23c3c4731f776e4b04a486e3fc57158c4f0b9d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751184.npz
toys	9f3b587dd490858104e383ae471836f46e22cc6412ac96a304e631f58f56f64c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751185.npz
toys	3934e209fc69537f0e6520b607ef0254ac0e5ea553d9bf27491d6a97d22a397f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751186.npz
toys	c1e0274ce6e8ce66fd3a368aa45f814c3e0c649f490e600e142df37f7ea243aa	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751187.npz
toys	2959dcd7a8e00a2fe7477b193327bbb3aaf6ffa2d3cde654996ee901c307f32b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751188.npz
toys	f1c167a95393fc204d92f0a11433c6d6aac2a046bf26765b91d25ab9966ca556	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751189.npz
toys	0fb71b8744bdf2cd436f95a9de299f786c341bdd1de0a2d70bdbfbad7b3a46db	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751190.npz
toys	14b975119bd59aef23bb0a70f04948688c5730a8dfc480dcde21ddeb2fb57a11	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751191.npz
toys	04f5213bc267393c0755e2989f3acc6075dbdf38d361f990bfb1e7d5d7f52549	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751192.npz
toys	ee4d9c9fb6b58c6be312a2ea415b6e8f138f809a6fb82f3c10c9bf7de8442c7e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751193.npz
toys	945117d88a934b1c0694eb93a686f79b57dfb289c6458ee5c2f21ff22bcee21f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751194.npz
toys	220c4d3f032691ecfdc19182f6865af10f87a1301302fdac486570637ad5d225	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751195.npz
toys	0dc7adfbb0a3a37229d4eb6b5ac52700d7d0ff4f917b22766b299869a35b2a06	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751196.npz
toys	8ce9f897227ed8f8e840533872b1b04b88590c6084d14abd582a1253f179b804	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751197.npz
toys	f281cba9e014aa60e757f08114dd947d9448a659cfc05faf6b54d2e95b758153	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751198.npz
toys	23265224ac74d063f549f0f430c7d52f5812d6f205a0b1b49f25426303187fa7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751199.npz
toys	8fe4a3d3a264748cb9be1f48a9d7ecc4f6b8cacb68643aafb62effe34b692613	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751200.npz
toys	9a28bdba6dc94db82e59f67e10ad54bb732a0d409b358e3a0ebb8712a8cff2f2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751201.npz
toys	05d305d01afbf55a1332f78559b79348e06e29cc39793e318e34ceb2c3e256f5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751202.npz
toys	b52490ec77d16c9f8f873cf5d0186522d69964ae1cdb5f18adfc759b8a0c4c39	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751203.npz
toys	cbf3753573b76d590519ef0e6dcee30a4a3bf89b143d75c5d99aea5f7ecd9459	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751204.npz
toys	9df3ea7f4a94a48d171d8e298c8470ac7cfb0b38c367c0545891353b1d7bbddb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751205.npz
toys	be8ab36c9aba618dd6ae9210b4a5eceaa10c5febb390812ef6a44da79d6e380f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751206.npz
toys	9275491b2be35759024afd0dd848d4ea415266a143ffdba7a193f0022057a166	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751207.npz
toys	ca2219afe24403f1b882b213cf8fc3593386315cbac86f4ab417205411d1f497	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751208.npz
toys	b559ec5d6a45686bfc8b65983f6e7a7cf0f99b993668b07f375244ab7d92d91c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751209.npz
toys	ab03d83649475a04fd5b09a31db8f542892e37c3d82ff2417eadb524ebde9371	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751210.npz
toys	93307850dd3e24083f908fc853996408717d19c49c39e704956ebc7021e878b6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751211.npz
toys	ff1e6b93b4be926ce6b2bbecd34c1ddbd2f496141b69317f497569e1de7da05c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751212.npz
toys	7528623a3d21a3ba8d5b29e06e22e80fddf50a31b8a268900debf5a303f2ecf7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751213.npz
toys	cc1df08ba0476c080af6f258df1da4100c9d7c53dc0c30f6a1d8f54c6769d646	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751214.npz
toys	c61015216ef167a9dbc12b60de88a467c80ee16e5b811174e18abd9508fbda20	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751215.npz
toys	e562d51b8a36c49c5af951ac4fd10d1908b7783c538862b5d15eac35c8ef2cf4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751216.npz
toys	07ae6c7675b206e3f4311607d5eac3911e25887fa7218966f06ba018171b763d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751217.npz
toys	f8b7f42c9891f5d83d2e034cfb2005404e2a7c96b0a7c43eb25bd47fbd996abe	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751218.npz
toys	874f3d681265233a5fbd144dff6b27cba3a5383badc701dfe0abd2042bf87d91	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751219.npz
toys	46b0c81c7933264f2261c431b9f5edfa2f95b03bf83176bc40feb6a9ad13cbe3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751220.npz
toys	6540933c2be190dde42ed9341412567d8e5a91acdf3b6e44a172dc07f150ff44	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751221.npz
toys	3e7f4b07eed124a44f4b31a023153bcceed798663a13915cb024edc290596dbe	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751222.npz
toys	a7b12cbd7c28164b3a7e391cfb7f513dbfaa3f272c5d2c1fa169113de803a9af	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751223.npz
toys	1511e97ebf373d6e0a26aa49032e2d1234d2a538f9d9123fe589c7b69c27c94c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751224.npz
toys	60385cb2b96ed4f88cc87c98db29e470d03f09a9b68dc4ad8115daf592dcf96d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751225.npz
toys	898bcad474dcbae5d5cb5243b259d0f3f9a5093db9cd3845ec458c8a56ad3db6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751226.npz
toys	d2a4e3612d5dc94bc632bd2133c52eb0e54707a6dd2da19bfb85d1f06cc483f3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751227.npz
toys	e952f527caa068aaed184199d23fd32630eb84b8a6580df588807043da98f0af	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751228.npz
toys	0767496dff4f8b47e88d63fc3f3a8f7149396a73387eb18b9968a45e45b587ef	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751229.npz
toys	89e0f7b406c9e7bfb7ff65fb5d5f97f47d4c9e7c69979190c3e57c42f5440cf2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751230.npz
toys	bcd0fcb7c5527b4279c9ee12100697726c4d4504a1dff9da90bf3158f7078511	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751231.npz
toys	cc0edeba9e661494e5bee597f6c2bbc31825a813a523aa72bc2fb03e1ed33342	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751232.npz
toys	fdcd8c031cadd47138b2bd93dd52c7a5c863da9b2b2125c5ae263fb99d11fe85	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751233.npz
toys	4f034011436f2e05595371916a7727cfbcb0d925bc739aab4cddcf8f62c704b6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751234.npz
toys	59d3ae8b5b11c6245d02a46240868e8440a67a2c82cde47dbac3cf71a360b3c9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751235.npz
toys	7ad01017afb3e4c4af67f8ca18e0c1236923ab75e3cf52c4c23e0f53bb5a7786	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751236.npz
toys	8b775e7f281edea03743e1a710a21dcaa8e3d2d5c5cb714f33b43afa6fc8a5d9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751237.npz
toys	330970f35c04dbfde40ac2feae4e708f65622f80cf9357e3d29451a7cbb971e7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751238.npz
toys	4131af26d62bb7e06038ef46fbfcca0ea2f55b33a5e5551b511156d764306e5e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751239.npz
toys	0c767eda2de4bee2fbb3d2c7f49dd384bcfa33a2a66a2061552bb7bada52217d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751240.npz
toys	209010a68f9147d8f0faed768d94d4aa16563ccd6beee46cddd1347dce27cb34	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751241.npz
toys	9af271affc2fbb91b59ee4e3b71bf96a71258acbea8b716ef120a846cf7ec078	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751242.npz
toys	803cc471ef14ec1874bf792706fe3bb9201f7df06bfe4647e6f039fc6fc86a97	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751243.npz
toys	4c030a51750015f94c977115dc9ab8c388069c536ae19cf5952f0e134b56e600	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751244.npz
toys	2572ebad98ff05793dbe2c3d2b5fd469b0c88f7f16f273d462918722fb1b7eb9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751245.npz
toys	d13e3776de5c740a1103fe0d51f5da5d593d5e9fd326a4bd82c5d2ad2d7edca9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751246.npz
toys	af811cb5e77f5e581cb4ddfcd244bc83d8df87408febd4cdd02aa0adc97406b2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751247.npz
toys	639abce2e598b3ef058a8f833f15dde2c782490c9b6acb13ff8df4f0aa6284af	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751248.npz
toys	2a92e1124ee15dc93a5fec6b458d18ae45ff3d2139faaf6f7138c9aec699376a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751249.npz
toys	69329d8e803df7c0dceea527a7d2e0e963e15968ef2906eaebd0e865fb87650e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751250.npz
toys	61a038cedc7f39aca23555c42ba59516c3123cbd60936f7cc404da3f624bae5e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751251.npz
toys	412ae9963d023a311ca53b323020bbb484564ea83fc4ddf228602544ca9a89e0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751252.npz
toys	3e822856d51e241ce6a63222f296844b91285bcaed6e7e7d2f1903d906e304ad	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751253.npz
toys	f9663f44c48dfdef64b69a0b8d8efa0c8fcac19431570e41cc87b9c73c3b62c5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751254.npz
toys	e14e3c2676af835ae85aa6444c2f8216866d84a6104a91c7b753614089407f46	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751255.npz
toys	9514478166c1f932ba4cab2d04680162ccd6e42496dc2d097e72041f26d1a575	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751256.npz
toys	4778e5780c12ecd718c2337b4c4e0eb996f17b1a514eb8038c6708b707b16040	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751257.npz
toys	bee84b7430b9431eabadad88daaa6869d8649acf7bb6e44485374644907d9c35	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751258.npz
toys	5cfe9dfdc4a23b1c7f11654a4278ce770a3bd00194b0b3c1d47b91898c769a88	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751259.npz
toys	a585f2d781098f893c5a3a7332bf1989a154f4d321cf461b93e4d271409f2e53	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751260.npz
toys	7774fce5582418f6b3daffb9fff2d6aa823612f3a94c7562d3be72232c735709	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751261.npz
toys	9a467e5e67c9e41f75f0c81a1a3701d36743f1bcc54d1e6ed4a88365df073917	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751262.npz
toys	bb70ada09ca8812e2aca5a8223385d80e92724b3fda5593743c5bccf24f6b80e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751263.npz
toys	7a906cf6661d60f2f820013372cecaa4d92a679aeff65c29a1280cb78295ba07	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751264.npz
toys	0298d57c1fb945194b98111e8e28c29bc3ef746461c0f630520bb794006077d8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751265.npz
toys	c0df010460efda8c9aaf99cd846acd4a34fce161df0051f56b41ba916e68f36b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751266.npz
toys	0aa2b1ce4c3393ca7708791cd664e2fc55b53938ab7713966b4f594d0510e74a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751267.npz
toys	db40448d7ad04399709f26d729b2bf01c7a5394b3bd153fca6b13afc4403c7f8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751268.npz
toys	d8cf42e926f626e5879ef7c7f0c790294d3a9344af2b0ab52025f3d86bd6543a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751269.npz
toys	cdce206a39b543735008ed639e91c8681203d62808b3027aefad509b2aeee8fe	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751270.npz
toys	73532c786ed8bb79f03e3db18c532d1d6f88f3f436a7e83281e4c504a97b8f0d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751271.npz
toys	77c28adfc17bfbf02b02b392ebb04d230a41f78f4320d580e6e3861172542633	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751272.npz
toys	2a6d47c9c3e54d86eb425180990b6ea19e125f0870344a502ad143e65efdaab3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751273.npz
toys	f3b170d576d94266018690cf3a94ea05b5c161223727fc6740639705886d4249	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751274.npz
toys	e16948d33af6961fb3156b7fa09ce2d164ce761f930fe404488480ccbdf6a7c2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751275.npz
toys	63d8c605a9312fe6047a96f760f2bfb28d7ad199d5f2bc1d7c7b410578ae771e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751276.npz
toys	79edd8d0e48ec91147ed15b0a64a0efc33e3578fd1b54c6fd9b06a374f7ec4e4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751277.npz
toys	1842af1b0a74d7ee89cd2327a9bbb0d65d183c72f9e92eb02cef3c7fa71e7dd3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751278.npz
toys	271c78d8b78997a5e0908fda29622f158e200e999780ff8578db1f9e8363a578	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751279.npz
toys	040e680958f273fbd060da16d8e2127c5157acedc62c55fdbc0c041241b4137a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751280.npz
toys	849f16d00e8ff5a94a025df4b71be0c94aecb9c53a543644380ac1672e62e131	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751281.npz
toys	06d41dc82e23afda196860824c1cb97615f994ce102bef46d7497b2028d63428	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751282.npz
toys	4485abfdadcb0876f995d786f2719b3ffe998c214d3ef0f2e3fab2a6fad0c1e0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751283.npz
toys	ce1b6181bab75081ffe72a771d566294b5b56175c8c9a92feaac40588cd4b208	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751284.npz
toys	d9fb09ca712c97efb14a82c54ae7c56938ca4537e9b99289b5b0c8f6e9cfd42c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751285.npz
toys	6edbf956cd96f4521c4e704da0f835a6af64dfc1356b676f6cbbe016de944b2a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751286.npz
toys	f414daa25ced83b5ebc28983cfe9af09de1c927f2ad7b13160ba25f89f72cd69	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751287.npz
toys	4dc1e70f400a21da3f17bb2807b3ca226fdb250593453ba584c9a1156c96b4df	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751288.npz
toys	92607b904bb8584e85ca3b78435ef8f83a157b81ff65c59aab2d030552edc205	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751289.npz
toys	917383ec5adef96562b746f6a4f4bc66070791bcc38817c1b9ddcec0a9cdc40f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751290.npz
toys	79fa5271235dc78b491c4ab43375e47fc09cf11e4c9efe315494583d307d98d3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751291.npz
toys	dcf7d6d7b96ef9b236360c722f244271b6d68fab7ed6449c23ff819f54d9cfb3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751292.npz
toys	127aad134c58c48a18397ee94cd78229f5eec7858365d4e57cbcb5587aa027de	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751293.npz
toys	93aa2b7c3dd0a145dfc6bc0e524904beb5dcf27c6c7c397fbd6ee007b0063c13	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751294.npz
toys	6d1c75308041747d29fc95ddacc9deeb5cea35084a6479443e41581f96511863	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751295.npz
toys	a62940e4a971935eae646577e89f9c3a30bb376093f6d9d5effd5ca54a5b163c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751296.npz
toys	d2105ff065855ec0a5447ef18558e4646109856c9f41aaafb4bceb0654e542cc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751297.npz
toys	bfdce2daf4ff9e44059fd4cd895196ef6155108ea053755b8e04ef2b3fecc449	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751298.npz
toys	a49ada894682a1313877b1dbd0e56335e703a7b11f46a4f892b2805d98d70ea9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_all_4751299.npz
toys	0d3bf7a71e9cbb2f8af0860919c97395cf5d8cc3de704f045390a5e7dd1eef20	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751000.npz
toys	a526a7b2e296dff21954507f6dd6dd1d438492d06a30775fcec22274f62bc1af	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751001.npz
toys	c82ed0e226d108780e689ec4e1d145a81c41e91f608a051dbac5cbdadcd37e29	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751002.npz
toys	24b3cd345faf8a65fb1eb87c4a63fc8b6c5c815536cd375a729dfabaf28bf14a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751003.npz
toys	42d59ff20e73ad149bf9acd4164ca8a02d8a1dca37dcbccc1d9dd4dc30154941	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751004.npz
toys	5ff7f373a14e94607b0b7cf773ab2581882c3243ebd82f9572358af9dd8c1ab3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751005.npz
toys	8389a1e88c144e801262fcdc55a8ac84040805ff09817b3b62fac4e0acdec39d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751006.npz
toys	354d5973c3abae59d3d35e15c9f8d90c88564afbd926f7bbc7144891bd20a68d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751007.npz
toys	1a585dca42a86e1f04f549eb413099d157ecf82de2ec771b9a482b92efc332cf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751008.npz
toys	ef2ef6b89336a1f49a98b6bee6acfd72156ada19f5bbe5a7897954fb0316f8b8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751009.npz
toys	a8e8572e3df4ee39d08890935f50d60706a40a5eebb4292286cf70eb710c8bbd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751010.npz
toys	ccdae1f478016be2cf2e53c058e76318094975c96ff09d86c2c20c8f089f40a4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751011.npz
toys	0aba4895b130ba330dd6b6d72116f9d52a30ef990092644ade805411267687eb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751012.npz
toys	d138621086b62679927167167c1813cbfc3b26fd7db4b7d361346f93c96d749a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751013.npz
toys	0b3ac197a62626671542f7a2116723ff968d0831ce0df81a3de4fa3002932179	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751014.npz
toys	560c32ee40bf4ccec7889fec872193dc15197871a92b643165168abd192df800	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751015.npz
toys	f95a65547427836463e9c404c078341652f8831d4d79de338f4bfbd73eb476dc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751016.npz
toys	6d0dfd6a970160e58513c7bb04bad854117118c9d2fdb299318a5a95e443ff85	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751017.npz
toys	3c2305dded8befa5dc97ea5e8363706d26513d7e96f9642b0d69b5e51c54f3ec	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751018.npz
toys	dcb37893e7d8e9fcc13f2d60df8a6c118193635489b9b38d7a71db3f0c6c2aa5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751019.npz
toys	06b0826fa996a7cc60a7dee6e2e60dca9a2d30a2d3ea99ca2c76c200a80749c3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751020.npz
toys	7ff13939388fa56f355d3e1d8ce7c2a8915f75ecc950f6a72164740a05d233a6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751021.npz
toys	8eafcfd4afd6907fef87336a3a8c9c0766c557fdc06a273cec5beca30a44196e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751022.npz
toys	053aecbdc322181ea0b043dddf6786fe29fdce35ebec09f44cda2008bbfa68c2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751023.npz
toys	22adc991d36af74ce713b3e43884661cacb5fd2d8166638ae5aae595024b84f2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751024.npz
toys	9aa4db70198b16b3a54f7d6ee567ece6ca87c2fe7e1d56b3f9cf87f512459c78	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751025.npz
toys	ce2e27f2a6dfa774bf8b672a5e171072bff18fd4de299cb7f82ddc4bb85fbdba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751026.npz
toys	dc91eac057740cff032399848831f97c887a53c2b8e8f094084a5971ddfc3e9e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751027.npz
toys	ad12cf76e5bbb282b4820977ecb4bfe006f2b550ea13e7822ffcb55f9e70a7bf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751028.npz
toys	ee932874ae1ea8893c8614a01a9e9db9bd96df94bcbbfca442717c51d9f0b6ae	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751029.npz
toys	ee64aa03fdaa3f9d2f45e099e35a4742e893917471d01fccddc0d5a532a90a37	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751030.npz
toys	de5ccf0949a645807b3d46d1258be435c4d5f7eed26726f6a7d48ea51f47d23a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751031.npz
toys	7bca8abc0a83181d567455cf94bd61cf5d93d7fc8267f123c753d910fa26a11b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751032.npz
toys	bbb8799f418a7770a3816e0242a0a752c09cbd62e84cb3eb300fffcca57c2ac7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751033.npz
toys	9ae2af2e4a60956424be8817d7309e967d010e6509c7b45181ed240840abbfea	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751034.npz
toys	43c1c37b74f55fe6bd5b431210bc0ba540b39ca269e164c24bece45406364a4e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751035.npz
toys	13c433dae7b51022bfd87f36e062912c1238e5d4f76abc51c115d1111ce879fb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751036.npz
toys	d127da14a05eda2960d03e38fcf853be29fe404de5ff371aecca90444b7c555a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751037.npz
toys	c38c76c434543dad0c3204f764779961415e8bca70266d984aaafad21fd12549	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751038.npz
toys	a619353a2068e72b8809326bdff58b01091aba5ecf22f31de9f156ac38acc7a3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751039.npz
toys	cad0939329f4e53fc828fed61160acbb1e749e20124b88c3aa84dbfc5bf593f2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751040.npz
toys	4e8f3fdfd29af0925e796fafa13a93887a86e97c762b1c82273a0db99585a38c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751041.npz
toys	e74cdbda6ea7bd2392f3b235e768ebfbb031c1e30e750854a6db35d320cdb59e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751042.npz
toys	343a7a5a95f3523fc55a3101ce3aa5df888eb112337e50c3556fda32a7e32b6d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751043.npz
toys	e5dd10bb9814f9747b3382955a505bb0c79ff9405608cb37ba2a85f30de5636b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751044.npz
toys	ea19eaa327032ede0418f5dfc421fec19de8104768115b12c64e528f0958eb0b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751045.npz
toys	3208cef4e60c67031d5e2fd22cc3aa0fb2464aa6b732fd672b3a5774c7d89594	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751046.npz
toys	d95169315552d11ed2d9f5324d005409cf86a644a04f896063f3691e8a504845	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751047.npz
toys	83515e24e0dadceacd05f400fbfbefef23197679eacabb00a289b64b996abc80	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751048.npz
toys	0c4d421a96e09c0f92168fbdf68fa41363606ba3f57861c5e77eefa06bab83cd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751049.npz
toys	578c1792240eaecb85dcff3cb48d5797d8e14736e12a9ab1f8b716bb327ea767	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751050.npz
toys	dde5c5851373e25bd8c0b7037912465197b73154e7e62912bf23bc770dfb265a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751051.npz
toys	f036124efc59f4f50b175db238592410cc3bdc7159d12135f58663fc06a1257a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751052.npz
toys	0b307610ea0db3dd54f943fbc63a42e01b51a70fe4967a88ffbb837830c1ccf2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751053.npz
toys	733535b21a7daf553d3fa67bff125fd7de2e21995dc02a897cb3d7f1f3bbeae6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751054.npz
toys	805f31401758234d67f29cb6b946026d0c55b9adcf004876d4128c43642818be	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751055.npz
toys	91d64904192f53c84695f634eb02eaaaaa52e3e50e51921ac6333b09b7eabb83	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751056.npz
toys	bb42ebf0bf8190ca184bb83cb44fce2907c5655a122d630434c8d899b1ca2de7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751057.npz
toys	51da00ca8a248328aaedc4a45737ffc1f4904b59bcbc5e37e492844ddd39b53f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751058.npz
toys	6b120b411cdff9a93847770cfe13ba9839237bb392340a8f8f58ce5c492d185f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751059.npz
toys	546f418a78d3aa7bf56e4f8349f4bbc983d162539b3588fb14dd2d7fafaf7782	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751060.npz
toys	f0594d03b9a5f767493166490b0cf85ee41104f62f3cef1b68115d9013e2284a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751061.npz
toys	48bcf966bece8d0b30a5d795753f5b78e9078ccd255547c19944c79fa990cbaa	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751062.npz
toys	0d5c76229eb87a7f6a79fbcc62901920eba2cf40a9974e7538ef2d4772632003	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751063.npz
toys	778b723367b1a9119d0727ce92e3e25929549dde224a3f282e0e11502b3a357b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751064.npz
toys	158ba26d538be7afa508278416b98ddf2e4ade969b0022493b33c8c6dddf6dee	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751065.npz
toys	aee89c4cbaecedfd4bb4761787ae2b93a98fe6882b7d2d2b202963204ce1a5cf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751066.npz
toys	1c4947c8676cd56c3e4ef8fc7ef2f9418d086743ac1956430ac4bfbb90c6f3a7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751067.npz
toys	2124a4723eece1d27279fd514e16973705bb56ae9fa33217d24694ba5b9a53e8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751068.npz
toys	8df601445e6cae6f4aa0b6573cc8a555d0ca3404e62d42b7c0ecf606f2645e5c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751069.npz
toys	6f053a56f5751a73c07d7db4a08ee85fdb59085b0fc7b0a459aa5db35d933999	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751070.npz
toys	2f651ff1f452d24f4e0e3f0567732d4108ccb96886ea96244f5a53fdd33f1fb2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751071.npz
toys	090c202fb2f68ea1217565c68be19ea9a7ca2ce29eae9dd5a236dd6189e95447	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751072.npz
toys	71ddb7ad93ab25b3f2f44f220ed5f00d8810f8665c127a3dc599dc0e48ed1088	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751073.npz
toys	b766c5829cd760d9fe1d5d130c6a2ed624dc5c3781a948fa1b6f5f831ea4b58a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751074.npz
toys	1bad96688038ea34330d312b2bf73ee869a493b98ce8c9ad3b32d84eb8f50a93	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751075.npz
toys	2c29d11ff50d675fcea4fea14a5aef92f51e538b0a850a01552533d343cd0682	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751076.npz
toys	e6e4e0ce027db832ab7fa580e4520e93064faf5acbfd82b40c7afd83052970ba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751077.npz
toys	1cfe9b17ed69e74ebaaec8c8b71bfc0e507b4b0c38dfc4879a57750f0ec08439	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751078.npz
toys	4e55b44a7ce086578d4a7ac246be6a2cbe5b3a6933ba5322082f396e4a832a25	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751079.npz
toys	fddacb37d276470cfb33b98e58ad0a77f1c65a08cf602c49590c13a436be7eb2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751080.npz
toys	fdc0e8166ea04b42e3c6cd4dc969fe2ab2e86546d51261f08ea84609e43cc819	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751081.npz
toys	ed9d1b455672b64360a204453d632b71f04446926df55c9070a928e686e14803	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751082.npz
toys	360742066752f763a6c61e5ccf381208d71b429b9a6169c461bfd04313d26e4d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751083.npz
toys	8da5a194b112803140c594c30f559261bea4628e3ffed1f4d9befbc8e5130be0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751084.npz
toys	7ad7a3e793bdbd02c0a2e7aad9ddeda0eeb4e6b0192a2d3e70e74919799e2fa2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751085.npz
toys	c13b0efdad530e2f5c2eb70b0de45cd98bee15aa74b1f804fca64a0aff30543c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751086.npz
toys	814501936c51f6ee1c5f0dbdd08e0b433973e9800aeb06f5a80b3fadcb106853	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751087.npz
toys	9ba949cc8ee2b51263f7c7d11a22dea5b52927b60544fd40c4725bf34a7ca1fb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751088.npz
toys	b7d6916cb2a065591ca51cbfba1819c3eb7586eb9623dde8924e91653ca4a304	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751089.npz
toys	f29371ca9a1d068fcbc5f4d590ef39c4632fc714f042e59364b857ed7e5c7448	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751090.npz
toys	8b40d45511e07be8a03d19bba371b2ae181ab3366f66d44271663f1f0546d158	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751091.npz
toys	26bf753efba98e48fd1f31fc45c864695cbd87b4383889016c0e6c35bd6b6ddb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751092.npz
toys	fa9605f2ee5f2525ffaa1a7916bddfa20a0ccdf86377cb84effda5dfc0ff492d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751093.npz
toys	c91f7a3307cfa8dbdf40c9afad599488936d9edaca9c6930318be7c6d1338f7d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751094.npz
toys	6d208209e89a2aea456603752b1df93673059459aeda19ca73f2188c7001948c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751095.npz
toys	79330da6c90184d17d2bdb703e1459b7d41e0bb9d69d4add39aeadd31aea9619	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751096.npz
toys	2473f8a3f5b533eaf51d27a063b2287aa837c5327e8a97704f5ebf29b258e9e4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751097.npz
toys	f00b09d0e559f9e394ef5200f4d072f1fe03ba89fd89876032ee4e2b121e5cd7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751098.npz
toys	9c2248e1bfe1b1f3d9011580076f1baa08ef841d2f215f96bd0b5f3b9efc04a6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751099.npz
toys	bb45eaab2bdfddc516a849cf358f2bf02eee900efdd64aecb526e46d3752e8e6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751100.npz
toys	4408c2eda65ab2344e1aeea0cbbadc289d0c8918c44476ee90dc596ae20af472	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751101.npz
toys	7def7e43376f9da3a0fdd510598a0b513a8b4bdac5454e60e078467e8a7c0a37	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751102.npz
toys	ff53bfbbedcc684a0007242fa87539e64dd3128eaabf3842c77a758f004875ab	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751103.npz
toys	b2f26090bd05f8feed1cdfbcff424f5071bb53962da2897be09171d3de77e76f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751104.npz
toys	ec86a7834a63dac82fb448430701cd737cd927a4bcef330ab9033eee2d19e14d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751105.npz
toys	99551789e43e6f96a0bbd9879acaed86672138e36e6d4988736564f81fbe5e0f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751106.npz
toys	d8cb4822a30c823861140dba70243cd8c92973df02702c4b57911d897864fc06	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751107.npz
toys	0a2a050e4fa0f73020f9abd009d650106198d1d66098afc509df4324a74f8504	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751108.npz
toys	68d34a3cc62b82978cd80f205944c239362eca6778e9ffb8b048ce4da0ff76ac	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751109.npz
toys	73ef7cae4bfb9045ccc9003099716e4ae45df1122466e3b7b39418d8529441db	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751110.npz
toys	d9869d209e07041fd620028a25ce7bc238c95300cae5cc4353c1f59996a75422	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751111.npz
toys	c386960062d6ada5ec6f49595fe03777ceada6097b01ec6e3e8f60b0c6bdd814	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751112.npz
toys	c087fcf7d6d79d36501c63110e258fd78cfd42f5fed3f69ec309b74274b3f230	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751113.npz
toys	5b9799221505e45900a7d36b59852363b81bfed7be2a11a065941fc4e192a24c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751114.npz
toys	221658c0f74dd8feb6c57210691e592cf0965b51410b1ca7e9d4192c792c7ccf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751115.npz
toys	987a1c47c07aa0435f86e6e24ba24c6022fd6d2c2c0de39ab3821d453813879d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751116.npz
toys	fd7ba17956ea5e1863b4501db7d28251c3d42378fb720d1c7dbcc0fbec59d327	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751117.npz
toys	3a44e7384756eb0b5daae0d010966faeb23c3dcd9adf3b126d6df3009f156986	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751118.npz
toys	0f1195136771d78ceb038b98a47d2d8d6ab58330016b6caf00691c2bdf987484	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751119.npz
toys	252b53972de2a130c31a71bdc8f3c9d0646fde65eb4b8d0d8de42f3133dc9d48	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751120.npz
toys	8029b43c026a56efec3d6bb51ff1bbe01183695a28cc7eb53fda0f0e169e1436	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751121.npz
toys	424270012c8078678a18534162ceee7998441cdabc8dc16a3098e4a5c01d0630	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751122.npz
toys	3abe001d64a5030fb6c36661b1b8ba51900be7a2030274067eb6ce6dcdc3fd5f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751123.npz
toys	d4c0db288e97322c90636d93b529fb1a1244bdc89a41edcaee9f0de371f10960	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751124.npz
toys	c7690bd5d72056cebbc1de3d1ae40322d3ac342624968354e9064b8433d8ad7f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751125.npz
toys	7c75e98e55027b5bd8de604e6eb5984c694b11397aa4f9eb898fa45dd6eaf32c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751126.npz
toys	7a4cc29b3ade1b55a055733c585444758d2e0a8710395267e8cbedaa96decd96	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751127.npz
toys	72e5cd1ae610f553874460eb69dd633963c17ae9409dd70b50263ff03b33ce67	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751128.npz
toys	8d3d755df9fff97fd4a4db7a2738e65dab951307dc5cca0fd01c9501b7792d26	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751129.npz
toys	12801fb9c442b6ddcd6767448547bbd631c713f2e0d9d3389104cbb4d3f08ab8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751130.npz
toys	35c9392d78e7f83ba20b39ff38a010802be7bc9ac009868e6ecba5a99cd60d55	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751131.npz
toys	07ec4850fa7d575abfaa931c63fae33051d42321b7445c99b01e0535d87037a4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751132.npz
toys	994e72c1308a93c6e21cd0d23ca77fbd449cdf499ac4836ed272df50500cd34e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751133.npz
toys	1c51eb1ead7b1dce1cbd3955eea44152c5c18a6a06a7e3fdc1046eecd65c890e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751134.npz
toys	c36715eae0885d19ab2794fef893a2d762c30362737e0347d2373d9e72438655	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751135.npz
toys	23a5ed93c9c1a0acbd2a1cf01bcae11ea88d4bec8d79234af093b4858956be8b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751136.npz
toys	d2a208867c13a3b0cabe14851ed919af2d571bdd4c3f6a3b01a4fd93e0796eac	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751137.npz
toys	6feb7a0a396bcca096fe8fe2f3f972c10422874523382aa15654c77aca77219e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751138.npz
toys	5980f39d6a8bf492b3fd50d6168de111a8ba20917994c2b36904bf617e2a25d7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751139.npz
toys	2400b60b718edd4d22b55e0e73a0724e4c99db9af83f65164cca725001cc3834	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751140.npz
toys	0c16fc64b633bf1b9fafb51d6102627f701756346e6ffa8ea6642ba92c641ae5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751141.npz
toys	d164e2691f34cfa2494666ddc3bf1053955ac58495fe1d941e1dd9d88756ee71	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751142.npz
toys	f080cf8c0245270762ddddb896099f291352cfa4a6f47a15eb5b11e70bd80a24	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751143.npz
toys	9edbb5a4af33e156f353880e629f865bc8f3fca67a6b68a77c5d82807ec8c874	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751144.npz
toys	5fd89e0a9fae9f4a28b6d01f87bcd5818afbc81c028f200bdaa9bcb688b736fc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751145.npz
toys	ef2dbce3240da7ca2c6c1c3a8fe947262f32f72c040cb269365973dc800fe33d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751146.npz
toys	4f882a8000a1fe5ae50bab6cab155e68f46b88057be2d64ebe6444d1295a3b03	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751147.npz
toys	9a5162126bc47011bfcc0d4c432568683c62eb958e3da796a2098584e913e728	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751148.npz
toys	3c06218639e7e12a5bc216c6c8036b69d7e7fd5a957e82d7ac9972e4c883c34b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751149.npz
toys	76a5e5f941b4946d5079710bc9a3896edc621f4168c01a1ece136b71834f1dba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751150.npz
toys	a219d6d89a5d26b78591e5095dc21a5c30655a0de79a2cafab5b01f7a82d99fb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751151.npz
toys	8f823242e4f00d3d7c690fcff65e5851b54b92588d8385366f45c91e8a1ea6ff	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751152.npz
toys	6a6fa4e888c2ec2f8151a5e1721b05155b1abf278b848fb227c3de59050c614d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751153.npz
toys	b2a3fadd1982064e7f1fa19d51c5bbb04b8f9f230110d437861d400e40d13c26	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751154.npz
toys	ee459f3dbae3d0b802a05d660b7a1d8045e054634eb8a51589b46f6858ee9fa1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751155.npz
toys	90cbc2f17469c1adc8475afab9537530dfdb2d62a58567bc56b71503b522b6bf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751156.npz
toys	d288f99b1a8b4d35d0495ef4737bc55bb770e43f01d4546b0b05408c553be1de	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751157.npz
toys	41c5bceab4f23058a97b9571c54ad87bdd77844166a59da2fabc247f619de2a3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751158.npz
toys	fa0a55f3e2f1a95800d39dd907bea962db44f4c6692e65593597ec391f7f50fa	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751159.npz
toys	e8d892f55b6bbf7d2e6e52f1f3a53f8ad93f05f260bfb8ce0649463892be4502	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751160.npz
toys	8da0fe79b90ae640fe399a64c0bbc0407d7bf4968dc029b962bc9dc2d3a26a63	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751161.npz
toys	663d33024ac2b3ec6f74b131ce10e041472aca94756e6f95d3d44da75294b25d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751162.npz
toys	e5f196ad89c09d2f6949f6c90ed13b01d562db1f8ef65143a95e26343673572c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751163.npz
toys	c93a5fbf1e4ab5838824311a3bcd7b213f3f7d933efc7b4bb65dedea11bfda61	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751164.npz
toys	8ee5eea433bad611050726f15a2e90c1dfdf0337d80010c027f67100f4f505bd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751165.npz
toys	a44d20ffb60cf6be9d9f55ea7fa48c3b2b0f3970539148900e02f5f6bc3a98dc	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751166.npz
toys	2ba4f92a661e994731252e3f960eb76a36d10d6e108fc5617637dc89776d7cad	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751167.npz
toys	d9520af564de8a2b4f59150f20e861b777809021f1d4315035c8badb3da95c83	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751168.npz
toys	fbe70382c11b0ce784f1be088ef66dc05da4b1927a2032766e7c17609c13dabe	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751169.npz
toys	5e628718500ea36b025a7747a91676263fd28965f6edf6f4e05fdbf915949fe4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751170.npz
toys	6ce496562407e7bb91d3bdb7d7946172f6503aa012cfcb0998ff1e09de694c07	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751171.npz
toys	03a6476cbb915fd8e942b17bd5c14cfb6c5609d75fccb5f5b2486b95adeb11b7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751172.npz
toys	74df2ff59b888c8431edfc8f593c57c38d69f399e8b6be7ca4c58553efaf39c6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751173.npz
toys	35d58ce79adec99b1d9344d97e6bdcda89481f077dba863d5b1f37edba3ba047	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751174.npz
toys	e3cc06dd6ab54f5fc9ee60709a4041289acb593c9555d47fcf7d66ce7183b32d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751175.npz
toys	f428035b5fda9da14534ccbfa53c526a5f365c1fb952b72e63b82b495bfb5f21	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751176.npz
toys	d82294ec4636061139d65416d8cc96dd58ad53e51196993eaeb0f7b1bc71542e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751177.npz
toys	ff1ada6d1b33d88e58615f62fc6eeb3edf94eba5ba7bad5ae52c81875014424a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751178.npz
toys	3238139f08c9e7299df14dea8317a10d175a376d4bfdf60ed5c5cf8a51d85e8a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751179.npz
toys	ae0b53e7e323198d874052e072442a027413723e58f460b7184071a0c7e57052	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751180.npz
toys	1cad6f64cce20e7734f7b23f6628261f8fb04dfd7ed77570842bba693935ab55	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751181.npz
toys	1963cdea136e947bc18cb221804975b7989d9cadc05476a21cc52d646da51fe9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751182.npz
toys	1b4edbf3e814b5bd4d1f74217365909dfff90e967861750912f5c899a95b2d5e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751183.npz
toys	3f2b51b9d1cc4bb162a3dc3a595477dfe27020abb88142849f99c2d3f2a978b7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751184.npz
toys	09bfac4dda7ac8e992235151913719da5a473249894e0e77c0ac44cf205547a2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751185.npz
toys	1d9eb23e86919c27805fddd58af6d6b1cc0d42c8c33c8bd3f9c33bb0591e89b7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751186.npz
toys	fa9bd331332ee8b3b8c2e8fe0ba2f218e1f07cb6efb53e398f629c65a0b51c87	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751187.npz
toys	39dfc38d011c169a1b1ff51e4b20be5936cec4beb8edb8a874d49485fc9048c1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751188.npz
toys	2c6f65dbe9a6b96e0f46ba55db82a2d1e191052c69a0b6e8793f20f06d1cd9cb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751189.npz
toys	86320f46e23f9602f3ff6c253272a8e60f67fe4b9756f294ae537257f86fb6e9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751190.npz
toys	c979771abcbe04edd3e2c695fad1a3a7844137cb63eba873616ba28a633d4f29	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751191.npz
toys	120904ddeead627711d25211998fd0e7067be2539572de0cf86a987d37ad516a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751192.npz
toys	683a4a48c236b9152f9019d7e3cb18adcf80a7a2f6b1f5b7dabde7436006f4d2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751193.npz
toys	ab6e8ce63e9a625c06e8cb3b6ae7060809fd9ffcfb15b3c66e896eacb2aba033	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751194.npz
toys	087e1475c4adbcba3eabcd42c530ca9681ccf38f8776455c23c1448b4139c832	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751195.npz
toys	6a3f93a7766e79b04c5c04d62f5aac24b9fdcb220c830d4999f69e255ec2b22f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751196.npz
toys	441b4c95f8c2e9e48ff5bc275061976cf2e6c9c1fff35572538212ac210ff8e0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751197.npz
toys	09443e9ce4e047c8c5549d7c58ed258bf01aeaae9331d589103d31df3a851166	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751198.npz
toys	f9cecabe8bc59f7627c5f970b896adbbad8c814d4addfd92ef3b23d492735378	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751199.npz
toys	64406a0582a5e073f5cd8d1f9dc1a6ec98acdff1c4120c1bb7748ac38b20bd98	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751200.npz
toys	688f249253d48ff7045b03f5ebb541edda0caf4936eb812f5868396e6c8c76de	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751201.npz
toys	8cc5688701473d43bd555236daf79c19d19c50c363e52d9b8265e934a87974f9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751202.npz
toys	4da8c99298920cd47da518d4cab625df8aa1abf9f17236390f1e018ca39a7800	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751203.npz
toys	d5b765148395abc172148767f00021b948e9d76476a1cbac9a5b050c16a59731	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751204.npz
toys	e47500d1603cddbbf15f61f84c328006b64bb2c255718f4b443d037a5834ddc6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751205.npz
toys	6a5628034524c810fce6dc29866a72d2d73bd5cd917e74d89c2d917cdd007b75	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751206.npz
toys	8386c133aa6e4307da56ebf7a1a175e8c5a704c93b5815e8e3979d271845b2a0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751207.npz
toys	7d7f199753d07f3a56f564931ba166dffde3220e61bd0e31eebac2cb4337bdf1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751208.npz
toys	b89617caa53fed3dec15f5d9ec7b41479e02af01a3b3f0787316e7443ad1a00a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751209.npz
toys	f9fb955b68b0a5bf3530730c4e32b027197408b4323776d10664652a8e64573d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751210.npz
toys	bfeb7e5463028bceb3a2f8b45a13157ba1f2909fe95e8a0658a263262e218489	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751211.npz
toys	4b6d05283d4193fde57e2b0f142c298a83bcd13ae2b487d691e3d6d1ddac16d1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751212.npz
toys	82efe3c14b3cdedd3eee3ccce4a70a6dbf3b968f9a06f29afd3e855621e47ce7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751213.npz
toys	1d187549aa963fe83f285fe739b24f4a023e163cc624964e66893426fc3cd23b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751214.npz
toys	44054930f44eb02feb10ecbebca8c9597d438a30beb47eb8185217902b958d5c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751215.npz
toys	1c4b860cedcbaf466fda662857313e24c6c1cc05390ab9b19618fdb9f5fb0582	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751216.npz
toys	e04d1a86d460d58fb66bb48b6ab1d146b2bd66cdf4d194a8171851da163a8bb2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751217.npz
toys	3a63d0672a368e3e19924e9003bcba2631ac3fc030f95d493ea410c7874291d5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751218.npz
toys	24f713d72600eeb2a57e67446d839e9db870dc775d52a3843af6621504dbc801	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751219.npz
toys	ec588ecd91ba79a48e99a69615d82b032e868a5b6889bcffc287e8e27a100f9f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751220.npz
toys	35ee27b064519fb5fd4e6dd689587a90874775361390f21e4d6e81e43c0694d8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751221.npz
toys	bfa01dbc01535385686df24771a03a66adc522c439aacec82922284652bd50cf	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751222.npz
toys	88a622425d9897cf8fc2c98ad58bbe0cd7be0c91ba6cbfe8c8f54139e9a919d4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751223.npz
toys	5e8af2b8d0829e6700cf9990010041df83a81a7cb79b0f24010888191e25eb79	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751224.npz
toys	e1acd2e1cb0685f78132287566b2d18899cae6c289f8fd48c3ab78d29280be43	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751225.npz
toys	16b43d2375e90d6afcb44b0e42873dab1ac8f732e4f1529c9399378aedefa0fb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751226.npz
toys	d879636c7d8ff49c41c3963c6d023692fb3657ce8ee36d4392c22d37c907350f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751227.npz
toys	133928004b694a8122fcd6628d086fa8e7ba2374cce584451f1e04231e38dd1a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751228.npz
toys	a391ead294f74e4ef485721222a7a7b21cf448077c1cd223a144b9a5874f69cd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751229.npz
toys	e198f95a0174b6343dfd127dab82b00e361187c70e55aad0c7ffcc2076c09c15	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751230.npz
toys	e37464d3ec3ec3540172b7b1658c5382d29addffec5381c02c9f51912804b9ad	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751231.npz
toys	2ab7d287e1089ba12e074273c92e35f7dd0facf47090301d7b59e47122475585	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751232.npz
toys	2433876a8d1f2bc35d9b475ac4b582ceffbf7473f4282a654ab0b1aec76baf13	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751233.npz
toys	280a885aaa631c3405d54f232b7da9f490fee841097a1dbdd896dd9daa07c72c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751234.npz
toys	9691c38e3f8c118606b031b75b71203fcbf97d294e96e787ee55e13718597852	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751235.npz
toys	e7f916ddb19e3948c865b44fdecf54ea4c399fb99171cdd843232af745c269a1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751236.npz
toys	ecc192867513e4476ec4f02d677042708cfedc4f49073f7d6465c9f98558c6ac	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751237.npz
toys	780827aee1746590159f86cc03d3f8883dd0ae830c1fcceeb31c05704e4dfd5a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751238.npz
toys	a55403f289ee61c1dae9dfb5055edb56f026dd020fbfe579ac4c04f99cb4d306	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751239.npz
toys	9f11e2f70e9d851ce68abf84cc4380b6d8bd5c5b66a871dc3ca305738daa05f4	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751240.npz
toys	403cc7fe403565c274f045aa4f1837384fca8153b0c25e2f7eb06682214578c1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751241.npz
toys	2df5fbcc913cead0143e5369617adc9bd6b69fce2c8f20303d525d8641236f21	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751242.npz
toys	76f01e69d8d73abe4f9b861f3ec8664937ec76dcfcadfe6fee38891e4bc8957e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751243.npz
toys	266e4c327fd776f2ef0ca768e1682e93ed9151c1f8243a5858446e755eca73a9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751244.npz
toys	602bf5db7686fdc397bf9dd0831c35afda687127e027ddb811dbd3a6ceeb6945	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751245.npz
toys	5aa9562a80ae1d84416577b1ed35f9b40c57956cc45f18350eb044559bb55f17	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751246.npz
toys	c7f451436770a23cb1b225b242658dc94c8ef0a618ec178fccc3efdc8456badd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751247.npz
toys	f9684432b808718c521b9c541c66483de0480a86f7dfc652173523364a769540	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751248.npz
toys	7adf0a7880d6ef22b6e94616b7f8c0ba73d283de4cfdd6f0378efeb2f190a5e2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751249.npz
toys	c92e4bf42295cd89f67b96853142cdfe439effe14f3b35059ec69d41a4edc7ae	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751250.npz
toys	e396ae880c72dd067dbde4ad35a1ea688cadcce0bb7e6e56dedd385b50c1e298	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751251.npz
toys	d28e39165260ee8abb0cabfe8ac66c09ebe3d2145db885ec8bd3ef83f61a835e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751252.npz
toys	621e825a3812a01659046f14651c368c73ccbab8662b0f014f638c29090ab777	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751253.npz
toys	66cf948f4d85dfa1ed83f77e0c294eebdcfa31fb6a383fcb19de37f12afd9c10	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751254.npz
toys	e1965392a466dd604102e262b119f4c526083d05174ef744e646a0252a1ab6ed	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751255.npz
toys	1f2edb4af992347d7abfc6f67c257c2f3bce390ff79957de28bb9ed00b8e7c48	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751256.npz
toys	26906ad458d3b78bcfe4918296c8dcafab1c0c2b12f08b98b67ef31303b66d74	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751257.npz
toys	783202c50998509d6e6a09311b666389d60758618d9b511019ec317fbee5490a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751258.npz
toys	a79a5da06775a8896c2225f25a855cc16379480426a76bfa3253e021eca559a9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751259.npz
toys	126dcfbc8b574b761d8d16c238463e1e2c48f54654e5917d53178d6908f5cb6b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751260.npz
toys	f269f17fc808c0315877fbc99ba71adaef61b986edae539d9640ff04bb6c84bd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751261.npz
toys	998227d2febca67858d8a983a9557c94e3f184158f0960a5c6bc4ce8769075dd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751262.npz
toys	d9367e6f199e8a4e050e75b18f1a518cd79dab309d228901323a8dd85664f198	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751263.npz
toys	b5dd984ad123038b6c6a7b18cf55b7500a4ac394db7a6027a8978d594f3f8395	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751264.npz
toys	f2022ff18c1a80497251a99462b6e738691a6f6b9ef3c9075dd075eb022d8837	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751265.npz
toys	31e85285318b0a2ba9c951011b66608b0b9815851337e9dffda4c7c914d70052	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751266.npz
toys	60209adb765b75ffcd0f85d3fbdb9658fc2873f7064ffc15a81e2b4a4fc162fb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751267.npz
toys	653bc7fe1bc79ad60053f070cc8ab5e8a35c34361ae1d8e0c939dcd21cf29c10	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751268.npz
toys	bba3b5539925a6ab172efb29d7ce532b721ed2c4b9405c2a44874b4eca802287	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751269.npz
toys	a7473601151a8e9440e90dd892301fa386d2568dab21915d6c926cb8026ac714	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751270.npz
toys	40a2283543dac7fd1fd30cd515f4ba6e3cec4d8d786df74f7bb501113398967d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751271.npz
toys	5f1ec1526f18061144da0a171d81aaa2f5dc6ae5826162da8ccc777d3243b0d9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751272.npz
toys	c85b1fdf5a34d4c43e9c5360dba89773e656fe22b92d8c6b66441b2f629b2b7f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751273.npz
toys	5afa283004758f9d91698f726ff86b35b0fc813d040641ef6307a2f80507a75d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751274.npz
toys	7a68feec3f228c634baaac47b4288085b575b020ad5b03c5a7f66bbc47bb3ace	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751275.npz
toys	39c377d6d52afa68701e8df390f9faa38b9c666e70c93c1245c5e8341ae553d6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751276.npz
toys	4a10123645fffcfb19c21eded0b15e2a088906d0848e46ec067cd27611d69343	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751277.npz
toys	6b2dab6cba1dfea1f2b92fee56d6b61ce413669d3cea10fa088aa0df59d056bd	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751278.npz
toys	c81f0a8ea236144f8ba9db1c78555470423e303b7893cde5fbae570444045b44	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751279.npz
toys	f1fe402bc879639359f742c530b5f75a18cc551ea6c0934a97f13c155fc92484	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751280.npz
toys	91c2eab7d79e04d40f3f3250f4a02c41302a82c46eb32dc88931344427afd979	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751281.npz
toys	5ce1ab278d57ff1d401f9a6fe070952db2fc8638cb99c51335dc3814c02de107	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751282.npz
toys	6b513809eb6ed465aac752228340512832db29026c6f7c3eb125f8c334e81239	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751283.npz
toys	5508c0d336ae2d3481f1849d5d370363584b760117ee68dc4374262a3edc90c1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751284.npz
toys	8f7dcdc0f3866bf0f34f5761b5be8ab017966abfddd68f3c7dae213f488f152b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751285.npz
toys	dc1f3589d0d759996f7fdbff605eba846dfc8f3feb5b2d9c3c13b9703cf447f6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751286.npz
toys	c3214e610edfe4bfbc46c96f5fd5b2fbd7ec859d1c43d51653a6f3ecf085844b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751287.npz
toys	ebf0c1c0f9351f44e839ef1fc7979a96582b39ca7624127e257881d3f0cdc8e5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751288.npz
toys	4ad95c5eb9ba41c56f28c02cc845d368d4d3e54c1fe8814a23c43c620762c2ac	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751289.npz
toys	aedddd8d945768ff9fbbeb12bf83e50820798112866acd9a818a1bfb0604bcc0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751290.npz
toys	c7a7baefd602d28f239783a853b4cac0ed86f2d3d9af707f8186fad4fbbf4a59	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751291.npz
toys	fd5d8139d7e53607e2f81ad0a70e72eee0c245649f15969a7e4b5110743047fb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751292.npz
toys	aed6a939c1a0c0fc3c85ec09a910486260552d5301e7569918d7841539dbde1e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751293.npz
toys	9487b5123935ff99ca7935fb1c6108d246f73f1f6a458305dbc86ff40f37ca06	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751294.npz
toys	897ae5ddb98d6ea793ca3b2fc24c206a3394914c53fbccc2c2378a2ed320851b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751295.npz
toys	55ba82dceca369e0b3f08f2828ff70055ae3405a8297190d9256786d4320886b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751296.npz
toys	a6604fbb1c6c779eae708d3888d0c24ac4e174c000c53b2ea9d8362d6b2ad6c5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751297.npz
toys	ede8bf36a677d79e3eff05f91dcfec1ddd56d21ed03b972c1612fbc3b014c3e6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751298.npz
toys	9e9083d1cbd8be3724263a2f1cabae510e49bc9cf6870daea060bfb52c5d7bb3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_toy_minus2_4751299.npz
extras	c0cbf6c54cf2b8ac1a715c6064373269936f2bd3f7385f918aa83221a4e46254	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_clipmean_all.npz
extras	128ad570c12b08c3bd8919defaaec7aa590d84e8730b9c98dde4332070f4aea8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_ar23_clipmean_minus2.npz
extras	48948d0e553155c2ef49663d670e32891b75f8f196c2a0c7ad8eec1b7670e94e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_data_control_Flux_0.npz
extras	64bef18932fca52135901c4e064139b9f32bca13e66dce75fd4814671de4f486	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_data_control_GEANT_Pion_0.npz
extras	1886d861cd9dcb319939537be008703ddffd9ec4cea6e2b6ddcf187f7f091139	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_data_control_MaRES_0.npz
extras	36c9c8427a312f591a9589b67e60c8c68899ae725c5b34e29f988a4f53771a2b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_data_control_setA_b1.npz
extras	175175edf3b95003a1cccf81e02dfbaa9024f7fe9af1d0e70e890df755faf751	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_clipmean_all.npz
extras	89510e949bbd7719931437c5434ab8d7aa53cbac4dfd21c28d1c2cecbc9bb5cb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/ll5d_g18_clipmean_minus2.npz
sidecars	2f56cacc22118289a7b72850ab33273682b9ad2033d3cdbcedf6af307feb2d1f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-block-61214607-814630.json
sidecars	f8b09789f1a9219b5d495158aaee5e92469f8f3b58ad05518205d66ef1d496e6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-block-61214609-419920.json
sidecars	2a81c9f3b29390963faf04ed3244ec617ae7417119e86f7b2ccacc281122f3f5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-block-61214609-419930.json
sidecars	050343496d0343cc45d0b9f736b352b509f0bedadf2c89bb3ba5df737833ab9d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-block-61214609-419933.json
sidecars	e18922629f59a6b8d2926eadeae1945b6a29bed38a3143da5a0fa7e12f33d35d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-block-61214609-419934.json
sidecars	9c930407769b12381b2d7579bc10cd5b4d20c6e937ef78949011b6d17c6b3f61	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-block-61214609-419944.json
sidecars	2ed2801dc81fe245c909fb4845be62eeb44904d8afacd7981faa100ec24f7fc8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-block-61214609-419946.json
sidecars	607ff02a30a3bb86ac91ee8bb7869d783a74dee310fe69dd10585da2b93d74f0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-block-61214609-419947.json
sidecars	eb528967edaea7bd86b3a60b921358ab96ec98676df86f52877c132cfa98bf88	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-block-61214609-419948.json
sidecars	53f99187536f8e92f71ab64fa5224e375c2ecdb367e15245871abd77718f13ba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-central-61184880-1892566.json
sidecars	fdb0275b1fc8199b7b8737e304eb7f1c0185205f81808c4490f8bb9992f307b3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-clipmean-61184880-1892597.json
sidecars	175a3437d76693332cfee71241e6458d6f3c7a8370c01ec3c8f3785e90a2390e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-seed-61214607-813696.json
sidecars	53f99187536f8e92f71ab64fa5224e375c2ecdb367e15245871abd77718f13ba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-stat-61184880-1894437.json
sidecars	aaca2882f4c1b2616eae72605dc54806bac44c8f764c8d8b806e59d4fa78d490	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-stat-61214609-436062.json
sidecars	170108b2b6e691ddf9f20319b1c9d29baa98e264e36882ccef94e515e5714b92	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-stat-61214610-626960.json
sidecars	170108b2b6e691ddf9f20319b1c9d29baa98e264e36882ccef94e515e5714b92	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-stat-61214610-626961.json
sidecars	37615994cd6c2afe1b9d24a7f60d2afdbe015479fc59e516f22a5e8c1eed5d0d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214610-626922.json
sidecars	05e9276fa84295e22e22b6eaf88ec737f952da1123f820a1478ba118182b9af9	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214610-626923.json
sidecars	c03cb8eb8972a3e1d7fa7c5c557a7b9a25c8e8db2d016ffb7c11c752496000be	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214610-626943.json
sidecars	b8fc0ffa4b19ef4c6a7d6cd46a275df23f6f224f60fa5ab229bc328b2fc37a49	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214610-626944.json
sidecars	f9f3858e5987e4559b96d0a5ea00721860ac7c45b66788b3a5155de019a279ad	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214610-626958.json
sidecars	b13bde2d5256bb7fc8d80c0766fd32ffd4c9007d1659029799dcdf5cc81285b2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214610-626959.json
sidecars	8932b3d41d27c77d72996268a54fa0b2de550edbdc723ae1af6548f2ed3dc0f8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214612-713900.json
sidecars	6e64cc146b5163860ff02123767e383e53b9b8e93355b1ec638e74a72f3e6d39	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214612-713917.json
sidecars	c798f2ef36f01b080f980d4dd68fa3f8fd1d86967015c481a9608e0717902f7c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214612-713922.json
sidecars	74e403c0e4e5272f1ab88d28205d18b3974fdcad1bd171aa5e58e375fb7b4969	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214612-713935.json
sidecars	d32eafdf4fe067887a7b5fdbed1dad72ebacc419f3272cd9db3e4f902e60382a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214612-713936.json
sidecars	e6579ecf0f4679cad520585f8e9c2d2edf17d6f396fb3125dd69227a42549617	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214612-713937.json
sidecars	2d2dbb3bca7e3bd9c16b38a4d75a0fcf78013119047e86c605077bbb5c4831f3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214612-713938.json
sidecars	3128bb85d873856f722806da8a7b8d13a86374c5008cc049c5be1e286e2f3665	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214612-713939.json
sidecars	82b22aa5239005279a977f909d28d52fc8d93fb71d5d3b8fb28e7c977ce370d5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214614-904526.json
sidecars	f3010bf23e8540346ae5a0fc353107cfc057a5232b4c42db36056f6ef2b8c185	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214614-904528.json
sidecars	dfaffeeafd1fb884bf7da2c778a8e5c13faf20d6d69bda9f16f88ee9feb65d06	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214614-904547.json
sidecars	14fc1a8232f9e0b49b8b093c0ae168b18dfdae3ecb80ea079d6d0b2a8f7ff2eb	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214614-904548.json
sidecars	768e1343d108cc8a3ff62b6fce2ba58648489a1f0f43826e1643adaf4244dab1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214614-904561.json
sidecars	013730bef553647fef0203d939bef9103a1f259bddbe877bebc1e0de3d079dae	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214614-904562.json
sidecars	f0f939409b89829b43436a7e3717d9d70b6ac94eaeafa1d480951a7f7148557f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214614-904563.json
sidecars	c7d590eb1d40d460b8b4b7c472fb2d416acb52d49015bf8b64b8f9136b41eb43	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214614-904564.json
sidecars	763ac4fd5a5ab35c4960738e7e1236aff8a141d9cf71a0fb21898ad7d955b241	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214615-1092219.json
sidecars	25fefa617607050cdd126c804816029515c7d74469e4a6814b7824618c48b46f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214615-1092220.json
sidecars	b2ba77e5f4f3bf9b998ca5c79e285a981f9c37e2afee18f488dc31b0b0dc26e5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214615-1092221.json
sidecars	bc1e54051a3249297f5778a93848db8cf3615c3b6d9a4f6d409716ac198fdbec	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214615-1092236.json
sidecars	24b84f203995886fb69537b65d6d8d5e06331761c68efe90949c758c148c7ed2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214615-1092237.json
sidecars	412ac771e7cff211345c1741e08903790b192f29bd280df2f9863e0cb7edc207	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214615-1092238.json
sidecars	92902f93e45c31f7bba67d4eb0be94fa6b083e7f66b5e19a064e2bce9056435c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214615-1092240.json
sidecars	91659ec4a6f0c486a623763a4f18df8bcd659553f75d551be38497f8ae6a1225	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-ar23-toy-61214615-1092241.json
sidecars	b2ea94a209f857feed11401208e9be33ed020d35297c78aed1e809277377948f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-data-control-61184880-1892565.json
sidecars	c1daf4cef358eb41aeaf9f7da4a36910222fb51281905608772a8940403156d8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-data-control-61184880-1892593.json
sidecars	a8ac5016a4b76579ea8e8ed936e60ce6f89c6dfebd6177e3bf2ef740f295b3db	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-data-control-61184880-1892595.json
sidecars	29e685c0f7eeff48e79f27fd54b5655341ee63eb1f7aee827334f8b5867a8632	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-data-control-61184880-1892596.json
sidecars	7709d2a68d97c46ca35a503168b1dbb55dc07ef2b10dbad21f7217407233c898	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-block-61214597-684539.json
sidecars	918d796de2770595fda3bf7ee5e1e2f45c7c927ca6418bd22174e8bdb7d0aa2d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-block-61214597-684540.json
sidecars	e355dcb2a5374700c2a5bd5c51d9b9cc48374c33a63b7ff7af14ae77da6b6ab7	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-block-61214597-684554.json
sidecars	3305cbc0aff2ff852b09e3b2e198be8f1cf04fa778540b424c4cfd594788fd00	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-block-61214597-684557.json
sidecars	96601e9b457fa9fe781ec4f9be6b08788400d33f3bc1154733472ab5c9232d26	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-block-61214597-684565.json
sidecars	3649571539375b480643efc8044235119f8af281a34274538df46d748e9f1b8c	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-block-61214597-684567.json
sidecars	2b405b18c33de360a21644d1a740dc73619a87db4371b8bcc19a2d09442b62ba	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-block-61214597-684568.json
sidecars	f872b30569eeb2208e22338a5592a19bdc7060857fd590d716887aba384e558b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-block-61214597-686201.json
sidecars	05407fa9d9be67f4d968f14b541886666f20e96cff627ce6217182af52913964	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-block-61214601-1906963.json
sidecars	fe4f582d368f806ac34fd17ba5700b4b75ea96cd578a6e81ba3c8dc77162f965	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-central-61184880-1892570.json
sidecars	f5d16be2cfcc74af43f9e1cb00797d6be3a34b23e534f38acf1c9883bf927249	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-clipmean-61184880-1892589.json
sidecars	61e850781c9171e87bc3fc30d989825ea3f79c02a2c55a5ab05e1bbfca5a41f8	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-seed-61214597-684561.json
sidecars	9bb58430f7676962b31ab6f59f1e36be56628673d87ea15b78de3b706001d40a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-stat-61214601-1906944.json
sidecars	9bb58430f7676962b31ab6f59f1e36be56628673d87ea15b78de3b706001d40a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-stat-61214601-1906975.json
sidecars	623449db521933dd55a10215839d9686c8fa79fd2fc7a1c96c74d7713797b94a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-stat-61214601-1917133.json
sidecars	66ecdd55ee5fab03bacd47fcab9585677e78ecf16276748d7b59cd45dceb7c9d	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61184880-1894634.json
sidecars	e07c2af3518afa7a10a9d506b7020f040bc98602b7b185b6fe037e58a86230fa	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61184880-1894712.json
sidecars	497f38cfb997ecaf920a2662ab2de48cd83b5654c5330006ab96e14b193e4509	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214601-1906943.json
sidecars	3350fb53bdc533e5879501e6d78bef4356e85e98bf721cd11475ebab64375681	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214601-1906960.json
sidecars	11aa6fd8adaf998b587ec94139cf03bd3fe48fa57b665ba53511bf4dc52fde70	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214601-1906969.json
sidecars	30b05ab1a73e88332b48c4d9d4918c323302307de5043719427cdb0d9c8ad648	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214601-1906972.json
sidecars	b2f9ae19acebb414979d175b4f1380a774ea1789fff258865416502b3c3586c0	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214601-1906974.json
sidecars	96acc7fe082cd55e27c10cb144b560f40f1800658cf47c8dec8f25d41479dd12	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214601-1922472.json
sidecars	a66c2ec72812f37563196c6c1233710b525a689dfbe0515faf7c2319e4754003	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214604-571052.json
sidecars	9651f6676c4e8efcee5161b72784a945bee34dc3471572de4810317b583849e1	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214604-571053.json
sidecars	a2e378983640079f21850b3bc0ccc4ba4a902506d91dbc7da5fd0d36aaa08995	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214604-571054.json
sidecars	50c07786d92734ff5d3a46ff6c045c39af2668a12a1c04590d835f7a50f61f0f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214604-571055.json
sidecars	620631f273f708600851c93c707eae48659357ecfadc1d4f5821182e0f266f0e	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214604-571067.json
sidecars	5474c1f686884a45ad13cc2b73823e885fe286018c211c81cb8c33239d4b8023	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214604-571069.json
sidecars	77f8d58d2c8c62cd5c8b85e6a5023add9273a429c85e1ac0997cd381ba67793b	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214604-571070.json
sidecars	4bfec83c7b16c3c65e53ff8b455c31af2a7e7882165f972ffb923bf218b0890a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214604-571071.json
sidecars	e28ce36f619a0c9c3f9b41947f8237f736aecb7309f694eb475354ef29c10161	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214605-733291.json
sidecars	8bc280ad34298b0308ebf09d119403544a4235ccdf6b50638a9f2e64a1a01e93	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214605-733293.json
sidecars	2dd32b0e965e1f57c4a0bdc79aa4e8703819dec6e8d970f4d41abbc2e9387240	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214605-733300.json
sidecars	b8a757599a48f2562fab4322d81b6c96821f14bc9688e98f9a1579e2c647861a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214605-733309.json
sidecars	b2d0fdf4151dfaca93f96fc06f5842fe58a08eed8b24aa751111ae3a4314e282	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214605-733314.json
sidecars	4ef9b7651f61255a38ea97390f30194195a8a8c10c95790456e04ae68991f7d2	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214605-733316.json
sidecars	d18e0deb56ec29909969f197ba00ca60fa1779cd44ee293681407fc180d498ca	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214605-733317.json
sidecars	604b5e7834cab840bd19d4122eb2654a18f6e20d380525c005e39c6244e2aa84	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214605-733318.json
sidecars	06cfec5830a8f989521e146e7f93c9a1b17ff0b6ea23caf7823f96b2316b2b3a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214607-805732.json
sidecars	174e7b8304356d91c21cc638741116523591a161963163830cc4e2492edac5ff	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214607-805749.json
sidecars	389ee21d2a90d699214cef2c1c6a4493fdd01c40b87454ac0ee6506e0440fbe3	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214607-805750.json
sidecars	6056bc7eb158a73d625e7b9cc0edb0c1d6050b44c6b9686d7d54dec52cc9e66a	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214607-805753.json
sidecars	d26d792c220120a1d6811ae64ffbe6584e8f19a0535d5551350207066fae33a6	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214607-805763.json
sidecars	2bc2022a14415992cdea7384c67be8a7e4bb8c06807e8d537440a18548331230	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214607-805764.json
sidecars	26f510bb5440a8e3f3069f36b078eab95ada458cc2bee5fc643074b31403f33f	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214607-805765.json
sidecars	d15765b31f1285e3859b37208ace9e1b5ed80362740567170d617ccc5362e8d5	/pscratch/sd/j/josephrb/ll5d-unfolds-r2/atime-g18-toy-61214607-805766.json
