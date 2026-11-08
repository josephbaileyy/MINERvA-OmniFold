#!/bin/bash
# Band diagnosis, P1 (FD-1B-BAND-DIAGNOSIS-BINDING-1.md rulings 2, 4 and 5; declaration sections 4.2, 5 and 7): section
# 4.2's HK reading and the readout-reproduction control, from Part 1's products, on a login node at nice 19, 0 node-h,
# no Slurm job, from a fresh clone at M = 83ac32fb with empty porcelain. In order:
#   1. the fence (ruling 4, BRANCH SHARED, P0 #944): every josephrb job must be named fd1b_bdg_*; ens1_*, rs1_*,
#      cov2d-* or any other name refuses, so this window overlaps no ens1_* job;
#   2. the clone: HEAD and porcelain; fd_1b_band_diag.py (658ca918) and Part 1's readout.json (8e05ca9b) gated on sha256;
#   3. thread variables as Part 1's P4 (A1 ruling 2): nothing exported; recorded as inherited and in Python;
#   4. the new root $W = /pscratch/sd/j/josephrb/fd-1b-band-diag-20261109, refused if it exists, created owner-only;
#   5. section 5's before-stat: the 73 sources P0 listed (11 staged, 27 Part 1 products, 34 in place under ruling 4,
#      pins.json), from the bound code, stat only (type|inode|nlink|size|mtime|atime|ctime|path), written to
#      $W/stat-before.txt. This is the stat that P3's after-stat is compared with, byte for byte; it is taken after ENS1's
#      stage-2 analysis ended (the director's note of 2026-11-08);
#   6. `fd_1b_band_diag.py same` on $V/stage, $V/unf and the clone's readout.json, writing $W/same.json (the module
#      refuses to overwrite). It reads only through O_NOATIME, hashes every file at first read, and checks the staged
#      copies against staged.json and S1's digest. A refusal (rc 4: Invalid, Refusal) is reported unrepaired;
#   7. the 73 sources re-stat'd into $W/stat-after-p1.txt and compared with stat-before.txt byte for byte: any
#      difference is printed and is a STOP (rc 4);
#   8. same.json, the stats and their sha256 printed to stdout.
# $V = /pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107 (Part 1's root) must exist. Nothing is written under $V. The
# clone is under the literal root /dev/shm/limres-bdg-p1-20261109, removed by its literal path at exit. Launched from a
# /dev/shm copy of itself ($1), which it deletes.
SELF=$1
M=83ac32fb5024026ac6c51c0621d5ae9ff9073370
MOD_SHA=658ca91849a8151a4fb801e41004102f0ba621c367f1c23146a8fc3a580484df
RO_SHA=8e05ca9bc2d0f2142b5c8d2bff28f05176c48f27454218390f09658344cea7b0
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
W=/pscratch/sd/j/josephrb/fd-1b-band-diag-20261109
RO=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/precheck-fd/p4/records/p4/readout.json
finish() { echo "== bdg-p1 rc=$1 $(date -u +%FT%TZ)"; rm -rf -- /dev/shm/limres-bdg-p1-20261109; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node"; rm -f -- "$SELF"; exit 9 ;; esac
[ ! -e /dev/shm/limres-bdg-p1-20261109 ] || { echo "STOP: /dev/shm/limres-bdg-p1-20261109 exists"; rm -f -- "$SELF"; exit 9; }
[ -d "$V/stage" ] && [ -d "$V/unf" ] || { echo "STOP: $V/stage or $V/unf missing"; rm -f -- "$SELF"; exit 9; }
[ ! -e /pscratch/sd/j/josephrb/fd-1b-band-diag-20261109 ] || { echo "STOP: $W exists"; rm -f -- "$SELF"; exit 9; }
mkdir /dev/shm/limres-bdg-p1-20261109 || { rm -f -- "$SELF"; exit 9; }
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== 1. fence (ruling 4, BRANCH SHARED: only fd1b_bdg_* allowed; anything else refuses)"
fence=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
echo "squeue rc=$frc; rows:"
printf '%s\n' "$fence"
echo "-- end rows"
bad=$(printf '%s\n' "$fence" | awk -F'|' 'NF && $2 !~ /^fd1b_bdg_/')
echo "refusing rows: [$bad]"
[ "$frc" -eq 0 ] && [ -z "$bad" ] || { echo "STOP: the fence is not clear"; finish 3; }
echo "FENCE: clear"
echo "== 2. fresh clone at $M"
git clone --quiet --filter=blob:none --no-checkout https://github.com/josephbaileyy/MINERvA-OmniFold.git \
  /dev/shm/limres-bdg-p1-20261109/repo || { echo "STOP: clone failed"; finish 5; }
git -C /dev/shm/limres-bdg-p1-20261109/repo -c advice.detachedHead=false checkout --quiet "$M" || { echo "STOP: checkout"; finish 5; }
head=$(git -C /dev/shm/limres-bdg-p1-20261109/repo rev-parse HEAD); porc=$(git -C /dev/shm/limres-bdg-p1-20261109/repo status --porcelain | wc -l)
echo "HEAD $head; porcelain lines $porc"; [ "$head" = "$M" ] && [ "$porc" -eq 0 ] || { echo "STOP: clone not M clean"; finish 5; }
got=$(sha256sum /dev/shm/limres-bdg-p1-20261109/repo/nd-unfolding/fd_1b_band_diag.py | cut -d' ' -f1)
echo "module sha256 $got (expected $MOD_SHA)"; [ "$got" = "$MOD_SHA" ] || { echo "STOP: module"; finish 5; }
got=$(sha256sum "/dev/shm/limres-bdg-p1-20261109/repo/$RO" | cut -d' ' -f1)
echo "Part 1 readout.json sha256 $got (expected $RO_SHA)"; [ "$got" = "$RO_SHA" ] || { echo "STOP: readout.json"; finish 5; }
cd /dev/shm/limres-bdg-p1-20261109/repo/nd-unfolding || finish 5
export PYTHONDONTWRITEBYTECODE=1
echo "== 3. thread variables as inherited (as Part 1's P4; none exported): OMP_NUM_THREADS=${OMP_NUM_THREADS-<unset>} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS-<unset>} MKL_NUM_THREADS=${MKL_NUM_THREADS-<unset>} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS-<unset>}"
echo "== 4. the new root"
mkdir -m 700 /pscratch/sd/j/josephrb/fd-1b-band-diag-20261109 || { echo "STOP: cannot create $W"; finish 5; }
echo "created $W"
echo "== 5. section 5's before-stat of the 73 sources, $(date -u +%FT%TZ)"
env -u PYTHONPATH "$PY" -B - > /dev/shm/limres-bdg-p1-20261109/paths.txt <<'PYEOF' || { echo "STOP: source list"; finish 5; }
from pathlib import Path
import fd_1b_band_diag as d, fd_1b_precheck_fd as pfd, s5p_universe as s5p
P = "/pscratch/sd/j/josephrb"
V = Path(f"{P}/fd-1b-precheck-fd-20261107")
us = d.detector_universes()
assert len(us) == 8, us
rows = [V / "stage" / "staged.json"]
rows += [V / "stage" / "derivation" / f"fd1b_derivation_{u}.npz" for u in ["CV"] + us]
rows += [V / "stage" / "s1" / "s1_assembly.npz"]
rows += [V / "unf" / f"{pfd.TAG}_{m}_{u}.npz" for m in pfd.MODES for u in ["CV"] + us]
rows += [Path(f"{P}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"), Path(f"{P}/s5c-20260924/runs/p2/bkg_dump.npz"),
         Path(f"{P}/fd-1b-20261030/pins.json")]
det = Path(f"{P}/s5p-20260926/bank_detector")
for u in us:
    keys = s5p.weight_keys(det, u)
    assert keys == ("wt", "wr", "denom_nd", "bkgw"), (u, keys)
    rows += [det / f"{u}_{k}.npy" for k in keys]
assert len(rows) == 73, len(rows)
print("\n".join(map(str, rows)))
PYEOF
stat_all() { while read -r f; do stat -c '%F|%i|%h|%s|%Y|%X|%Z|%n' "$f" 2>&1; done < /dev/shm/limres-bdg-p1-20261109/paths.txt; }
stat_all > /pscratch/sd/j/josephrb/fd-1b-band-diag-20261109/stat-before.txt
echo "stat-before.txt: $(wc -l < "$W/stat-before.txt") lines; missing $(grep -c 'No such file' "$W/stat-before.txt"); sha256 $(sha256sum "$W/stat-before.txt" | cut -d' ' -f1)"
grep -q 'No such file' "$W/stat-before.txt" && { echo "STOP: a source is missing"; finish 4; }
echo "== 6. same, $(date -u +%FT%TZ)"
nice -n 19 env -u PYTHONPATH "$PY" -B -c 'import os, numpy as np; print("thread variables (python):", {k: os.environ.get(k, "<unset>") for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")}, "numpy", np.__version__)'
nice -n 19 env -u PYTHONPATH "$PY" -B fd_1b_band_diag.py same --staged "$V/stage" --unfolds "$V/unf" \
  --readout "/dev/shm/limres-bdg-p1-20261109/repo/$RO" --out "$W/same.json"
s=$?
echo "same rc=$s $(date -u +%FT%TZ)"
echo "== 7. the 73 sources re-stat'd after same, against the before-stat"
stat_all > /pscratch/sd/j/josephrb/fd-1b-band-diag-20261109/stat-after-p1.txt
echo "stat-after-p1.txt: $(wc -l < "$W/stat-after-p1.txt") lines; sha256 $(sha256sum "$W/stat-after-p1.txt" | cut -d' ' -f1)"
moved=0
if cmp -s "$W/stat-before.txt" "$W/stat-after-p1.txt"; then echo "sources: byte-identical before and after same"; else echo "STOP: a source's stat moved during P1:"; diff "$W/stat-before.txt" "$W/stat-after-p1.txt" | head -40; moved=1; fi
echo "== 8. records"
for f in stat-before.txt stat-after-p1.txt same.json; do [ -f "$W/$f" ] && echo "sha256 $(sha256sum "$W/$f" | cut -d' ' -f1) $f"; done
echo "== stat-before.txt"; cat "$W/stat-before.txt"
echo "== same.json"; [ -f "$W/same.json" ] && cat "$W/same.json" || echo "(not written)"
echo "== end of records"
[ "$moved" -eq 0 ] || finish 4
finish "$s"
