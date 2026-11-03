#!/bin/bash
# COV2D connect E1: the cluster-env test receipt the director asked for at binding 1 (2026-11-03), before control
# (2a), under COV2D-BINDING-1.md (merged at 95e371700ec57546c459ba029a8e8a616d8ccdee). The code is as bound at
# dec97852f8da840c855777fa3d2179d6548252ee (#723); the tests are at M (#726's merge, the numpy-2 fixture fix), where
# the five bound blobs are asserted unchanged. A login node, 0 node-h, no job. A fresh clone at M in /dev/shm, then:
#   root_6_28 (activated by prefix; no `set -u`, which aborts its activation): test_re2_data_file.py,
#     test_re2_driver.py, test_null205.py. Expected: 16 passed, no skip.
#   omnifold_py310 (uproot 5.6.9, no PyROOT; the env of the receipt R1 and the probes C1 and C2): test_cov2d.py,
#     test_cov2d_writer.py. Expected: 19 passed, and exactly the 18 skips listed below, the tests that need PyROOT
#     and uproot together (skipUnless). Those 18 ran locally only, under conda-forge ROOT 6.28/12 with uproot 5.6.9.
# The receipt FAILS if any test fails or errors, if a pass count differs, or if the skips differ from the expected
# set in either direction (the director's condition), or if the porcelain is not empty after.
# No pscratch or CFS path is read or written: the clone, TMPDIR and every log are under $W in /dev/shm. pytest runs
# with -B, PYTHONDONTWRITEBYTECODE=1 and -p no:cacheprovider.
# Run: setsid nohup bash /dev/shm/josephrb-cov2d-e1.sh >/dev/null 2>&1 </dev/null &
M=c96c97f392f7402791e921ccdac952e74d454cee
W=/dev/shm/josephrb-cov2d-e1; DD=$W/deploy
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
CONDA=/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda
FAIL=0
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit 2; }
check() {  # $1 pytest -v log, $2 expected-skips file, $3 expected pass count, $4 label
  awk '$2=="SKIPPED"{print $1}' "$1" | LC_ALL=C sort > "$1.skips"
  LC_ALL=C sort "$2" > "$2.sorted"
  if diff "$2.sorted" "$1.skips" > "$1.skipdiff"; then
    echo "$4 skips: exactly the expected $(wc -l < "$1.skips")"
  else
    echo "$4 skips: FAIL, they differ from the expected set (< expected only, > actual only):"; cat "$1.skipdiff"; FAIL=1
  fi
  if grep -Eq '^[^ ]+ (FAILED|ERROR)' "$1"; then echo "$4: FAIL, a test failed or errored"; FAIL=1; fi
  p=$(awk '$2=="PASSED"' "$1" | wc -l)
  if [ "$p" -eq "$3" ]; then echo "$4 passed: $p, as expected"; else echo "$4 passed: FAIL, $p, expected $3"; FAIL=1; fi
}
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" "$W/tmp" || exit 2
exec >> "$W/connect-e1.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
: > "$W/expected_root628.skips"
cat > "$W/expected_py310.skips" <<'EOF'
2d-unfolding/cov2d/tests/test_cov2d_writer.py::File::test_control_fires_on_a_changed_row
2d-unfolding/cov2d/tests/test_cov2d_writer.py::File::test_control_fires_on_a_dropped_row
2d-unfolding/cov2d/tests/test_cov2d_writer.py::File::test_control_fires_on_a_leaf_type
2d-unfolding/cov2d/tests/test_cov2d_writer.py::File::test_control_fires_on_the_parameter
2d-unfolding/cov2d/tests/test_cov2d_writer.py::File::test_control_passes_on_the_writer
2d-unfolding/cov2d/tests/test_cov2d_writer.py::File::test_refuses_unequal_columns
2d-unfolding/cov2d/tests/test_cov2d_writer.py::File::test_schema_and_parameter
2d-unfolding/cov2d/tests/test_cov2d.py::Receipt::test_a_nonpositive_truth_cell_stops
2d-unfolding/cov2d/tests/test_cov2d.py::Receipt::test_an_unequal_band_is_not_certified_by_its_largest_universe
2d-unfolding/cov2d/tests/test_cov2d.py::Receipt::test_atime_move_stops
2d-unfolding/cov2d/tests/test_cov2d.py::Receipt::test_compounding_row_stops
2d-unfolding/cov2d/tests/test_cov2d.py::Receipt::test_driver_names_without_root_equal_the_import
2d-unfolding/cov2d/tests/test_cov2d.py::Receipt::test_mild_bank_passes_and_every_row_is_evaluated
2d-unfolding/cov2d/tests/test_cov2d.py::Receipt::test_negative_composites_are_counted
2d-unfolding/cov2d/tests/test_cov2d.py::Receipt::test_nonfinite_weights_are_zeroed_and_counted
2d-unfolding/cov2d/tests/test_cov2d.py::Receipt::test_the_bound_is_exact_at_the_edge
2d-unfolding/cov2d/tests/test_cov2d.py::Receipt::test_truth_cell_matches_a_th2d
2d-unfolding/cov2d/tests/test_cov2d.py::Receipt::test_truth_cells_are_recomputed_independently
EOF
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "porcelain_before_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
(cd "$DD" && git ls-tree HEAD 2d-unfolding/re2/re2_driver.py 2d-unfolding/cov2d/cov2d.py 2d-unfolding/cov2d/cov2d_receipt.py \
  2d-unfolding/cov2d/cov2d_writer.py nd-unfolding/fd_1b_null.py) > "$W/bound.blobs"
