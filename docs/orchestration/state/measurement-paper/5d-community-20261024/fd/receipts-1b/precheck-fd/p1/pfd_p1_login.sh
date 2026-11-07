#!/bin/bash
# 1B pre-check Part 1, P1: staging and controls E and M (FD-1B-PRECHECK-FD-BINDING-1.md ruling 3; declaration
# sections 5-7), on a login node at nice 19 and 0 node-h, from a fresh clone at M = ed8f328f with empty porcelain.
# - The COV2D fence logic must read no cov2d-* job (else STOP, nothing staged), because the stage holds two COV2D
#   inputs: the flux constraint and the flux-universe file.
# - Staging is the bound `fd_1b_precheck_fd.py stage` (fd_1b_inv.stage): each source read once with O_NOATIME into
#   $V/stage, with the declared digests for the assembly, the constraint and the flux file, refusing any source whose
#   atime moves.
# - Controls E and M run inside the bound `readout`, which checks gate D's committed ratios and the diagnosis's
#   per-band ratios bit for bit (E), and S1's staged unfolds against the assembly (M), before it opens its first
#   mode product. With no products yet (P2 has not run), it must stop exactly at fd1b_pfd_A_CV.npz; any fs.Invalid is
#   a control failure.
# - Every source is stat'd before and after (size, mtime, atime), and the two lists must be byte-identical.
# $V = /pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107 (refused if it exists). The clone is under the literal root
# /dev/shm/limres-pfd-p1-20261107, removed by its literal path at exit. Launched from a /dev/shm copy ($1).
SELF=$1
M=ed8f328fab52122112f54850d0078d79e81834c5
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
P=/pscratch/sd/j/josephrb
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
finish() { echo "== pfd-p1 rc=$1 $(date -u +%FT%TZ)"; rm -rf -- /dev/shm/limres-pfd-p1-20261107; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node"; rm -f -- "$SELF"; exit 9 ;; esac
[ ! -e /dev/shm/limres-pfd-p1-20261107 ] || { echo "STOP: /dev/shm/limres-pfd-p1-20261107 exists"; rm -f -- "$SELF"; exit 9; }
[ ! -e "$V" ] || { echo "STOP: $V exists"; rm -f -- "$SELF"; exit 9; }
mkdir /dev/shm/limres-pfd-p1-20261107 || { rm -f -- "$SELF"; exit 9; }
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== COV2D fence, immediately before staging (must be empty)"
fence=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
hits=$(printf '%s\n' "$fence" | awk -F'|' '$2 ~ /^cov2d-/')
echo "squeue rc=$frc; cov2d-* rows: [$hits]"
[ "$frc" -eq 0 ] && [ -z "$hits" ] || { echo "STOP: the fence is not clear; nothing staged"; finish 3; }
git clone --quiet --filter=blob:none --no-checkout https://github.com/josephbaileyy/MINERvA-OmniFold.git \
  /dev/shm/limres-pfd-p1-20261107/repo || { echo "STOP: clone failed"; finish 5; }
git -C /dev/shm/limres-pfd-p1-20261107/repo -c advice.detachedHead=false checkout --quiet "$M" || { echo "STOP: checkout"; finish 5; }
head=$(git -C /dev/shm/limres-pfd-p1-20261107/repo rev-parse HEAD); porc=$(git -C /dev/shm/limres-pfd-p1-20261107/repo status --porcelain | wc -l)
echo "HEAD $head; porcelain lines $porc"; [ "$head" = "$M" ] && [ "$porc" -eq 0 ] || { echo "STOP: clone not M clean"; finish 5; }
echo "module sha256 $(sha256sum /dev/shm/limres-pfd-p1-20261107/repo/nd-unfolding/fd_1b_precheck_fd.py | cut -d' ' -f1) (bound 7c3ffe86...)"
[ "$(sha256sum /dev/shm/limres-pfd-p1-20261107/repo/nd-unfolding/fd_1b_precheck_fd.py | cut -d' ' -f1)" = 7c3ffe86b721f79ba9ee3d426b4c711ca96eeec7b2a4071eba5cf62bf102ef0f ] || { echo "STOP: module"; finish 5; }
cd /dev/shm/limres-pfd-p1-20261107/repo/nd-unfolding || finish 5
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
env -u PYTHONPATH "$PY" -B - "$P" > /dev/shm/limres-pfd-p1-20261107/spec.json <<'PYEOF' || { echo "STOP: spec"; finish 5; }
import json, sys
import fd_1b_toys as t
P = sys.argv[1]
us = ["CV"] + t.s1_universes()
spec = [{"role": "derivation", "src": f"{P}/fd-1b-20261030/runs/derivation/fd1b_derivation_{u}.npz",
         "dest": f"derivation/fd1b_derivation_{u}.npz"} for u in us]
spec += [{"role": "s1-universe", "src": f"{P}/s1-20261024/runs/uni/S1_{u}.npz", "dest": f"uni/S1_{u}.npz"} for u in us]
spec += [{"role": "s1-assembly", "src": f"{P}/s1-20261024/s1_assembly.npz", "dest": "s1/s1_assembly.npz",
          "sha256": "db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4"},
         {"role": "flux-constraint", "src": f"{P}/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt",
          "dest": "flux_constraint.txt", "sha256": "e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2"},
         {"role": "flux-file", "src": f"{P}/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root",
          "dest": "flux_universes.root", "sha256": "5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb"}]
print(json.dumps(spec, indent=1))
PYEOF
echo "spec entries $(grep -c '"role"' /dev/shm/limres-pfd-p1-20261107/spec.json); sha256 $(sha256sum /dev/shm/limres-pfd-p1-20261107/spec.json | cut -d' ' -f1)"
srcs() { env -u PYTHONPATH "$PY" -B -c 'import json,sys; [print(e["src"]) for e in json.load(open(sys.argv[1]))]' /dev/shm/limres-pfd-p1-20261107/spec.json; }
srcs | while read -r f; do stat -c '%n|%s|%Y|%X' "$f" 2>&1; done > /dev/shm/limres-pfd-p1-20261107/stat-before.txt
echo "stat before: $(wc -l < /dev/shm/limres-pfd-p1-20261107/stat-before.txt) lines; missing $(grep -c 'No such file' /dev/shm/limres-pfd-p1-20261107/stat-before.txt)"
mkdir -p "$V" || finish 9
echo "== stage (bound code), $(date -u +%FT%TZ)"
nice -n 19 env -u PYTHONPATH "$PY" -B fd_1b_precheck_fd.py stage --spec /dev/shm/limres-pfd-p1-20261107/spec.json --out "$V/stage"
src=$?
echo "stage rc=$src $(date -u +%FT%TZ)"
srcs | while read -r f; do stat -c '%n|%s|%Y|%X' "$f" 2>&1; done > /dev/shm/limres-pfd-p1-20261107/stat-after.txt
if cmp -s /dev/shm/limres-pfd-p1-20261107/stat-before.txt /dev/shm/limres-pfd-p1-20261107/stat-after.txt; then
  echo "stat after: byte-identical to before ($(wc -l < /dev/shm/limres-pfd-p1-20261107/stat-after.txt) sources)"
else echo "DEVIATION: stat after differs:"; diff /dev/shm/limres-pfd-p1-20261107/stat-before.txt /dev/shm/limres-pfd-p1-20261107/stat-after.txt | head -20; fi
cp /dev/shm/limres-pfd-p1-20261107/stat-before.txt "$V/stat-before.txt"; cp /dev/shm/limres-pfd-p1-20261107/stat-after.txt "$V/stat-after.txt"
cp /dev/shm/limres-pfd-p1-20261107/spec.json "$V/spec.json"
[ "$src" -eq 0 ] || { echo "STOP: staging"; finish 4; }
echo "staged.json sha256 $(sha256sum "$V/stage/staged.json" | cut -d' ' -f1)"
env -u PYTHONPATH "$PY" -B -c 'import json,sys; r=json.load(open(sys.argv[1])); from collections import Counter; print("staged by role", dict(Counter(e["role"] for e in r["staged"])), "missing", r["missing"])' "$V/stage/staged.json"
echo "== controls E and M (the bound readout, stopping at the first mode product), $(date -u +%FT%TZ)"
mkdir -p "$V/unf"
R=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b
nice -n 19 env -u PYTHONPATH "$PY" -B - "$V" "$R" <<'PYEOF'
import sys
from pathlib import Path
import fd_1b_precheck_fd as pfd
import fd_1b_score as fs
V, R = Path(sys.argv[1]), Path("..") / sys.argv[2]
want = V / "unf" / f"{pfd.TAG}_A_CV.npz"
try:
    pfd.readout(V / "stage", V / "unf", R / "stage2/run/score/gate-d.json", R / "diag/diag.json", R / "inv/i0/i0.json")
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
finish "$c"
