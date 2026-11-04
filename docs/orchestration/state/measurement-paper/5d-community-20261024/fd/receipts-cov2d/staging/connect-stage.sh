#!/bin/bash
# COV2D connect STAGE: $CV and the 10 active laterals staged from CFS to this lane's own new pscratch directory, on a
# DTN, at 0 node-h (COV2D-DECLARATION.md §8 "Lateral I/O", §7; COV2D-BINDING-1.md ruling 1: "control (2a) on a login
# node and staging from a DTN, next"). Part B's route (re2b_dtn_hash.sh), with (c)'s §7 rule added: every source is
# read through O_NOATIME and its atime is checked unchanged.
#   1. The quota is re-read with `lfs quota` on /pscratch (myquota is not installed on the DTNs). STOP if used plus the
#      11 sources' bytes would exceed 90 % of the soft quota. It is re-read after.
#   2. The CFS SHA256SUMS beside the laterals must hash, through O_NOATIME, to its pinned 73775251... (part B's
#      LAT_SUMS_SHA). Each of the 10 laterals' rows must equal part B's committed DTN record (inputs.stat, 89595b3e...),
#      so two independent records agree before anything is copied. $CV's digest is CV_SHA, 43f8cc16....
#   3. Each copy is written as .partial, re-read through O_NOATIME and hashed. Its stat must agree before and after,
#      its sha256 must equal the declared digest (the SHA256SUMS row, or CV_SHA), and only then is it renamed and made
#      read-only (0440). The record is $T/stage/inputs.stat, in part B's format "sha256 size mtime inode path".
# Nothing is written to CFS. No $UNI copy (§7). A failed copy stays as .partial for the director.
# Run on dtn01: setsid nohup bash /pscratch/sd/j/josephrb/cov2d-stage-20261104.sh >/dev/null 2>&1 </dev/null &
T=/pscratch/sd/j/josephrb/cov2d-inputs-20261104; L=$T/stage
CFS_CV=/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root
CFS_ACT=/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012/active_universe_5d_standard_merged
CV_SHA=43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df
LAT_SUMS_SHA=73775251f377a35b86c5d9433d1db63d65267525b9261f773064a1e9d17764f6
declare -A PARTB=(   # part B's DTN record of each lateral's copy (re2/run/partb_readout/preflight/inputs.stat)
  [BeamAngleX_0]=38b9fc307eabd864cd0fd663679b51fb2e6d064672410af6b3cf8b0a7e161ed5
  [BeamAngleX_1]=0e0491a624c2d64c6fa3fde271940f0cfa9acb2d08b72cdf1e21e1c15903c3f2
  [BeamAngleY_0]=058746fdb29aa2cc0e3db82e7be42648cd7ce43b8603e96e444111546949ecf6
  [BeamAngleY_1]=3bca6a458336c7b4b2250ccbcdc8ca0ac26d416ac4604114f5dfffe0fece2b0e
  [MuonResolution_0]=839ab9c51bdc69b13e340d5fdc8fd21968bfcc7a62deeb3db529d5f2fc4a6d5d
  [MuonResolution_1]=3330800629d536a94d37d91941089620ca90af228c64f43b4ed633a97550644f
  [Muon_Energy_MINERvA_0]=533037d27e0b5e38d778c935b7a44f5e30e0a1afb81870c8b063303859986bfe
  [Muon_Energy_MINERvA_1]=90a1d7b78d6deed51499e11ae735f09438dbf3d85c4a463c18fae441b6668ab2
  [Muon_Energy_MINOS_0]=f105f68193cc80d125fe272588d3223e9df57cd2e9f720e0853dbd712f52a87a
  [Muon_Energy_MINOS_1]=f2e67fd6c986f0a7d45eb894c1640c7d8fb48af83dbce37122d6946ae4aedfa0)
LATERALS="BeamAngleX_0 BeamAngleX_1 BeamAngleY_0 BeamAngleY_1 MuonResolution_0 MuonResolution_1
          Muon_Energy_MINERvA_0 Muon_Energy_MINERvA_1 Muon_Energy_MINOS_0 Muon_Energy_MINOS_1"
