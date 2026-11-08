#!/bin/bash
# Band diagnosis, P0: the stat-only connect (FD-1B-BAND-DIAGNOSIS-BINDING-1.md rulings 2, 4 and 5; declaration section 6),
# on a login node at 0 node-h, from a fresh clone at M = 83ac32fb with empty porcelain. It stats every source the run
# reads (Part 1's staged copies and products, and the in-place inputs) and records each one's realpath. It reads no
# file content: stat, lstat and readlink only. Ruling 4: every source's realpath and inode are compared with ENS1's
# committed stage-2 input list (stage2-inputs-stat.txt, #940, in the clone at M), whose paths are realpath'd here the
# same way; the branch (SHARED or NONE) is decided over the ruling's in-place sources (the inputs npz, the background
# dump and the 8 detector weight sets). The fence is recorded (cov2d-*, ens1_*, rs1_*, fd1b_bdg_*). The source list
# comes from the bound code at M. Everything local is under the literal root /dev/shm/limres-bdg-p0-20261108 (refused
# if it exists), removed by its literal path at exit. Launched from a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
M=83ac32fb5024026ac6c51c0621d5ae9ff9073370
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
finish() { echo "== bdg-p0 rc=$1 $(date -u +%FT%TZ)"; rm -rf -- /dev/shm/limres-bdg-p0-20261108; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node"; rm -f -- "$SELF"; exit 9 ;; esac
[ ! -e /dev/shm/limres-bdg-p0-20261108 ] || { echo "STOP: /dev/shm/limres-bdg-p0-20261108 exists"; rm -f -- "$SELF"; exit 9; }
mkdir /dev/shm/limres-bdg-p0-20261108 || { rm -f -- "$SELF"; exit 9; }
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== fence (recorded; P0 reads no content)"
fence=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
echo "squeue rc=$frc"
for fam in cov2d- ens1_ rs1_ fd1b_bdg_; do
  echo "$fam* rows: [$(printf '%s\n' "$fence" | awk -F'|' -v f="$fam" 'index($2, f) == 1')]"
done
git clone --quiet --filter=blob:none --no-checkout https://github.com/josephbaileyy/MINERvA-OmniFold.git \
  /dev/shm/limres-bdg-p0-20261108/repo || { echo "STOP: clone failed"; finish 5; }
git -C /dev/shm/limres-bdg-p0-20261108/repo -c advice.detachedHead=false checkout --quiet "$M" || { echo "STOP: checkout"; finish 5; }
head=$(git -C /dev/shm/limres-bdg-p0-20261108/repo rev-parse HEAD); porc=$(git -C /dev/shm/limres-bdg-p0-20261108/repo status --porcelain | wc -l)
echo "HEAD $head; porcelain lines $porc"; [ "$head" = "$M" ] && [ "$porc" -eq 0 ] || { echo "STOP: clone not M clean"; finish 5; }
ENS1=/dev/shm/limres-bdg-p0-20261108/repo/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rounding-stability-20261106/ensemble/receipts/stage1-a1-analysis/stage2-inputs/stage2-inputs-stat.txt
echo "ENS1 stage-2 list sha256 $(sha256sum "$ENS1" | cut -d' ' -f1); rows $(grep -vc '^#' "$ENS1")"
cd /dev/shm/limres-bdg-p0-20261108/repo/nd-unfolding || finish 5
# The source list, from the bound code: kind|role|path. weight_keys() tests a file's existence (a stat).
env -u PYTHONPATH "$PY" -B - > /dev/shm/limres-bdg-p0-20261108/paths.txt <<'PYEOF' || { echo "STOP: source list"; finish 5; }
from pathlib import Path
import fd_1b_band_diag as d, fd_1b_precheck_fd as pfd, s5p_universe as s5p
P = "/pscratch/sd/j/josephrb"
V = Path(f"{P}/fd-1b-precheck-fd-20261107")
us = d.detector_universes()
assert len(us) == 8, us
rows = [("staged", "staged-json", V / "stage" / "staged.json")]
rows += [("staged", "derivation", V / "stage" / "derivation" / f"fd1b_derivation_{u}.npz") for u in ["CV"] + us]
rows += [("staged", "s1-assembly", V / "stage" / "s1" / "s1_assembly.npz")]
rows += [("part1", f"product-{m}", V / "unf" / f"{pfd.TAG}_{m}_{u}.npz") for m in pfd.MODES for u in ["CV"] + us]
rows += [("inplace", "inputs-npz", Path(f"{P}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz")),
         ("inplace", "bkg-dump", Path(f"{P}/s5c-20260924/runs/p2/bkg_dump.npz")),
         ("inplace-other", "pins", Path(f"{P}/fd-1b-20261030/pins.json"))]
det = Path(f"{P}/s5p-20260926/bank_detector")
for u in us:
    keys = s5p.weight_keys(det, u)
    assert keys == ("wt", "wr", "denom_nd", "bkgw"), (u, keys)
    rows += [("inplace", f"weights-{u}", det / f"{u}_{k}.npy") for k in keys]
for r in rows:
    print("|".join(map(str, r)))
PYEOF
L=/dev/shm/limres-bdg-p0-20261108/paths.txt
echo "sources $(wc -l < "$L"): staged $(grep -c '^staged|' "$L"), Part 1 products $(grep -c '^part1|' "$L"), in place (ruling 4) $(grep -c '^inplace|' "$L"), other in place $(grep -c '^inplace-other|' "$L")"
echo "== stat (kind|role|path|type|inode|nlink|size|mtime|atime|ctime|realpath), no content read"
env -u PYTHONPATH "$PY" -I -B - "$L" "$ENS1" <<'PYEOF'
import os, stat, sys, time
L, ENS1 = sys.argv[1], sys.argv[2]
def st(path):
    try:
        s = os.stat(path)
    except FileNotFoundError:
        return None
    kind = "regular file" if stat.S_ISREG(s.st_mode) else "directory" if stat.S_ISDIR(s.st_mode) else "other"
    return kind, s.st_dev, s.st_ino, s.st_nlink, s.st_size, int(s.st_mtime), int(s.st_atime), int(s.st_ctime)
ens = {}
for line in open(ENS1):
    if line.startswith("#") or not line.strip():
        continue
    f = line.rstrip("\n").split("|")
    ens[f[7]] = {"inode": int(f[1]), "real": os.path.realpath(f[7])}
ens_real = {v["real"]: p for p, v in ens.items()}
ens_ino = {v["inode"]: p for p, v in ens.items()}
missing, oldest, shared, shared_other = 0, time.time(), [], []
for line in open(L):
    kind, role, path = line.rstrip("\n").split("|")
    s = st(path)
    if s is None:
        print(f"{kind}|{role}|{path}|MISSING")
        missing += 1
        continue
    real = os.path.realpath(path)
    print(f"{kind}|{role}|{path}|{s[0]}|{s[2]}|{s[3]}|{s[4]}|{s[5]}|{s[6]}|{s[7]}|{real}")
    oldest = min(oldest, s[6])
    hit = ens_real.get(real) or ens_ino.get(s[2])
    if hit is not None:
        (shared if kind == "inplace" else shared_other).append((role, path, real, hit))
print("== summary")
print(f"missing {missing}")
print(f"oldest atime {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(oldest))}; exposed from (oldest atime + 8 weeks, "
      f"arithmetic) {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(oldest + 56 * 86400))}")
print(f"== ruling 4: ENS1 stage-2 paths {len(ens)} (realpath'd here); in-place sources shared {len(shared)}; "
      f"other sources shared {len(shared_other)}")
for role, path, real, hit in shared + shared_other:
    print(f"SHARED|{role}|{path}|{real}|ENS1 {hit}")
print(f"BRANCH {'SHARED' if shared else 'NONE'}")
sys.exit(4 if missing else 0)
PYEOF
prc=$?
[ "$prc" -eq 0 ] || { echo "STOP: a source is missing (or the stat step failed, rc $prc); to the director"; finish 4; }
finish 0
