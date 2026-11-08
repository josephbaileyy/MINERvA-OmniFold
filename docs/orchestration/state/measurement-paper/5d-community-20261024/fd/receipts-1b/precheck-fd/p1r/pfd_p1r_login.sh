#!/bin/bash
# 1B pre-check Part 1, P1 rerun at M_A1 (addendum A1, #921; the director's ruling on P1's INVALID, #877): reuse the existing stage. On a login node
# at nice 19 and 0 node-h, from a fresh clone at the new M with empty porcelain:
# - the COV2D fence logic must read no cov2d-* job (else STOP);
# - the stage is verified, not re-staged, with O_NOATIME reads (A1, ruling 3) and stage atime recorded before and after
#   the rehash and after the controls. Every copy in $V/stage is re-hashed against the sha256 that P1's staged.json
#   recorded for it, and staged.json itself against P1's recorded digest (f2f06419...). No original is opened.
# - every source (original) is re-stat'd (stat only) before the controls and compared with P1's stat-after.txt, and again
#   after the controls; any difference (an original's atime included) is printed and STOPs (the director's A1 go);
# - the thread environment is I0's (addendum A1, ruling 2): no OMP/OPENBLAS/MKL/NUMEXPR thread export, pure inheritance,
#   recorded as inherited and as used (shell), and inside the controls (os.environ, numpy, threadpoolctl or np.show_config);
# - controls E and M run in the bound readout at the new M, control M with the H2 definition's float64 U. With no
#   products yet, it must stop exactly at fd1b_pfd_A_CV.npz; any fs.Invalid is a control failure.
# $V = /pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107 must exist. The clone is under the literal root
# /dev/shm/limres-pfd-p1r-20261107, removed by its literal path at exit. Launched from a /dev/shm copy ($1).
SELF=$1
M=8d7a40c23b3b6b70c2913ba363a10a22e152aee4
MOD_SHA=a7fbbb5850733b248c89c3f4e9527c40b8531228b88241ab2d3f2063c0863d2d
STAGED_SHA=f2f0641975d810172ad946f650d9b59c52fea57e3b70947c12cb87656bf31189
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
finish() { echo "== pfd-p1r rc=$1 $(date -u +%FT%TZ)"; rm -rf -- /dev/shm/limres-pfd-p1r-20261107; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node"; rm -f -- "$SELF"; exit 9 ;; esac
[ ! -e /dev/shm/limres-pfd-p1r-20261107 ] || { echo "STOP: /dev/shm/limres-pfd-p1r-20261107 exists"; rm -f -- "$SELF"; exit 9; }
[ -d "$V/stage" ] && [ -d "$V/unf" ] && [ -z "$(ls -A "$V/unf")" ] || { echo "STOP: $V/stage or an empty $V/unf missing"; rm -f -- "$SELF"; exit 9; }
mkdir /dev/shm/limres-pfd-p1r-20261107 || { rm -f -- "$SELF"; exit 9; }
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== COV2D fence (must be empty)"
fence=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
hits=$(printf '%s\n' "$fence" | awk -F'|' '$2 ~ /^cov2d-/')
echo "squeue rc=$frc; cov2d-* rows: [$hits]"
[ "$frc" -eq 0 ] && [ -z "$hits" ] || { echo "STOP: the fence is not clear"; finish 3; }
git clone --quiet --filter=blob:none --no-checkout https://github.com/josephbaileyy/MINERvA-OmniFold.git \
  /dev/shm/limres-pfd-p1r-20261107/repo || { echo "STOP: clone failed"; finish 5; }
git -C /dev/shm/limres-pfd-p1r-20261107/repo -c advice.detachedHead=false checkout --quiet "$M" || { echo "STOP: checkout"; finish 5; }
head=$(git -C /dev/shm/limres-pfd-p1r-20261107/repo rev-parse HEAD); porc=$(git -C /dev/shm/limres-pfd-p1r-20261107/repo status --porcelain | wc -l)
echo "HEAD $head; porcelain lines $porc"; [ "$head" = "$M" ] && [ "$porc" -eq 0 ] || { echo "STOP: clone not M clean"; finish 5; }
got=$(sha256sum /dev/shm/limres-pfd-p1r-20261107/repo/nd-unfolding/fd_1b_precheck_fd.py | cut -d' ' -f1)
echo "module sha256 $got (expected $MOD_SHA)"; [ "$got" = "$MOD_SHA" ] || { echo "STOP: module"; finish 5; }
cd /dev/shm/limres-pfd-p1r-20261107/repo/nd-unfolding || finish 5
echo "thread variables as inherited: OMP_NUM_THREADS=${OMP_NUM_THREADS-<unset>} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS-<unset>} MKL_NUM_THREADS=${MKL_NUM_THREADS-<unset>} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS-<unset>}"
export PYTHONDONTWRITEBYTECODE=1
echo "thread variables as used by the controls (A1 ruling 2: inherited as I0 did, none exported): OMP_NUM_THREADS=${OMP_NUM_THREADS-<unset>} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS-<unset>} MKL_NUM_THREADS=${MKL_NUM_THREADS-<unset>} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS-<unset>}"
echo "== the stage, verified against P1's record with O_NOATIME reads (no original opened), $(date -u +%FT%TZ)"
nice -n 19 env -u PYTHONPATH "$PY" -B - "$V" "$STAGED_SHA" /dev/shm/limres-pfd-p1r-20261107 <<'PYEOF' || { echo "STOP: the stage is not P1's record"; finish 4; }
import hashlib, json, os, sys
from pathlib import Path
V, want, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
S = V / "stage"
def snap():
    return {str(p.relative_to(S)): os.stat(p).st_atime_ns for p in sorted(S.rglob("*")) if p.is_file()}
def digest(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOATIME)
    h, data = hashlib.sha256(), []
    try:
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                break
            h.update(b)
            if path.name == "staged.json":
                data.append(b)
    finally:
        os.close(fd)
    return h.hexdigest(), b"".join(data)
def write(name, m):
    (out / name).write_text("".join(f"{k}\t{v}\n" for k, v in sorted(m.items())))
before = snap()
write("stage-atime-before.tsv", before)
got, raw = digest(S / "staged.json")
print(f"staged.json sha256 {got} (P1 recorded {want}), read with O_NOATIME")
if got != want:
    sys.exit(1)
rec = json.loads(raw)
bad, n = [], 0
for e in rec["staged"]:
    n += 1
    if digest(S / e["dest"])[0] != e["sha256"]:
        bad.append(e["dest"])
want_files = sorted([e["dest"] for e in rec["staged"]] + ["staged.json"])
after = snap()
write("stage-atime-after-rehash.tsv", after)
moved = sorted(k for k in before if after.get(k) != before[k])
print(f"staged copies re-hashed with O_NOATIME: {n}; mismatches: {len(bad)} {bad[:5]}; "
      f"files in stage beyond the record: {sorted(set(before) - set(want_files))}; missing: {sorted(set(want_files) - set(before))}")
print(f"stage atime before vs after the rehash: {len(before)} files, {len(moved)} moved {moved[:20]}")
sys.exit(1 if bad or set(before) != set(want_files) or rec["missing"] else 0)
PYEOF
for f in stage-atime-before.tsv stage-atime-after-rehash.tsv; do cp "/dev/shm/limres-pfd-p1r-20261107/$f" "$V/p1r-$f"; echo "$f: $(wc -l < "$V/p1r-$f") lines; sha256 $(sha256sum "$V/p1r-$f" | cut -d' ' -f1)"; done
echo "== the sources, re-stat'd (stat only) and compared with P1's stat-after.txt"
env -u PYTHONPATH "$PY" -B -c 'import json,sys; [print(e["src"]) for e in json.load(open(sys.argv[1]))]' "$V/spec.json" \
  | while read -r f; do stat -c '%n|%s|%Y|%X' "$f" 2>&1; done > /dev/shm/limres-pfd-p1r-20261107/stat-p1r.txt
cp /dev/shm/limres-pfd-p1r-20261107/stat-p1r.txt "$V/stat-p1r.txt"
echo "stat-p1r.txt: $(wc -l < "$V/stat-p1r.txt") lines; sha256 $(sha256sum "$V/stat-p1r.txt" | cut -d' ' -f1)"
if cmp -s "$V/stat-after.txt" "$V/stat-p1r.txt"; then echo "sources: byte-identical to P1's stat-after (name, size, mtime, atime)"; else echo "STOP: an original's stat differs from P1's stat-after (the director: if any original's atime moves, STOP and report):"; diff "$V/stat-after.txt" "$V/stat-p1r.txt" | head -40; finish 4; fi
echo "== controls E and M at the new M, $(date -u +%FT%TZ)"
R=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b
nice -n 19 env -u PYTHONPATH "$PY" -B - "$V" "$R" <<'PYEOF'
import sys
from pathlib import Path
import fd_1b_precheck_fd as pfd
import fd_1b_score as fs
import os, numpy as np
print("thread variables (python):", {k: os.environ.get(k, "<unset>") for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")}, "numpy", np.__version__)
try:
    import threadpoolctl
    print("threadpools:", [(i.get("internal_api"), i.get("num_threads"), i.get("version"), i.get("filepath")) for i in threadpoolctl.threadpool_info()])
except ImportError:
    print("threadpools: threadpoolctl not installed; numpy's build configuration follows")
    np.show_config()
sys.stdout.flush()
V, R = Path(sys.argv[1]), Path("..") / sys.argv[2]
want = V / "unf" / f"{pfd.TAG}_A_CV.npz"
try:
    pfd.readout(V / "stage", V / "unf", R / "stage2/run/score/gate-d.json", R / "diag/diag.json", R / "inv/i0/i0.json",
                Path("pv-ladder/readouts/h2_definition.json"))
    print("CONTROLS: UNEXPECTED: the readout completed with no products"); sys.exit(6)
except fs.Invalid as e:
    print(f"CONTROLS: FAIL (fs.Invalid): {e}"); sys.exit(7)
except FileNotFoundError as e:
    if Path(e.filename) == want:
        print(f"CONTROLS: E and M PASSED; the readout stopped at its first mode product, as expected before P2: {e.filename}")
        sys.exit(0)
    print(f"CONTROLS: STOP at an unexpected missing file: {e}"); sys.exit(8)
PYEOF
c=$?
echo "controls rc=$c $(date -u +%FT%TZ)"
echo "== stage atime after the controls (stat only; the bound readout reads staged copies with its own plain reads)"
env -u PYTHONPATH "$PY" -B - "$V" /dev/shm/limres-pfd-p1r-20261107 <<'PYEOF'
import os, sys
from pathlib import Path
V, out = Path(sys.argv[1]), Path(sys.argv[2])
S = V / "stage"
now = {str(p.relative_to(S)): os.stat(p).st_atime_ns for p in sorted(S.rglob("*")) if p.is_file()}
(out / "stage-atime-after-controls.tsv").write_text("".join(f"{k}\t{v}\n" for k, v in sorted(now.items())))
prev = dict(line.split("\t") for line in (out / "stage-atime-after-rehash.tsv").read_text().splitlines())
moved = sorted(k for k in now if str(now[k]) != prev.get(k))
print(f"stage atime after the rehash vs after the controls: {len(now)} files, {len(moved)} moved")
for k in moved:
    print(f"  moved {k}")
PYEOF
cp /dev/shm/limres-pfd-p1r-20261107/stage-atime-after-controls.tsv "$V/p1r-stage-atime-after-controls.tsv" && echo "stage-atime-after-controls.tsv: $(wc -l < "$V/p1r-stage-atime-after-controls.tsv") lines; sha256 $(sha256sum "$V/p1r-stage-atime-after-controls.tsv" | cut -d' ' -f1)"
echo "== the sources, re-stat'd after the controls (stat only) and compared with the pre-controls re-stat"
env -u PYTHONPATH "$PY" -B -c 'import json,sys; [print(e["src"]) for e in json.load(open(sys.argv[1]))]' "$V/spec.json" \
  | while read -r f; do stat -c '%n|%s|%Y|%X' "$f" 2>&1; done > /dev/shm/limres-pfd-p1r-20261107/stat-p1r-end.txt
cp /dev/shm/limres-pfd-p1r-20261107/stat-p1r-end.txt "$V/stat-p1r-end.txt"
echo "stat-p1r-end.txt: $(wc -l < "$V/stat-p1r-end.txt") lines; sha256 $(sha256sum "$V/stat-p1r-end.txt" | cut -d' ' -f1)"
if cmp -s "$V/stat-p1r.txt" "$V/stat-p1r-end.txt"; then echo "sources: unchanged through the controls"; else echo "STOP: an original's stat moved during this connect:"; diff "$V/stat-p1r.txt" "$V/stat-p1r-end.txt" | head -40; finish 4; fi
finish "$c"
