#!/bin/bash
# COV2D connect S-<T>: addendum A4's phase S (COV2D-ADDENDUM-A4.md section 4), `cov2d_readout.py score --truth T
# --null-digest D`, for one truth, after its null record is merged to main (COV2D-BINDING-2 addendum A4, ruling 1).
# Login node, 0 node-h (A4 section 9), at M = ac25b665. The same template as connect-n.sh (phase N, receipted in
# readout/<T>/): a fresh clone at M in /dev/shm, the MAT pin before and after sourcing, the MnvH1D preflight, nice 19,
# taskset -c 8-11, threads 1, porcelain before and after, the clone removed at the end (logged).
# The gate is the driver's (section 9.7): origin/main's null_<T>.json must hash to D, name this M, this truth and PASS;
# the blocks npz and the re-hashed inventory must match; only then is a toy opened. Before running, this script records
# origin/main's sha and the sha256 of `git show origin/main:<null record>` (the driver still does its own check).
# Verdict: COVERS or UNDER-COVERS (rc 0, "COV2D-SCORE <T> COVERS|UNDER-COVERS"); REFUSED (rc 2, the gate);
# STOP or INVALID from the driver (rc 3, "COV2D-SCORE <T> STOP|INVALID"); else INVALID (connect). A section 9.9 INVALID
# goes to the director unrepaired, with the mechanism named (binding A4, ruling 2).
# connect-s-<T>.sh is this file with T and D set; nothing else differs.
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-s-<T>.sh >/dev/null 2>&1 </dev/null &
M=ac25b66533788ceb18b1d4e5add259c53b216669
T=G18
D=ecdb4be2fbb18852d32c1a4f9fb3cbc4107310d72c5bdeb2eb3651996ed0c41f
READOUT_SHA=d1a3cff9768cb3913c9b95c9c6c1bb7402c5a14103f1dd22f5131c16aacda297
W=/dev/shm/josephrb-cov2d-s-$T; DD=$W/deploy
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold   # the shared checkout with the MAT build (setup_salloc_env.sh)
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
RUN="nice -n 19 taskset -c 8-11"
cleanup() { echo "removal: host=$(hostname) $(date -u +%FT%TZ) $(du -sh "$DD" 2>/dev/null | cut -f1) $DD"; rm -rf "$DD" "$W/tmp"; echo "rc=$?"; ls -d "$DD" "$W/tmp" 2>&1; }
stop() { echo "STOP $*"; cleanup; echo "PHASE-S INVALID (connect)"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit 2; }
case "$T" in G18|AR23) ;; *) echo "STOP T is not set"; exit 2 ;; esac
case "$D" in *[!0-9a-f]*|"") echo "STOP D is not set"; exit 2 ;; esac
[ ${#D} = 64 ] || { echo "STOP D is not a sha256"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" "$W/tmp" "$W/out" || exit 2
exec >> "$W/connect-s-$T.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" -c advice.detachedHead=false checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "porcelain_before_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
got=$(sha256sum "$DD/2d-unfolding/cov2d/cov2d_readout.py" | cut -c1-64)
[ "$got" = "$READOUT_SHA" ] && echo "READOUT-SHA OK $got" || stop "cov2d_readout.py is $got"
(cd "$DD" && git ls-tree -r HEAD 2d-unfolding/cov2d | grep -v __pycache__) > "$W/blobs.before"
NR=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/readout/$T/null_$T.json
echo "origin/main=$(git -C "$DD" rev-parse origin/main)"
g=$(git -C "$DD" show "origin/main:$NR" | sha256sum | cut -c1-64)
[ "$g" = "$D" ] && echo "NULL-ON-MAIN OK $g" || stop "origin/main null_$T.json is $g, not $D"
(
  "$PY310" -B -c "import sys; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; r.run_check_mat_setup(None)" || exit 7
  source "$A/setup_salloc_env.sh" > /dev/null 2>&1 || exit 3
  export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  echo "python=$(command -v python) TMPDIR=$TMPDIR"
  python -c "import sys, numpy, ROOT; print(sys.version.split()[0], 'numpy', numpy.__version__, 'ROOT', ROOT.gROOT.GetVersion())" || exit 4
  python - <<'PYEOF' || exit 5
import hashlib, os, ROOT
src = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_1A.root"
fd = os.open(src, os.O_RDONLY | os.O_NOATIME); data = b""
while True:
  b = os.read(fd, 1 << 24)
  if not b: break
  data += b
os.close(fd)
print("MAT preflight file:", src, "sha256", hashlib.sha256(data).hexdigest())
dst = os.path.join(os.environ["TMPDIR"], "mat_preflight.root"); open(dst, "wb").write(data)
f = ROOT.TFile.Open(dst); h = f.Get("pTmu_reweightedflux_integrated")
print("MAT preflight:", type(h).__name__, h.ClassName(), h.GetNbinsX(), "bins")
assert h.ClassName().startswith("PlotUtils::MnvH1D"), h.ClassName()
os.remove(dst)
PYEOF
  cd "$DD/2d-unfolding/cov2d" && $RUN /usr/bin/time -v python -B cov2d_readout.py score --truth "$T" --null-digest "$D" --out "$W/out"
) > "$W/score_$T.log" 2>&1; rc=$?
grep -v '^Warning in <TInterpreter::ReadRootmapFile>' "$W/score_$T.log" | tail -40
L=$(grep "^COV2D-SCORE $T " "$W/score_$T.log" | tail -1)
case "$rc:$L" in
  "0:COV2D-SCORE $T COVERS"|"0:COV2D-SCORE $T UNDER-COVERS") V=${L#COV2D-SCORE $T } ;;
  "2:COV2D-SCORE $T REFUSED "*) V=REFUSED ;;
  "3:COV2D-SCORE $T STOP"|"3:COV2D-SCORE $T INVALID") V=${L#COV2D-SCORE $T } ;;
  *) V="INVALID (connect: rc=$rc, no matching verdict line)" ;;
esac
echo "PHASE-S $T $V rc=$rc"
(cd "$W/out" && sha256sum * 2>&1)
n=$(git -C "$DD" status --porcelain | wc -l); echo "porcelain_after_lines=$n head=$(git -C "$DD" rev-parse HEAD)"
git -C "$DD" status --porcelain | head -20
(cd "$DD" && git ls-tree -r HEAD 2d-unfolding/cov2d | grep -v __pycache__) > "$W/blobs.after"
cmp -s "$W/blobs.before" "$W/blobs.after" && echo "blobs unchanged" || echo "blobs CHANGED"
cleanup
echo "end=$(date -u +%FT%TZ)"
echo DONE
