#!/bin/bash
# COV2D connect E2: the cluster-env test receipt, after E1 FAILED because neither cluster env has pytest. The director
# approved (2026-11-03) the stdlib runner, `python -m unittest -v`, with nothing installed, and these guards:
#   * an import preflight, before any suite: the runner and every module the suites import must import in their env,
#     and each test module must import, or STOP;
#   * each test file in its own interpreter, from its own directory; a signal exit (rc >= 128) is FAIL;
#   * per file, unittest's own "Ran N tests" with N the file's expected total, the final "OK" or "OK (skipped=K)" with
#     K its expected skips, and rc 0;
#   * per file, the ok count and the skipped set by name exactly as expected, and no FAIL or ERROR.
# Under COV2D-BINDING-1.md (merged at 95e371700ec57546c459ba029a8e8a616d8ccdee). The code is as bound at
# dec97852f8da840c855777fa3d2179d6548252ee (#723); the tests are at M (#726's merge), where the five bound blobs are
# asserted unchanged. A login node, 0 node-h, no job, files run one after another. The 18 tests that need PyROOT and
# uproot together skip in omnifold_py310 and run in no cluster env; they ran locally only, under conda-forge ROOT
# 6.28/12 with uproot 5.6.9. No pscratch or CFS path is read or written: the clone, TMPDIR and every log are under $W in
# /dev/shm. unittest's -v format differs by Python: 3.10 (omnifold_py310) prints `test_x (module.Class) ... ok`, 3.11+
# (root_6_28) `test_x (module.Class.test_x) ... ok`, and a test with a docstring puts its status on the next line;
# `parse` reads all three.
# Run: setsid nohup bash /dev/shm/josephrb-cov2d-e2.sh >/dev/null 2>&1 </dev/null &
M=c96c97f392f7402791e921ccdac952e74d454cee
W=/dev/shm/josephrb-cov2d-e2; DD=$W/deploy
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
CONDA=/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda
ROOTENV=$HOME/.conda/envs/root_6_28
stop() { echo "STOP $*"; echo "E2 FAIL"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit 2; }
fail() { echo "FAIL $*"; echo "$*" >> "$W/fail.flags"; }
parse() {  # unittest -v log -> "module::Class::test status" per test
  awk '/^test[^ ]* \([^)]*\)/ { p = $2; gsub(/[()]/, "", p); split(p, a, "."); key = a[1] "::" a[2] "::" $1 }
       key != "" && / \.\.\. / { s = $0; sub(/.* \.\.\. /, "", s); split(s, b, " "); print key, b[1]; key = "" }' "$1"
}
run_file() {  # $1 python, $2 dir under the clone, $3 module, $4 expected total, $5 expected ok, $6 expected-skips file
  local log="$W/ut_$3.log" rc n k
  (cd "$DD/$2" && "$1" -B -m unittest -v "$3") > "$log" 2>&1; rc=$?
  echo "$3: rc=$rc; $(grep -E '^Ran [0-9]+ tests? in' "$log"); $(tail -n 1 "$log")"
  [ "$rc" -ge 128 ] && fail "$3: signal exit, rc=$rc (signal $((rc - 128)))"
  [ "$rc" -eq 0 ] || fail "$3: rc=$rc"
  n=$(grep -E '^Ran [0-9]+ tests? in' "$log" | awk '{print $2}')
  [ "$n" = "$4" ] || fail "$3: 'Ran ${n:-none}' tests, expected $4"
  k=$(wc -l < "$6" | tr -d ' ')
  if [ "$k" = "0" ]; then want="OK"; else want="OK (skipped=$k)"; fi
  [ "$(grep -v '^[[:space:]]*$' "$log" | tail -n 1)" = "$want" ] || fail "$3: last line is not '$want'"
  parse "$log" > "$log.parsed"
  [ "$(awk '$2 == "ok"' "$log.parsed" | wc -l | tr -d ' ')" = "$5" ] || fail "$3: ok count $(awk '$2 == "ok"' "$log.parsed" | wc -l | tr -d ' '), expected $5"
  awk '$2 == "skipped" {print $1}' "$log.parsed" | LC_ALL=C sort > "$log.skips"
  LC_ALL=C sort "$6" | diff - "$log.skips" > "$log.skipdiff" || { fail "$3: skips differ (< expected only, > actual only)"; cat "$log.skipdiff"; }
  awk '$2 != "ok" && $2 != "skipped"' "$log.parsed" | grep -q . && fail "$3: a test did not pass or skip: $(awk '$2 != "ok" && $2 != "skipped"' "$log.parsed" | tr '\n' ';')"
  [ "$(wc -l < "$log.parsed" | tr -d ' ')" = "$4" ] || fail "$3: parsed $(wc -l < "$log.parsed" | tr -d ' ') tests, expected $4"
}

