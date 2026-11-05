#!/bin/bash
# REF-C2C1's test run with RooUnfold (the director's ruling of 2026-11-05 on #787): all 29 tests of
# test_ref_c2c1.py in the named environment, with REF_C2C1_ROOUNFOLD set to the libRooUnfold.so given, failing unless
# every test ran, none failed, and the C-ROO test (RooUnfoldBayes against the numpy update) ran rather than skipped,
# all read from unittest's result object by run_suite.py (not from the verbose text, which RooUnfold's stdout interleaves).
#
#   bash 2d-unfolding/ref_c2c1/run_tests.sh /path/to/libRooUnfold.so [PYTHON]
#
# PYTHON defaults to the cluster's root_6_28 interpreter (PyROOT, LightGBM, scikit-learn, matplotlib). LightGBM sizes
# its pool from the CPU affinity, so run it pinned (taskset), as RE-2's suite says. Writes nothing in the checkout:
# the tests use temporary directories and -B with PYTHONDONTWRITEBYTECODE.
set -u
LIB=${1:?usage: run_tests.sh LIBROOUNFOLD [PYTHON]}
PY=${2:-/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3}
EXPECT=29
HERE=$(cd "$(dirname "$0")" && pwd)
[ -s "$LIB" ] || { echo "refusing: $LIB is missing or empty" >&2; exit 2; }
[ -x "$PY" ] || { echo "refusing: $PY is not an executable interpreter" >&2; exit 2; }
echo "== environment"
echo "interpreter: $PY"
"$PY" -c "import sys, numpy, ROOT, lightgbm, sklearn, matplotlib; print('python', sys.version.split()[0]); print('numpy', numpy.__version__, '| ROOT', ROOT.gROOT.GetVersion(), '| lightgbm', lightgbm.__version__, '| scikit-learn', sklearn.__version__, '| matplotlib', matplotlib.__version__)" \
  || { echo "RUN FAIL: the environment lacks a required module" >&2; exit 1; }
echo "libRooUnfold: $LIB sha256 $(sha256sum "$LIB" 2>/dev/null | cut -d' ' -f1)"
echo "== tests"
out=$(mktemp -d)
# outcomes come from unittest's result object (run_suite.py), never from the text: RooUnfoldBayes prints to stdout
# between a test's name and its "ok", and that stdout stays in this log
(cd "$HERE/.." && REF_C2C1_ROOUNFOLD="$LIB" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 \
  "$PY" -B ref_c2c1/run_suite.py run ref_c2c1/test_ref_c2c1.py "$out/outcomes.json") 2>&1
rc=$?
echo "== outcomes (unittest's result object)"
cat "$out/outcomes.json" 2>/dev/null || { echo "RUN FAIL: the suite wrote no outcomes (rc $rc)"; exit 1; }
"$PY" -B "$HERE/run_suite.py" check "$out/outcomes.json" "$EXPECT" Ibu.test_roounfold_bayes_is_the_same_update
v=$?
rm -rf "$out"
[ "$rc" -eq 0 ] || { echo "RUN FAIL: the suite exited $rc"; exit 1; }
exit $v
