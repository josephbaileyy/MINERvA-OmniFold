#!/bin/bash
# COV2D connect A5-TESTS: addendum A5's tests in the cluster environments at the A5 code head, 0 node-h. Derived from
# ../../a4/cluster_tests/connect-a4t.sh (same runner, audit hook, porcelain and removal). A fresh clone at H5 in /dev/shm
# on a login node, plus a second worktree at the readout's M (ac25b665) for a before/after comparison of the two suites
# whose code A5 changes outside the driver (1B's test_fd_1b_mc; test_cov2d_readouts): the set of failing or erroring
# tests at H5 must equal the set at M in each environment (1B's default unchanged; no regression).
#   RM = root_6_28 + the pinned MAT environment (the driver's): readout, score, readouts, blocks, null, cov2d at H5
#   R  = root_6_28 by prefix, no MAT: readout, score at H5; test_fd_1b_mc and test_cov2d_readouts at H5 and at M
#   P  = omnifold_py310: test_fd_1b_mc and test_cov2d_readouts at H5 and at M
# No data are read; RM's only pscratch reads are its MAT setup, as before. login02, nice 19, taskset -c 8-11, threads 1.
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-a5t.sh >/dev/null 2>&1 </dev/null &
H5=49e4202269ff3d3a6250b824f39c9347680f6b6e
M=ac25b66533788ceb18b1d4e5add259c53b216669   # the readout's M (COV2D-BINDING-2 addendum A4): the before of before/after
W=/dev/shm/josephrb-cov2d-a5t; DD=$W/deploy; DM=$W/deploy-m; L=$W/logs
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
R628=/global/homes/j/josephrb/.conda/envs/root_6_28
CONDA2410=/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda
RUN="nice -n 19 taskset -c 8-11"
finish() { echo "removal: host=$(hostname) $(date -u +%FT%TZ) $(du -sh "$DD" 2>/dev/null | cut -f1)"; git -C "$DD" worktree remove --force "$DM" 2>/dev/null; rm -rf "$DM" "$DD" "$W/tmp" "$W/runsuite.py"; echo "rc=$?"; ls -d "$DM" "$DD" "$W/tmp" "$W/runsuite.py" 2>&1; echo "end=$(date -u +%FT%TZ)"; echo DONE; }
case "$H5" in *[!0-9a-f]*|"") echo "STOP H5 is not set"; exit 2 ;; esac
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" "$W/tmp" "$L" || exit 2
exec >> "$W/connect-a5t.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" -c advice.detachedHead=false checkout --quiet --detach "$H5" \
    || { echo "STOP clone"; finish; exit 2; }