[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" "$W/tmp" || exit 2
exec >> "$W/connect-e2.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
: > "$W/fail.flags"; : > "$W/none.skips"
cat > "$W/test_cov2d.skips" <<'EOF'
test_cov2d::Receipt::test_a_nonpositive_truth_cell_stops
test_cov2d::Receipt::test_an_unequal_band_is_not_certified_by_its_largest_universe
test_cov2d::Receipt::test_atime_move_stops
test_cov2d::Receipt::test_compounding_row_stops
test_cov2d::Receipt::test_driver_names_without_root_equal_the_import
test_cov2d::Receipt::test_mild_bank_passes_and_every_row_is_evaluated
test_cov2d::Receipt::test_negative_composites_are_counted
test_cov2d::Receipt::test_nonfinite_weights_are_zeroed_and_counted
test_cov2d::Receipt::test_the_bound_is_exact_at_the_edge
test_cov2d::Receipt::test_truth_cell_matches_a_th2d
test_cov2d::Receipt::test_truth_cells_are_recomputed_independently
EOF
cat > "$W/test_cov2d_writer.skips" <<'EOF'
test_cov2d_writer::File::test_control_fires_on_a_changed_row
test_cov2d_writer::File::test_control_fires_on_a_dropped_row
test_cov2d_writer::File::test_control_fires_on_a_leaf_type
test_cov2d_writer::File::test_control_fires_on_the_parameter
test_cov2d_writer::File::test_control_passes_on_the_writer
test_cov2d_writer::File::test_refuses_unequal_columns
test_cov2d_writer::File::test_schema_and_parameter
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

echo "== preflight: omnifold_py310"
"$PY310" -c "import sys, unittest, numpy, uproot; print(sys.version.split()[0], 'numpy', numpy.__version__, 'uproot', uproot.__version__)" || stop "omnifold_py310: runner or module import"
for m in test_cov2d test_cov2d_writer; do
  (cd "$DD/2d-unfolding/cov2d/tests" && "$PY310" -B -c "import $m") > "$W/pre_$m.log" 2>&1 || { cat "$W/pre_$m.log"; stop "omnifold_py310: import $m"; }
done
"$PY310" -c "import ROOT" 2>&1 | tail -1
echo "== preflight: root_6_28"
(
  eval "$("$CONDA" shell.bash hook)" && conda activate "$ROOTENV" || exit 3
  echo "python=$(command -v python)"
  python -c "import sys, unittest, numpy, ROOT, lightgbm, sklearn; print(sys.version.split()[0], 'numpy', numpy.__version__, 'ROOT', ROOT.gROOT.GetVersion(), 'lightgbm', lightgbm.__version__, 'sklearn', sklearn.__version__)" || exit 4
  for m in re2/tests:test_re2_data_file re2/tests:test_re2_driver cov2d/tests:test_null205; do
    (cd "$DD/2d-unfolding/${m%%:*}" && python -B -c "import ${m##*:}") > "$W/pre_${m##*:}.log" 2>&1 || { cat "$W/pre_${m##*:}.log"; exit 5; }
  done
  python -c "import uproot" 2>&1 | tail -1
  exit 0
) || stop "root_6_28 preflight rc=$?"

echo "== omnifold_py310 suites"
run_file "$PY310" 2d-unfolding/cov2d/tests test_cov2d 27 16 "$W/test_cov2d.skips"
run_file "$PY310" 2d-unfolding/cov2d/tests test_cov2d_writer 10 3 "$W/test_cov2d_writer.skips"
echo "== root_6_28 suites"
(
  eval "$("$CONDA" shell.bash hook)" && conda activate "$ROOTENV" || { fail "root_6_28: activate"; exit 3; }
  PYR=$(command -v python)
  run_file "$PYR" 2d-unfolding/re2/tests test_re2_data_file 4 4 "$W/none.skips"
  run_file "$PYR" 2d-unfolding/re2/tests test_re2_driver 9 9 "$W/none.skips"
  run_file "$PYR" 2d-unfolding/cov2d/tests test_null205 3 3 "$W/none.skips"
)

echo "== envs with uproot and ROOT on disk (descriptive: a directory listing, not an import)"
for e in "$HOME"/.conda/envs/*/; do
  u=$(ls -d "$e"lib/python3*/site-packages/uproot 2>/dev/null | head -1); r=$(ls -d "$e"lib/python3*/site-packages/ROOT "$e"lib/ROOT 2>/dev/null | head -1)
  echo "$(basename "$e") uproot=${u:+yes} ROOT=${r:+yes}"
done
n=$(git -C "$DD" status --porcelain | wc -l); echo "porcelain_after_lines=$n head=$(git -C "$DD" rev-parse HEAD)"
git -C "$DD" status --porcelain | head -20
[ "$n" = "0" ] || fail "porcelain after: $n lines"
sha256sum "$W"/ut_*.log
echo "fail flags: $(wc -l < "$W/fail.flags" | tr -d ' ')"; cat "$W/fail.flags"
if [ -s "$W/fail.flags" ]; then echo "E2 FAIL"; else echo "E2 PASS"; fi
echo "end=$(date -u +%FT%TZ)"
echo DONE