cat "$W/bound.blobs"
for b in 97f26a1d03be8cf14cdb6e0ce05e794f66f9b571 7dafdd3ff827378554931bd1b3d1f19aeeabe11d \
         d5718bf44c2084c20c30a8b8614e9c40e6fbeee3 2402ed4b656cfc9e0bfcaf32e1870672cfb9074d \
         1810161d53c6b849d0dce7fb506d88d551d89900; do
  grep -q " $b	" "$W/bound.blobs" || stop "bound blob $b missing at M"
done
echo "bound blobs: 5 of 5 at M"
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1
cd "$DD" || stop cd

echo "== root_6_28"
(
  eval "$("$CONDA" shell.bash hook)" && conda activate "$HOME/.conda/envs/root_6_28" || { echo "activate failed"; exit 3; }
  echo "python=$(command -v python)"
  python -c "import sys, numpy, ROOT, pytest; print(sys.version.split()[0], 'numpy', numpy.__version__, 'ROOT', ROOT.gROOT.GetVersion(), 'pytest', pytest.__version__)"
  python -c "import uproot" 2>&1 | tail -1
  python -c "import lightgbm, sklearn; print('lightgbm', lightgbm.__version__, 'sklearn', sklearn.__version__)"
  python -B -m pytest -v -rs -p no:cacheprovider 2d-unfolding/re2/tests/test_re2_data_file.py \
    2d-unfolding/re2/tests/test_re2_driver.py 2d-unfolding/cov2d/tests/test_null205.py > "$W/tests_root628.out" 2>&1
  echo "root_6_28 pytest rc=$?"
)
echo "root_6_28 subshell rc=$?"
tail -3 "$W/tests_root628.out"
check "$W/tests_root628.out" "$W/expected_root628.skips" 16 root_6_28

echo "== omnifold_py310"
"$PY310" -c "import sys, numpy, uproot, pytest; print(sys.version.split()[0], 'numpy', numpy.__version__, 'uproot', uproot.__version__, 'pytest', pytest.__version__)"
"$PY310" -c "import ROOT" 2>&1 | tail -1
"$PY310" -B -m pytest -v -rs -p no:cacheprovider 2d-unfolding/cov2d/tests/test_cov2d.py \
  2d-unfolding/cov2d/tests/test_cov2d_writer.py > "$W/tests_py310.out" 2>&1
echo "omnifold_py310 pytest rc=$?"
tail -3 "$W/tests_py310.out"
check "$W/tests_py310.out" "$W/expected_py310.skips" 19 omnifold_py310

echo "== envs with uproot and ROOT on disk (descriptive: a directory listing, not an import)"
for e in "$HOME"/.conda/envs/*/; do
  u=$(ls -d "$e"lib/python3*/site-packages/uproot 2>/dev/null | head -1); r=$(ls -d "$e"lib/python3*/site-packages/ROOT "$e"lib/ROOT 2>/dev/null | head -1)
  echo "$(basename "$e") uproot=${u:+yes} ROOT=${r:+yes}"
done

n=$(git -C "$DD" status --porcelain | wc -l); echo "porcelain_after_lines=$n head=$(git -C "$DD" rev-parse HEAD)"
git -C "$DD" status --porcelain | head -20
[ "$n" = "0" ] || { echo "porcelain after: FAIL"; FAIL=1; }
sha256sum "$W/tests_root628.out" "$W/tests_py310.out"
if [ "$FAIL" = "0" ]; then echo "E1 PASS"; else echo "E1 FAIL"; fi
echo "end=$(date -u +%FT%TZ)"
echo DONE