stop() { echo "STOP $*"; echo "STAGE FAIL"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit 2; }
case "$(hostname)" in dtn*) ;; *) echo "STOP run on a DTN, not $(hostname)"; exit 2 ;; esac
[ -e "$T" ] && { echo "STOP $T exists"; exit 2; }
mkdir "$T" "$T/laterals" "$L" || exit 2
exec >> "$L/connect-stage.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
cat > "$L/cov2d_stage.py" <<'PYEOF'
"""COV2D staging (COV2D-DECLARATION.md §8, "Lateral I/O"; §7): $CV and the 10 active laterals copied from CFS to this
lane's own new pscratch directory, on a DTN. Each source is read through O_NOATIME (§7: everything but the bound
driver reads that way), and its atime is checked unchanged. Each copy is written as <name>.partial, flushed, re-read
through O_NOATIME and hashed. Its stat must agree before and after the hash, and its sha256 must equal the declared
digest: the CFS SHA256SUMS row for a lateral, CV_SHA for $CV. Then it is renamed and made read-only (0440).

  python3 cov2d_stage.py <manifest tsv: source<TAB>destination<TAB>sha256> <record out> [workers]

The record has part B's format, "sha256 size mtime inode path", one row per copy, in manifest order. Exit 0 when
every copy passes, 4 on any failure. A failed copy is left as <name>.partial for the director and never renamed.
"""
from __future__ import annotations

import hashlib
import os
import sys
from concurrent.futures import ThreadPoolExecutor

CHUNK = 64 << 20


def sha256_noatime(path: str) -> str:
    h = hashlib.sha256()
    fd = os.open(path, os.O_RDONLY | os.O_NOATIME)
    try:
        while True:
            b = os.read(fd, CHUNK)
            if not b:
                break
            h.update(b)
    finally:
        os.close(fd)
    return h.hexdigest()


def stat3(path: str) -> str:
    s = os.stat(path)
    return f"{s.st_size} {int(s.st_mtime)} {s.st_ino}"


def one(src: str, dst: str, want: str) -> tuple[bool, str, str]:
    """Copy, hash and seal one file. Returns (ok, record row or "", log line)."""
    part = dst + ".partial"
    a0 = os.stat(src).st_atime_ns
    fi = os.open(src, os.O_RDONLY | os.O_NOATIME)
    fo = os.open(part, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o640)
    try:
        while True:
            b = os.read(fi, CHUNK)
            if not b:
                break
            view = memoryview(b)
            while view:
                view = view[os.write(fo, view):]
        os.fsync(fo)
    finally:
        os.close(fi)
        os.close(fo)
    a1 = os.stat(src).st_atime_ns
    before = stat3(part)
    got = sha256_noatime(part)
    after = stat3(part)
    src_size = os.stat(src).st_size
    log = (f"{os.path.basename(dst)}: src_atime_ns {a0} -> {a1}; size src {src_size} copy {before.split()[0]}; "
           f"sha256 {got}; declared {want}")
    if a1 != a0:
        return False, "", log + "; FAIL the source's atime moved"
    if before != after:
        return False, "", log + "; FAIL the copy changed while hashed"
    if int(before.split()[0]) != src_size:
        return False, "", log + "; FAIL size differs from the source"
    if got != want:
        return False, "", log + "; FAIL sha256 differs from the declared digest"
    os.rename(part, dst)
    os.chmod(dst, 0o440)
    return True, f"{got} {stat3(dst)} {dst}", log + "; ok"


