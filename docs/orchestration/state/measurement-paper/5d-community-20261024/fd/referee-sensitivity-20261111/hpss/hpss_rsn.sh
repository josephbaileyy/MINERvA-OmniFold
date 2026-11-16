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
OUT=/pscratch/sd/j/josephrb/hpss-rsn-20261111
H=/home/j/josephrb/mnv-rsn-inputs-20261111
W=/dev/shm/josephrb-hpss-rsn
LIST_SHA=0dafaac8e3664875f496974fb79f73e319ada7647eb5106dbe6626cefa9d99c6
GROUPS_IN_ORDER="pvl_prep pvl_products cpl_block"
N_ROWS=67
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
pvl_prep	9d6837f1eefb6eb09ba5187f9ae9547667a1675237a956e75446b0060b2a34de	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/cells/L-3D.json
pvl_prep	2fb349ad62eb7b146db80601771ac347c287ad60969121b9e22cd2bf929b3390	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/cells/L-4D.json
pvl_prep	d1486ea4f3a9aee7df2eab0be481412961adff0afd9df164e5622fff74054fa7	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/cells/L-5D-PV.json
pvl_prep	1bb6557eb1670d15406592c8b1ae442cf0e7c5d3923ee2767bed5f572aaeafba	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/cells/L-EW.json
pvl_prep	f4165362f000b08b218373b67f7754f450ecac803979cc01882435b6289628a4	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-3D/genie_mec.json
pvl_prep	0e0248024eeda68f8dc875cd0cda55a9fe6a3637384985e7526db477ad93d36d	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-3D/genie_mec_sq.json
pvl_prep	919b1d5902344b58b6c5464641cbfb1001ea09eb844dee1303b185b7ace1cc10	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-3D/gibuu.json
pvl_prep	79be9ecf83a5dc07426ceb78e6d0c0e6bbef2d6572014d4346727e3aafb309c2	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-3D/gibuu_sq.json
pvl_prep	8167163d427dd5803676e61eada276419f2f152c887a59c6175adadae6fe5e3b	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-3D/nuwro.json
pvl_prep	635419c89728fac9a5c1822294d692dcbc13cf07a676514c669226d0283d7454	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-3D/nuwro_sq.json
pvl_prep	b7504b4e6c15ee66987572fd946dd3cfab3a0d0d4fa88899ad38864076bb38bd	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-3D/ratios.json
pvl_prep	57cdd9304b2eb1ac2d0ea57b9ebc7cc7fe99d603a0f3798990025b5ae244134e	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-3D/tune_v1.json
pvl_prep	d7d4a366e55470c362deba5b8383270f8f4cd25e81081eac3a120169911daa97	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-4D/genie_mec.json
pvl_prep	1b7e9c146ef3d05ce3d287e0d0714a1732b63115b91ddff8299be238c572014f	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-4D/genie_mec_sq.json
pvl_prep	81189fbf798dc9fc6264c22e8f00577306e0c0c2de85329b2666c7bf7fc17a50	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-4D/gibuu.json
pvl_prep	f1e404080b74e2871057ee04b7872d6b2f9ee2f29b1ad5c272d445ef2d5bc3c4	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-4D/gibuu_sq.json
pvl_prep	f56102de705fcf901587de96fa3261d7fb734c39f828fda07f67beccdeec80ce	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-4D/nuwro.json
pvl_prep	9e11de6e71e4081f53476fffdff68297fae108b864c44cd5ea9a48f48e26f0b0	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-4D/nuwro_sq.json
pvl_prep	03e21baa7bc46462b9677e1db81a278679580710aab17183107efc49e90a2c25	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-4D/ratios.json
pvl_prep	c80166ee02fe17bb85d10be1fa80f61ae8a644ca51107c52c1e1e02768e3db83	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-4D/tune_v1.json
pvl_prep	8d0e0f42911240f24118c1c731ce6d06a9bd52d0e025202a1ece9da0b54af64f	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-5D-PV/genie_mec.json
pvl_prep	7fb9ecc3766929eb11487305d67e647a78a713dd883feb0327a39de4e583b85f	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-5D-PV/genie_mec_sq.json
pvl_prep	52438000ab8746a09b8118f3c4cf718fece7f77312cb3c3d62348f7073744e35	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-5D-PV/gibuu.json
pvl_prep	cc45a0094bb33005dc23dbd922b103b42208df0b9e20af8008a24ff3aa81fdaa	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-5D-PV/gibuu_sq.json
pvl_prep	38e47eb6b6ac63f6657022ae0cc5a2b5eaffc6a2e503735ce7222275771fea6e	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-5D-PV/nuwro.json
pvl_prep	c00594596ba68ccb3c0526c1dd33a8e5ffc6201714ebc5803fdcba66e6dc9152	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-5D-PV/nuwro_sq.json
pvl_prep	925cbd8d7655d3f7c407488dd3157cc6dbe5ded934a37927b678cf5e4b923c58	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-5D-PV/ratios.json
pvl_prep	13bb1eae4ce0db4023bb29a5b98ca8b7e1e22288a1547f6a31a735fa1445435b	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-5D-PV/tune_v1.json
pvl_prep	466a646d178963d5861f2496b105a76c7a22f75a6ca57e2f1930fd2b47589827	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-EW/genie_mec.json
pvl_prep	d197550fed19a47afe8a12a96fc5d756c1a8ab133e6966789ef44203d8a788f4	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-EW/genie_mec_sq.json
pvl_prep	6eecde2bdf52701db14f6bb9af7604dac67eef4ae7c2eb942c72460cb551fec0	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-EW/gibuu.json
pvl_prep	94364d17003a972b1532c3e3418d1d32de5c28aa6dbac3c5770f4f7be9f9120c	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-EW/gibuu_sq.json
pvl_prep	d1e06de21ea99c2e91a906792ed4cc35372c189d651a0333f2c7e3c8a3129b08	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-EW/nuwro.json
pvl_prep	f2011a2d6e86d7073b2ed923fddd1f83d24c6438cd774325e13c9d5fd528b158	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-EW/nuwro_sq.json
pvl_prep	2596856da66df77586acf49d131ea326fab9d7640463cfb1e7a5184219de710b	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-EW/ratios.json
pvl_prep	8cae4bb987b12f0096d28fe7b9e5364803d373e26f03504f45654a0318039208	/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-EW/tune_v1.json
pvl_products	ce5db9c55220cc2334770354ad36bac48e861df998c3903a8b30e017dc2ad5af	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-3D_e_closure_nuwro.npz
pvl_products	aab2a1dcbabb39f41e150d9236eab9b3000197c4b52361d6dc168661e3113cc2	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-3D_e_closure_tune_v1.npz
pvl_products	b957879156acf917bacf2142e7f39b17dae09ac4430964c1a28cfccb022d0e5c	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-3D_e_genie_mec.npz
pvl_products	bc30a1e23b17761e279e7a7399d77b805fd10a3c698bbe63306f127d3d2c0037	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-3D_e_gibuu.npz
pvl_products	8ef349b0f1c938863961a8e95f9209cbb5a03b57fffbe10b7731f94d599442c0	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-3D_e_nuwro.npz
pvl_products	2f62e75a2eff2634b8afcfb3a4e8b3d4cc5d7c6e202b39c973e68b294fe697eb	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-3D_e_tune_v1.npz
pvl_products	6ab3addf582047172b28902fed79f148c23734c035a34735d2a510a61ccc1fb1	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-4D_e_closure_nuwro.npz
pvl_products	f4ec184af764aa6fe8adcf34b021e89e58c9021a1585ddbbb30077bad1261db3	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-4D_e_closure_tune_v1.npz
pvl_products	883271a1c1218e2f47e6145b593b2191825a84cb553add058f56cf749423a669	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-4D_e_genie_mec.npz
pvl_products	25316558322b184c2be8a9fe7ba69487830f82212f608a76520a458556c10b9c	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-4D_e_gibuu.npz
pvl_products	39c6fc381d30e8f7ee2c08bf9d25ae04c099452ba33da105c71d5856be7933ee	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-4D_e_nuwro.npz
pvl_products	1f835bf3bf6f92a6dd7370811c6c945c79d09a5a68ac9ff5ea9879b1cf44053f	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-4D_e_tune_v1.npz
pvl_products	fff9030e7fd63c538b27c58f2a35417b5d28c3d2f6de2880219b181812215182	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-5D-PV_e_closure_nuwro.npz
pvl_products	eb3e218866dd36e093c85e85a791f8dd8de1491f4ad0694924644b01c8e55f08	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-5D-PV_e_closure_tune_v1.npz
pvl_products	bdff9193b04f17c4aa9d97e7d9c26221b03dc8c9b0d2376cd775e6b195b749c5	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-5D-PV_e_genie_mec.npz
pvl_products	bdf331570daeb3dc56d6096e2c39ca3e7a6091339680eb58034ee9a14c82f3c3	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-5D-PV_e_gibuu.npz
pvl_products	caf6eee726ddb128d26cf74fad2a2b4e69273607a2a0e1e4a48750766bddc66f	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-5D-PV_e_nuwro.npz
pvl_products	dbe9a95e746fba127811182e9a352f6dc243d78ff699e803611b5deedbcb0f4f	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-5D-PV_e_tune_v1.npz
pvl_products	c42b54de2580348070ccf0f1cc353d0f792fefc596be27fcabc8cc46b770c99c	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-EW_c_all_tune_v1.npz
pvl_products	7d522f30798b26b3efc06d7d33e63809ab58340059cb8c56f7fb22e06959fffd	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-EW_c_genie_mec.npz
pvl_products	1a56525dc457d3f0398c619c176a7c22263c7b1b017145a5326c227c845a09e7	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-EW_c_gibuu.npz
pvl_products	d5bcaf9698631a81dfe007c4df9a51fc1cb8696c4c92191bec9e73fb83d34db5	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-EW_c_nuwro.npz
pvl_products	ad045bcd70a8561716dfc6be3bc711b508e24863628bc835bdc3867f55d80c79	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-EW_c_tune_v1.npz
pvl_products	d5928d463ab5e675dfbac2f226b61dd847f7d8ed4ad56a1cbc89b71eafe0d340	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-EW_e_all_tune_v1.npz
pvl_products	71b15472da29043d5e0a5e829e38b07e0e3060ccc8cb536b07a233b037bde6a9	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-EW_e_closure_nuwro.npz
pvl_products	a9181eee3cff1ecb56e2f1ad5d4b9665ca68a6aaa7e096c13e141581523264b3	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-EW_e_closure_tune_v1.npz
pvl_products	c41225324df0a2758732ebf4f3474a088eeaacab0271f059b8db7f6e92efa043	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-EW_e_genie_mec.npz
pvl_products	568ad2ee734eccc4d9fe5400f37c581f105f6c880bc8997f25bc613f701a27ea	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-EW_e_gibuu.npz
pvl_products	9dfbcfd06593b7590620acf2b651c537f97c5d5d771ed480cba58ce3a39285d4	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-EW_e_nuwro.npz
pvl_products	a1b99897e3b646883580a68184b9e338e34c5c7ccac16912bfb2366ff0ba4068	/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-EW_e_tune_v1.npz
cpl_block	d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f	/pscratch/sd/j/josephrb/fd-ct-5b-addition-20261031/with/block/cpl_block.npz
