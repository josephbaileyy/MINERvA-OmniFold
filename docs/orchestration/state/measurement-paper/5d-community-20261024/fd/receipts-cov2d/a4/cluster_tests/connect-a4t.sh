#!/bin/bash
# COV2D connect A4-TESTS: addendum A4's tests in the cluster environments, at the A4 code head (PR #875), 0 node-h.
# Derived from the approved A2 connect ../a2/cluster_tests/connect-a2tests-2.sh (its suite runner, audit hook, porcelain
# and removal), without its rerun deploy and quota check. A fresh clone at the code head in /dev/shm on a login node
# (not pscratch: cov2d_blocks' open audit guards /pscratch); each suite in its own process:
#   RM = root_6_28 + the pinned MAT environment, the environment the driver runs in (A4 section 3): test_cov2d_readout
#        and the bound suites of the modules it imports and runs (blocks, null, score); test_cov2d (deploy_head)
#   R  = root_6_28 by full prefix, no MAT: test_cov2d_readout, blocks, null, score (as A2's R)
#   P  = omnifold_py310 (no ROOT): test_cov2d_readouts, its declared environment
# On Linux os.O_NOATIME is real, so the tests leave Run.watch live: the end-to-end phase N and S tests then also pass the
# real atime guard (the Mac run stubbed watch). No data are read. The only pscratch reads are RM's own setup: the
# pinned MAT setup scripts and libraries under $A, as in every earlier COV2D connect. The runner's audit hook reports
# any /pscratch or /global/cfs path the suites themselves open. The bound modules are checked unchanged from M.
# login02, nice 19, taskset -c 8-11, threads 1. /dev/shm is cleared at the end except the logs, which are fetched and
# then removed (logged).
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-a4t.sh >/dev/null 2>&1 </dev/null &
H4=7177d0f83120a70373057adc6a64a2c84985e867
M=a60547692df5f963e428cdfe4661fc51ab785b7b
READOUT_SHA=d1a3cff9768cb3913c9b95c9c6c1bb7402c5a14103f1dd22f5131c16aacda297
W=/dev/shm/josephrb-cov2d-a4t; DD=$W/deploy; L=$W/logs
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
R628=/global/homes/j/josephrb/.conda/envs/root_6_28
CONDA2410=/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda
RUN="nice -n 19 taskset -c 8-11"
finish() { echo "removal: host=$(hostname) $(date -u +%FT%TZ) $(du -sh "$DD" 2>/dev/null | cut -f1)"; rm -rf "$DD" "$W/tmp" "$W/runsuite.py"; echo "rc=$?"; ls -d "$DD" "$W/tmp" "$W/runsuite.py" 2>&1; echo "end=$(date -u +%FT%TZ)"; echo DONE; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" "$W/tmp" "$L" || exit 2
exec >> "$W/connect-a4t.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" -c advice.detachedHead=false checkout --quiet --detach "$H4" \
    || { echo "STOP clone"; finish; exit 2; }
[ "$(git -C "$DD" rev-parse HEAD)" = "$H4" ] || { echo "STOP head"; finish; exit 2; }
porc() { echo "porcelain-$1 plain=$(git -C "$DD" status --porcelain | wc -l) ignored=$(git -C "$DD" status --porcelain --ignored | wc -l)"; git -C "$DD" status --porcelain --ignored | head -20; }
echo "head=$(git -C "$DD" rev-parse HEAD)"; porc before
got=$(sha256sum "$DD/2d-unfolding/cov2d/cov2d_readout.py" | cut -c1-64)
[ "$got" = "$READOUT_SHA" ] && echo "READOUT-SHA OK $got" || { echo "STOP cov2d_readout.py is $got"; finish; exit 2; }
for f in cov2d.py cov2d_blocks.py cov2d_null.py cov2d_score.py cov2d_readouts.py; do
    git -C "$DD" diff --quiet "$M" "$H4" -- "2d-unfolding/cov2d/$f" && echo "BOUND-UNCHANGED $f" || echo "BOUND-CHANGED $f"
done
(cd "$DD" && git ls-tree -r HEAD 2d-unfolding/cov2d | grep -v __pycache__) > "$L/blobs.txt"
cat > "$W/runsuite.py" <<'PY'
"""Run one test module, verbosely; report its counts and any /pscratch or /global/cfs path the suite itself opened."""
import os, sys, unittest
env, mod = sys.argv[1], sys.argv[2]
hits = []
def hook(event, args):
    if event in ("open", "os.listdir", "os.scandir", "glob.glob", "shutil.copyfile") and args:
        p = args[0]
        if isinstance(p, (str, bytes, os.PathLike)):
            p = os.fsdecode(p)
            if p.startswith(("/pscratch", "/global/cfs")):
                hits.append(f"{event} {p}")
sys.addaudithook(hook)
sys.path.insert(0, os.getcwd())
r = unittest.main(module=None, argv=["runsuite", "-v", mod], exit=False).result
print(f"SUITE env={env} module={mod} ran={r.testsRun} failures={len(r.failures)} errors={len(r.errors)} "
      f"skipped={len(r.skipped)} guarded_reads={len(hits)} ok={r.wasSuccessful()}", flush=True)
for h in sorted(set(hits)):
    print(f"GUARDED {h}")
for t, why in r.skipped:
    print(f"SKIP {t.id()}: {why}")
sys.exit(0 if r.wasSuccessful() else 1)
PY
T=$DD/2d-unfolding/cov2d/tests
envinfo() { "$PYX" -B -c "
import os, sys, numpy
def v(m):
    try:
        mod = __import__(m)
        return getattr(mod, '__version__', None) or (mod.gROOT.GetVersion() if m == 'ROOT' else '?')
    except Exception as e:
        return 'absent (' + type(e).__name__ + ')'
print('ENV $1', sys.executable, sys.version.split()[0], 'numpy', numpy.__version__, 'uproot', v('uproot'), 'ROOT', v('ROOT'), 'O_NOATIME', getattr(os, 'O_NOATIME', None))
"; }
suite() { local e=$1 m=$2; (cd "$T" && $RUN "$PYX" -B "$W/runsuite.py" "$e" "$m" > "$L/${e}_$m.log" 2>&1); echo "rc env=$e module=$m rc=$?"; grep "^SUITE \|^GUARDED " "$L/${e}_$m.log"; }
# RM: root_6_28 + the pinned MAT environment
(
  "$PY310" -B -c "import sys; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; r.run_check_mat_setup(None)" || exit 7
  source "$A/setup_salloc_env.sh" > /dev/null 2>&1 || exit 3
  export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  PYX=$(command -v python); echo "RM python=$PYX"
  "$PYX" -B -c "import sys, json; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; m = r.mat_environment(); print('MAT ' + json.dumps({'mapped': m['mapped_mat_files'], 'dictionary': m['plotutils_mnvh1d_dictionary']}))" || exit 8
  envinfo RM
  for m in test_cov2d_readout test_cov2d_blocks test_cov2d_null test_cov2d_score test_cov2d; do suite RM $m; done
); echo "RM rc=$?"
# R: root_6_28 by prefix, no MAT
(
  eval "$("$CONDA2410" shell.bash hook 2>/dev/null)" && conda activate "$R628" || exit 3
  export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  PYX=$(command -v python); [ "$PYX" = "$R628/bin/python" ] || { echo "R python is $PYX"; exit 3; }
  envinfo R
  for m in test_cov2d_readout test_cov2d_blocks test_cov2d_null test_cov2d_score; do suite R $m; done
); echo "R rc=$?"
# P: omnifold_py310
(
  PYX=$PY310
  envinfo P
  suite P test_cov2d_readouts
); echo "P rc=$?"
porc after
# the guard tests ran on Linux with the real O_NOATIME and a live Run.watch, not skipped
for e in RM R; do
  for t in test_null_passes_at_both_truths_and_opens_no_toy test_score_completes_after_the_gate test_a_plain_toy_open_in_phase_n_is_refused_by_the_audit test_a_noatime_toy_read_in_phase_n_stops test_atime_moved_stops_and_unmoved_does_not; do
    grep -q "^$t .* ok$" "$L/${e}_test_cov2d_readout.log" && echo "GUARD-TEST RAN-OK $e $t" || echo "GUARD-TEST NOT-OK $e $t"
  done
done
(cd "$L" && sha256sum *.log blobs.txt) > "$L/SHA256SUMS"
echo "TESTS-SUMMARY $(grep -c '^SUITE .* ok=True' "$W/connect-a4t.log") ok of $(grep -c '^SUITE ' "$W/connect-a4t.log") suite runs"
finish