[ "$(git -C "$DD" rev-parse HEAD)" = "$H5" ] || { echo "STOP head"; finish; exit 2; }
git -C "$DD" worktree add --quiet --detach "$DM" "$M" && [ "$(git -C "$DM" rev-parse HEAD)" = "$M" ] || { echo "STOP worktree at M"; finish; exit 2; }
echo "worktree-m=$(git -C "$DM" rev-parse HEAD)"
porc() { echo "porcelain-$1 plain=$(git -C "$DD" status --porcelain | wc -l) ignored=$(git -C "$DD" status --porcelain --ignored | wc -l)"; git -C "$DD" status --porcelain --ignored | head -20; }
echo "head=$(git -C "$DD" rev-parse HEAD)"; porc before
echo "A5 diff M..H5 (code):"; git -C "$DD" diff --stat "$M" "$H5" -- 2d-unfolding nd-unfolding
for f in 2d-unfolding/cov2d/cov2d.py 2d-unfolding/cov2d/cov2d_blocks.py 2d-unfolding/cov2d/cov2d_null.py; do
    git -C "$DD" diff --quiet "$M" "$H5" -- "$f" && echo "UNCHANGED $f" || echo "CHANGED $f"
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
suite() { local e=$1 m=$2 d=${3:-$T} tag=${4:-}; (cd "$d" && $RUN "$PYX" -B "$W/runsuite.py" "$e$tag" "$m" > "$L/${e}${tag}_$m.log" 2>&1); echo "rc env=$e$tag module=$m rc=$?"; grep "^SUITE \|^GUARDED " "$L/${e}${tag}_$m.log"; }
NT=$DD/nd-unfolding/tests; TM=$DM/2d-unfolding/cov2d/tests; NTM=$DM/nd-unfolding/tests
both() { local e=$1; suite "$e" test_fd_1b_mc "$NT"; suite "$e" test_fd_1b_mc "$NTM" "-M"; suite "$e" test_cov2d_readouts "$T"; suite "$e" test_cov2d_readouts "$TM" "-M"; }
# RM: root_6_28 + the pinned MAT environment
(
  "$PY310" -B -c "import sys; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; r.run_check_mat_setup(None)" || exit 7
  source "$A/setup_salloc_env.sh" > /dev/null 2>&1 || exit 3
  export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  PYX=$(command -v python); echo "RM python=$PYX"
  "$PYX" -B -c "import sys, json; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; m = r.mat_environment(); print('MAT ' + json.dumps({'mapped': m['mapped_mat_files'], 'dictionary': m['plotutils_mnvh1d_dictionary']}))" || exit 8
  envinfo RM
  for m in test_cov2d_readout test_cov2d_score test_cov2d_readouts test_cov2d_blocks test_cov2d_null test_cov2d; do suite RM $m; done
); echo "RM rc=$?"
# R: root_6_28 by prefix, no MAT
(
  eval "$("$CONDA2410" shell.bash hook 2>/dev/null)" && conda activate "$R628" || exit 3
  export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  PYX=$(command -v python); [ "$PYX" = "$R628/bin/python" ] || { echo "R python is $PYX"; exit 3; }
  envinfo R
  for m in test_cov2d_readout test_cov2d_score; do suite R $m; done
  both R
); echo "R rc=$?"
# P: omnifold_py310
(
  PYX=$PY310
  envinfo P
  both P
); echo "P rc=$?"
porc after
# A5's tests ran, ok, not skipped: the first ' ... <status>' line at or after the test's own line is its status
# (a test with a docstring prints its status on the next line)
ranok() { awk -v t="$1" '$1==t{f=1} f&&/ \.\.\. /{s=$0; exit} END{exit !(s ~ / \.\.\. ok$/)}' "$2"; }
for e in RM R; do
  for t in test_kappa_1e12_in_both_C_T_and_C_T_minus_grades_under_a5 test_each_tolerance_is_recorded_from_its_matrix_before_any_toy_and_passed_to_its_grade test_a_refusal_of_the_C_T_grade_writes_the_invalid_record_and_finishes_run test_a_refusal_of_the_C_T_minus_grade_writes_the_invalid_record_and_finishes_run test_a_cov2d_refusal_inside_the_try_stays_a_refusal_not_a_grade_refusal test_any_other_failure_inside_the_try_propagates_unrecorded test_the_formula test_the_floor_is_1b_s_1e_9; do
    ranok "$t" "$L/${e}_test_cov2d_readout.log" && echo "A5-TEST RAN-OK $e $t" || echo "A5-TEST NOT-OK $e $t"
  done
done
for e in R P; do
  for t in test_the_fixture_is_full_rank_and_ill_conditioned test_1b_default_is_1e_9_and_refuses_here_with_its_message test_a5_tolerance_passes_and_reports_the_compared_values test_a_wrong_cholesky_refuses_at_the_a5_tolerance test_below_full_rank_the_check_is_skipped_and_reported_so test_well_conditioned_grades_are_unchanged_by_the_argument; do
    ranok "$t" "$L/${e}_test_fd_1b_mc.log" && echo "A5-TEST RAN-OK $e $t" || echo "A5-TEST NOT-OK $e $t"
  done
  # before/after: the failing or erroring tests at H5 equal those at M
  for m in test_fd_1b_mc test_cov2d_readouts; do
    fh=$(grep -E '^(ERROR|FAIL): ' "$L/${e}_$m.log" | sort | tr '\n' ';'); fm=$(grep -E '^(ERROR|FAIL): ' "$L/${e}-M_$m.log" | sort | tr '\n' ';')
    [ "$fh" = "$fm" ] && echo "SAME-FAILURES $e $m [$fh]" || echo "FAILURES-DIFFER $e $m H5=[$fh] M=[$fm]"
  done
done
(cd "$L" && sha256sum *.log blobs.txt) > "$L/SHA256SUMS"
echo "TESTS-SUMMARY $(grep -c '^SUITE .* ok=True' "$W/connect-a5t.log") ok of $(grep -c '^SUITE ' "$W/connect-a5t.log") suite runs"
finish