def main(argv: list[str]) -> int:
    manifest, record = argv[0], argv[1]
    workers = int(argv[2]) if len(argv) > 2 else 4
    rows = [line.rstrip("\n").split("\t") for line in open(manifest) if line.strip()]
    if any(len(r) != 3 or len(r[2]) != 64 for r in rows):
        print("REFUSE the manifest needs source, destination and a 64-hex sha256 on every row")
        return 4
    if os.path.exists(record):
        print(f"REFUSE {record} exists")
        return 4
    for _, dst, _ in rows:
        if os.path.exists(dst) or os.path.exists(dst + ".partial"):
            print(f"REFUSE {dst} or its .partial exists")
            return 4
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda r: one(*r), rows))
    for ok, _, log in results:
        print(log, flush=True)
    good = [row for ok, row, _ in results if ok]
    if len(good) != len(rows):
        print(f"STAGE FAIL {len(rows) - len(good)} of {len(rows)} copies failed; no record written")
        return 4
    with open(record + ".partial", "w") as f:
        f.write("\n".join(good) + "\n")
    os.rename(record + ".partial", record)
    os.chmod(record, 0o440)
    print(f"STAGE PASS {len(good)} of {len(rows)} copies; record {record} sha256 {sha256_noatime(record)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
PYEOF
echo "stager sha256=$(sha256sum "$L/cov2d_stage.py" | cut -c1-64)"
python3 -c "import sys, os; print('python', sys.version.split()[0], 'O_NOATIME', hasattr(os, 'O_NOATIME'))"
quota() {  # used and soft-quota KiB on /pscratch, from lfs
  lfs quota -u "$(id -un)" /pscratch | awk '$1 == "/pscratch" {gsub(/\*/, "", $2); print $2, $3}'
}
echo "== quota before"
lfs quota -u "$(id -un)" /pscratch
read -r USED QUOTA <<< "$(quota)"
NEED=$(stat -c %s "$CFS_CV" $(for lat in $LATERALS; do echo "$CFS_ACT/runEventLoopOmniFold_5D_MEFHC_active_$lat.root"; done) \
  | awk '{s += $1} END {printf "%d", s / 1024}')
awk -v u="$USED" -v q="$QUOTA" -v n="$NEED" 'BEGIN {printf "used %.2f %%, staging %d KiB, projected %.2f %% of the soft quota\n", 100*u/q, n, 100*(u+n)/q}'
awk -v u="$USED" -v q="$QUOTA" -v n="$NEED" 'BEGIN {exit !(q > 0 && (u + n) <= 0.90 * q)}' || stop "the projected quota is above 90 % (or unread)"
echo "== SHA256SUMS"
python3 -c "
import os, sys
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOATIME); data = b''
while True:
    b = os.read(fd, 1 << 20)
    if not b: break
    data += b
os.close(fd); sys.stdout.buffer.write(data)" "$CFS_ACT/SHA256SUMS" > "$L/SHA256SUMS.copy" || stop "read SHA256SUMS"
got=$(sha256sum "$L/SHA256SUMS.copy" | cut -c1-64); echo "SHA256SUMS sha256=$got (pinned $LAT_SUMS_SHA)"
[ "$got" = "$LAT_SUMS_SHA" ] || stop "SHA256SUMS is not the pinned file"
: > "$L/manifest.tsv"
printf '%s\t%s\t%s\n' "$CFS_CV" "$T/runEventLoopOmniFold_MEFHC.root" "$CV_SHA" >> "$L/manifest.tsv"
for lat in $LATERALS; do
  f=runEventLoopOmniFold_5D_MEFHC_active_$lat.root
  want=$(awk -v f="$f" '$2 == f {print $1}' "$L/SHA256SUMS.copy")
  [ "$(awk -v f="$f" '$2 == f' "$L/SHA256SUMS.copy" | grep -c .)" = 1 ] || stop "not exactly one SHA256SUMS row for $f"
  [ "$want" = "${PARTB[$lat]}" ] || stop "$f: SHA256SUMS $want != part B's record ${PARTB[$lat]}"
  printf '%s\t%s\t%s\n' "$CFS_ACT/$f" "$T/laterals/$f" "$want" >> "$L/manifest.tsv"
done
echo "manifest: $(grep -c . "$L/manifest.tsv") rows; SHA256SUMS agrees with part B's record on all 10 laterals"
echo "== stage"
nice -n 19 python3 -B "$L/cov2d_stage.py" "$L/manifest.tsv" "$L/inputs.stat" 4; rc=$?
echo "stager rc=$rc"
echo "== quota after"
lfs quota -u "$(id -un)" /pscratch
read -r USED2 QUOTA2 <<< "$(quota)"
awk -v u="$USED2" -v q="$QUOTA2" 'BEGIN {printf "used %.2f %% of the soft quota\n", 100*u/q}'
ls -la "$T" "$T/laterals"; du -sh "$T"
[ "$rc" = 0 ] && [ "$(grep -c . "$L/inputs.stat" 2>/dev/null)" = 11 ] && echo "STAGE PASS" || echo "STAGE FAIL"
echo "end=$(date -u +%FT%TZ)"
echo DONE
