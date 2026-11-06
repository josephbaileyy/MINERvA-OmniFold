#!/bin/bash
# COV2D connect A2-TESTS: A2's section 6 step 1, the suites in the cluster environments at A2's binding M, before AR23's
# rerun. The suites as binding 2's ruling 5 (0 node-h); A2's both-direction guard tests must be seen running on Linux.
# A fresh clone at M in /dev/shm on a login node; each suite in its own process, in the environment(s) the amendment's
# section 8 names for it (and, where its code runs in more than one, in each):
#   P  = omnifold_py310 (no ROOT): step A, readouts, null, scorer, jobs (the submit side), cov2d
#   R  = root_6_28 by full prefix through the conda 24.10.0 hook, no MAT: blocks, null, scorer
#   RM = root_6_28 + the pinned MAT environment (run_check_mat_setup, then $A/setup_salloc_env.sh): step B, pilot,
#        jobs (the in-job check), cov2d (deploy_head)
# No data are read. The only pscratch reads are RM's own setup: the pinned MAT setup scripts and libraries under $A,
# as in every earlier COV2D connect. A Python audit hook in the runner records any open/listdir/scandir of a /pscratch
# or /global/cfs path by the suites themselves (reported, not blocked). Porcelain (plain and --ignored) before and
# after. login02, nice 19, taskset -c 8-11, threads 1. Everything under /dev/shm is removed at the end but the logs,
# which are fetched and then removed (logged).
# Then the deploy for the rerun is made, a fresh clean clone at M on pscratch, and the submission's quota check (A2,
# option (c): showquota against the seven shared inputs' sizes, stat only) runs on this login node from the clone.
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-a2tests2.sh >/dev/null 2>&1 </dev/null &
M=a60547692df5f963e428cdfe4661fc51ab785b7b
W=/dev/shm/josephrb-cov2d-a2tests2; DD=$W/deploy; L=$W/logs
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
R628=/global/homes/j/josephrb/.conda/envs/root_6_28
CONDA2410=/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda
RUN="nice -n 19 taskset -c 8-11"
finish() { echo "removal: host=$(hostname) $(date -u +%FT%TZ) $(du -sh "$DD" 2>/dev/null | cut -f1)"; rm -rf "$DD" "$W/tmp" "$W/runsuite.py"; echo "rc=$?"; ls -d "$DD" "$W/tmp" "$W/runsuite.py" 2>&1; echo "end=$(date -u +%FT%TZ)"; echo DONE; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" "$W/tmp" "$L" || exit 2
exec >> "$W/connect-a2tests.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" -c advice.detachedHead=false checkout --quiet --detach "$M" \
    || { echo "STOP clone"; finish; exit 2; }
[ "$(git -C "$DD" rev-parse HEAD)" = "$M" ] || { echo "STOP head"; finish; exit 2; }
porc() { echo "porcelain-$1 plain=$(git -C "$DD" status --porcelain | wc -l) ignored=$(git -C "$DD" status --porcelain --ignored | wc -l)"; git -C "$DD" status --porcelain --ignored | head -20; }
echo "head=$(git -C "$DD" rev-parse HEAD)"; porc before
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
import sys, numpy
def v(m):
    try:
        mod = __import__(m)
        return getattr(mod, '__version__', None) or (mod.gROOT.GetVersion() if m == 'ROOT' else '?')
    except Exception as e:
        return 'absent (' + type(e).__name__ + ')'
print('ENV $1', sys.executable, sys.version.split()[0], 'numpy', numpy.__version__, 'uproot', v('uproot'), 'ROOT', v('ROOT'))
"; }
suite() { local e=$1 m=$2; (cd "$T" && $RUN "$PYX" -B "$W/runsuite.py" "$e" "$m" > "$L/${e}_$m.log" 2>&1); echo "rc env=$e module=$m rc=$?"; grep "^SUITE \|^GUARDED " "$L/${e}_$m.log"; }
# P: omnifold_py310
(
  PYX=$PY310
  envinfo P
  for m in test_cov2d_pseudo test_cov2d_readouts test_cov2d_null test_cov2d_score test_cov2d_jobs test_cov2d; do suite P $m; done
)
# R: root_6_28 by prefix, no MAT
(
  eval "$("$CONDA2410" shell.bash hook 2>/dev/null)" && conda activate "$R628" || exit 3
  export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  PYX=$(command -v python); [ "$PYX" = "$R628/bin/python" ] || { echo "R python is $PYX"; exit 3; }
  envinfo R
  for m in test_cov2d_blocks test_cov2d_null test_cov2d_score; do suite R $m; done
); echo "R rc=$?"
# RM: root_6_28 + the pinned MAT environment
(
  "$PY310" -B -c "import sys; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; r.run_check_mat_setup(None)" || exit 7
  source "$A/setup_salloc_env.sh" > /dev/null 2>&1 || exit 3
  export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  PYX=$(command -v python); echo "RM python=$PYX"     # whatever the MAT setup leaves on PATH: the jobs' python
  "$PYX" -B -c "import sys, json; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; m = r.mat_environment(); print('MAT ' + json.dumps({'mapped': m['mapped_mat_files'], 'dictionary': m['plotutils_mnvh1d_dictionary']}))" || exit 8
  envinfo RM
  for m in test_cov2d_pseudo_write test_cov2d_pilot test_cov2d_jobs test_cov2d; do suite RM $m; done
); echo "RM rc=$?"
porc after
# A2 section 4: the both-direction guard tests ran on Linux (real O_NOATIME, no emulation), not skipped
for t in "P_test_cov2d_pseudo test_inputs_are_staged_and_the_guard_records_its_values" "P_test_cov2d_pseudo test_a_plain_read_of_a_staged_copy_stops"          "RM_test_cov2d_pseudo_write test_inputs_are_staged_root_reads_working_copies_and_the_guard_records" "RM_test_cov2d_pseudo_write test_a_plain_read_of_a_staged_copy_stops"; do
    set -- $t; grep -q "^$2 .* ok$" "$L/$1.log" && echo "GUARD-TEST RAN-OK $1 $2" || echo "GUARD-TEST NOT-OK $1 $2"
done
# the deploy, then the submission's quota check on login
C=/pscratch/sd/j/josephrb/cov2d-deploy-a6054769
if [ -e "$C" ]; then echo "STOP the deploy $C exists"; else
  git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$C" && git -C "$C" -c advice.detachedHead=false checkout --quiet --detach "$M"     && echo "deploy=$C head=$(git -C "$C" rev-parse HEAD) plain=$(git -C "$C" status --porcelain | wc -l) ignored=$(git -C "$C" status --porcelain --ignored | wc -l)"
  # A2 (option (c)): the submission's quota check, as the gate runs it, on this login node: showquota against the
  # seven shared inputs' sizes (stat only)
  $RUN "$PY310" -B -c "import os, sys; sys.path[:0] = ['$DD/2d-unfolding/cov2d', '$DD/2d-unfolding/cov2d/jobs']; import cov2d as c, cov2d_jobs as cj; need = sum(os.stat(p).st_size for p in cj.staged_inputs('AR23')); t = c.read_quota(); print(t); print('STAGED-BYTES', need); print('HEADROOM-PROBLEM', c.headroom_problem(need, t))" > "$L/quota_login.log" 2>&1
  echo "quota rc=$?"; grep "pscratch\|^STAGED-BYTES\|^HEADROOM-PROBLEM" "$L/quota_login.log"
  echo "deploy after: plain=$(git -C "$C" status --porcelain | wc -l) ignored=$(git -C "$C" status --porcelain --ignored | wc -l)"
fi
(cd "$L" && sha256sum *.log blobs.txt) > "$L/SHA256SUMS"
echo "TESTS-SUMMARY $(grep -c '^SUITE .* ok=True' "$W/connect-a2tests.log") ok of $(grep -c '^SUITE ' "$W/connect-a2tests.log") suite runs"
finish
