#!/bin/bash
# COV2D connect N-<T>: addendum A4's phase N (COV2D-ADDENDUM-A4.md section 3), `cov2d_readout.py null --truth T`, for
# one truth (one connect per truth; noatime_inputs repoints the rollup's globals: one truth per process). Login node,
# 0 node-h (A4 section 9), at M = ac25b665 (COV2D-BINDING-2 addendum A4). Template: connect-95-run3.sh (control95, receipted in #869): a fresh
# clone in /dev/shm (cov2d_blocks' open audit guards /pscratch), the MAT pin before and after sourcing
# setup_salloc_env.sh, a MAT preflight on one real MnvH1D, nice 19, taskset -c 8-11, threads 1, porcelain before and
# after, the clone removed at the end (logged).
# Reads are the driver's own (A4 section 3.1): each through O_NOATIME, digest-checked, under the open audit. No toy is
# opened (stat only; the driver checks its own audit log). The outputs (null_<T>.json, blocks_<T>.npz) stay in
# $W/out for the fetch; they are committed to main before phase S may run (A4 section 4).
# Verdict: PASS (rc 0, "COV2D-NULL <T> PASS"), STOP (rc 3, "COV2D-NULL <T> STOP"), else INVALID. An INVALID (or a
# section 9.9 / runArgv mismatch) goes to the director unrepaired, with the mechanism named (binding A4, ruling 2).
# connect-n-G18.sh and connect-n-AR23.sh are this file with T set; nothing else differs.
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-n-<T>.sh >/dev/null 2>&1 </dev/null &
M=ac25b66533788ceb18b1d4e5add259c53b216669
T=G18
READOUT_SHA=d1a3cff9768cb3913c9b95c9c6c1bb7402c5a14103f1dd22f5131c16aacda297
W=/dev/shm/josephrb-cov2d-n-$T; DD=$W/deploy
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold   # the shared checkout with the MAT build (setup_salloc_env.sh)
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
RUN="nice -n 19 taskset -c 8-11"
cleanup() { echo "removal: host=$(hostname) $(date -u +%FT%TZ) $(du -sh "$DD" 2>/dev/null | cut -f1) $DD"; rm -rf "$DD" "$W/tmp"; echo "rc=$?"; ls -d "$DD" "$W/tmp" 2>&1; }
stop() { echo "STOP $*"; cleanup; echo "PHASE-N INVALID (connect)"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit 2; }
case "$T" in G18|AR23) ;; *) echo "STOP T is not set"; exit 2 ;; esac
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" "$W/tmp" "$W/out" || exit 2
exec >> "$W/connect-n-$T.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" -c advice.detachedHead=false checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "porcelain_before_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
got=$(sha256sum "$DD/2d-unfolding/cov2d/cov2d_readout.py" | cut -c1-64)
[ "$got" = "$READOUT_SHA" ] && echo "READOUT-SHA OK $got" || stop "cov2d_readout.py is $got"
(cd "$DD" && git ls-tree -r HEAD 2d-unfolding/cov2d | grep -v __pycache__) > "$W/blobs.before"
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
  cd "$DD/2d-unfolding/cov2d" && $RUN /usr/bin/time -v python -B cov2d_readout.py null --truth "$T" --out "$W/out"
) > "$W/null_$T.log" 2>&1; rc=$?
grep -v '^Warning in <TInterpreter::ReadRootmapFile>' "$W/null_$T.log" | tail -40
if [ "$rc" = 0 ] && grep -q "^COV2D-NULL $T PASS" "$W/null_$T.log"; then V=PASS
elif [ "$rc" = 3 ] && grep -q "^COV2D-NULL $T STOP" "$W/null_$T.log"; then V=STOP
else V=INVALID; fi
echo "PHASE-N $T $V rc=$rc"
(cd "$W/out" && sha256sum * 2>&1)
n=$(git -C "$DD" status --porcelain | wc -l); echo "porcelain_after_lines=$n head=$(git -C "$DD" rev-parse HEAD)"
git -C "$DD" status --porcelain | head -20
(cd "$DD" && git ls-tree -r HEAD 2d-unfolding/cov2d | grep -v __pycache__) > "$W/blobs.after"
cmp -s "$W/blobs.before" "$W/blobs.after" && echo "blobs unchanged" || echo "blobs CHANGED"
cleanup
echo "end=$(date -u +%FT%TZ)"
echo DONE
