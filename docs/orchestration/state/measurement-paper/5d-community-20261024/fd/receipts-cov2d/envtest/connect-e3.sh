#!/bin/bash
#SBATCH -A m3246
#SBATCH -q regular
#SBATCH -C cpu
#SBATCH -N 1
#SBATCH -t 01:30:00
#SBATCH -J cov2d-e3
#SBATCH -o /pscratch/sd/j/josephrb/cov2d-e3/e3-%j.out
# COV2D connect E3: the cluster-env test receipt, after E2 was killed (INVALID): the root_6_28 files ran LightGBM
# unpinned on a shared login node. test_re2_driver.py:4 says LightGBM sizes its thread pool from the CPU affinity and
# ignores OMP_NUM_THREADS, so run it pinned (`taskset -c 8-11`). The director approved (2026-11-03):
#   * the omnifold_py310 part on the login node, as in E2 (1.4 s there);
#   * the three root_6_28 files as an sbatch job on one regular CPU node, CPU only, under 12 h, nothing to CFS, each
#     file under `taskset -c 8-11`, with each live driver child's affinity and thread count recorded in the log;
#   * all of E2's guards: an import preflight STOP, each file in its own interpreter, a signal exit FAIL, unittest's
#     "Ran N" and final "OK" / "OK (skipped=K)" against the expected counts, rc 0, the ok count and the skipped set.
# Added for E3: a sampler reads /proc every 5 s during each root_6_28 file. Any sampled process with a
# Cpus_allowed_list other than 8-11 is a FAIL, and so is a re2 file with no driver child sampled.
# Under COV2D-BINDING-1.md (merged at 95e371700ec57546c459ba029a8e8a616d8ccdee). The code is as bound at
# dec97852f8da840c855777fa3d2179d6548252ee (#723); the tests are at M (#726's merge), where the five bound blobs are
# asserted unchanged. Each part clones M afresh into its own node's /dev/shm. Logs go to $L on pscratch, which is
# small text only. No CFS path is written.
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-e3.sh >/dev/null 2>&1 </dev/null &
#   (it runs the py310 part, removes its clone, and on a clean py310 part submits itself: sbatch <this> root).
M=c96c97f392f7402791e921ccdac952e74d454cee
W=/dev/shm/josephrb-cov2d-e3; DD=$W/deploy; L=/pscratch/sd/j/josephrb/cov2d-e3
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
CONDA=/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda
ROOTENV=$HOME/.conda/envs/root_6_28
CORES=8-11
MODE=${1:-login}
stop() { echo "STOP $*"; echo "E3 FAIL"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit 2; }
fail() { echo "FAIL $*"; echo "$*" >> "$L/fail.flags"; }
parse() {  # unittest -v log -> "module::Class::test status" per test
  awk '/^test[^ ]* \([^)]*\)/ { p = $2; gsub(/[()]/, "", p); split(p, a, "."); key = a[1] "::" a[2] "::" $1 }
       key != "" && / \.\.\. / { s = $0; sub(/.* \.\.\. /, "", s); split(s, b, " "); print key, b[1]; key = "" }' "$1"
}
run_file() {  # $1 python, $2 dir under the clone, $3 module, $4 expected total, $5 expected ok, $6 expected-skips file
  local log="$L/ut_$3.log" rc n k
  (cd "$DD/$2" && $PIN "$1" -B -m unittest -v "$3") > "$log" 2>&1; rc=$?
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
sample() {  # $1 output file: every 5 s, each process of this run: kind=driver (the tests launch every driver run as
            # `python -c "...runpy.run_path(...)"`), kind=unittest, or kind=other (any other process naming $W/)
  local d c k st
  while :; do
    for d in /proc/[0-9]*; do
      c=$(tr '\0' ' ' < "$d/cmdline" 2>/dev/null) || continue
      case "$c" in
        *"-m unittest -v test_"*) k=unittest ;;
        *"$W/"*"runpy.run_path("*) k=driver ;;
        *"$W/"*) k=other ;;
        *) continue ;;
      esac
      # a process exiting mid-read yields no status: skip it rather than log an empty affinity
      st=$(awk '/^Threads:/ {t = $2} /^Cpus_allowed_list:/ {a = $2} END {if (t != "" && a != "") print "threads=" t, "cpus=" a}' "$d/status" 2>/dev/null)
      [ -n "$st" ] && echo "$(date -u +%T) pid=${d#/proc/} kind=$k $st ${c:0:140}"
    done >> "$1"
    sleep 5
  done
}
checkout() {
  git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
  n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "porcelain_before_lines=$n head=$h"
  [ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
  (cd "$DD" && git ls-tree HEAD 2d-unfolding/re2/re2_driver.py 2d-unfolding/cov2d/cov2d.py 2d-unfolding/cov2d/cov2d_receipt.py \
    2d-unfolding/cov2d/cov2d_writer.py nd-unfolding/fd_1b_null.py) > "$L/bound.blobs.$MODE"
  cat "$L/bound.blobs.$MODE"
  for b in 97f26a1d03be8cf14cdb6e0ce05e794f66f9b571 7dafdd3ff827378554931bd1b3d1f19aeeabe11d \
           d5718bf44c2084c20c30a8b8614e9c40e6fbeee3 2402ed4b656cfc9e0bfcaf32e1870672cfb9074d \
           1810161d53c6b849d0dce7fb506d88d551d89900; do
    grep -q " $b	" "$L/bound.blobs.$MODE" || stop "bound blob $b missing at M"
  done
  echo "bound blobs: 5 of 5 at M"
}
porcelain_after() {
  n=$(git -C "$DD" status --porcelain | wc -l); echo "porcelain_after_lines=$n head=$(git -C "$DD" rev-parse HEAD)"
  git -C "$DD" status --porcelain | head -20
  [ "$n" = "0" ] || fail "$MODE: porcelain after: $n lines"
}
remove_clone() {
  echo "removal: host=$(hostname) $(date -u +%FT%TZ) $(du -sh "$W" 2>/dev/null | cut -f1) $W"
  rm -rf "$W"; echo "rm -rf $W rc=$?"; ls -d "$W" 2>&1
}

if [ "$MODE" = login ]; then
  [ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
  [ -e "$L" ] && { echo "STOP $L exists"; exit 2; }
  mkdir "$W" "$W/tmp" "$L" || exit 2
  exec >> "$L/connect-e3-login.log" 2>&1
  echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ mode=login"
  : > "$L/fail.flags"; : > "$L/none.skips"
  cat > "$L/test_cov2d.skips" <<'EOF'
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
  cat > "$L/test_cov2d_writer.skips" <<'EOF'
test_cov2d_writer::File::test_control_fires_on_a_changed_row
test_cov2d_writer::File::test_control_fires_on_a_dropped_row
test_cov2d_writer::File::test_control_fires_on_a_leaf_type
test_cov2d_writer::File::test_control_fires_on_the_parameter
test_cov2d_writer::File::test_control_passes_on_the_writer
test_cov2d_writer::File::test_refuses_unequal_columns
test_cov2d_writer::File::test_schema_and_parameter
EOF
  checkout
  export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1
  PIN=
  echo "== preflight: omnifold_py310"
  "$PY310" -c "import sys, unittest, numpy, uproot; print(sys.version.split()[0], 'numpy', numpy.__version__, 'uproot', uproot.__version__)" || stop "omnifold_py310: runner or module import"
  for m in test_cov2d test_cov2d_writer; do
    (cd "$DD/2d-unfolding/cov2d/tests" && "$PY310" -B -c "import $m") > "$L/pre_$m.log" 2>&1 || { cat "$L/pre_$m.log"; stop "omnifold_py310: import $m"; }
  done
  "$PY310" -c "import ROOT" 2>&1 | tail -1
  echo "== omnifold_py310 suites"
  run_file "$PY310" 2d-unfolding/cov2d/tests test_cov2d 27 16 "$L/test_cov2d.skips"
  run_file "$PY310" 2d-unfolding/cov2d/tests test_cov2d_writer 10 3 "$L/test_cov2d_writer.skips"
  porcelain_after
  remove_clone
  [ -s "$L/fail.flags" ] && { cat "$L/fail.flags"; stop "omnifold_py310 part failed; the job is not submitted"; }
  j=$(sbatch --parsable "$0" root); echo "sbatch rc=$? jobid=$j"
  [ -n "$j" ] || stop "sbatch"
  echo "end=$(date -u +%FT%TZ)"; echo DONE
  exit 0
fi

[ "$MODE" = root ] || { echo "STOP unknown mode $MODE"; exit 2; }
[ -d "$L" ] && [ -f "$L/fail.flags" ] || { echo "STOP $L or its fail.flags is missing"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists on $(hostname)"; exit 2; }
mkdir "$W" "$W/tmp" || exit 2
exec >> "$L/connect-e3-root.log" 2>&1
trap remove_clone EXIT
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ mode=root job=${SLURM_JOB_ID:-none} nproc=$(nproc)"
checkout
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1
echo "== preflight: root_6_28"
(
  eval "$("$CONDA" shell.bash hook)" && conda activate "$ROOTENV" || exit 3
  echo "python=$(command -v python)"
  python -c "import sys, unittest, numpy, ROOT, lightgbm, sklearn; print(sys.version.split()[0], 'numpy', numpy.__version__, 'ROOT', ROOT.gROOT.GetVersion(), 'lightgbm', lightgbm.__version__, 'sklearn', sklearn.__version__)" || exit 4
  for m in re2/tests:test_re2_data_file re2/tests:test_re2_driver cov2d/tests:test_null205; do
    (cd "$DD/2d-unfolding/${m%%:*}" && python -B -c "import ${m##*:}") > "$L/pre_${m##*:}.log" 2>&1 || { cat "$L/pre_${m##*:}.log"; exit 5; }
  done
  python -c "import uproot" 2>&1 | tail -1
  taskset -c "$CORES" awk '/^Cpus_allowed_list:/ {print "taskset check:", $0}' /proc/self/status
  exit 0
) || stop "root_6_28 preflight rc=$?"
echo "== root_6_28 suites, each under taskset -c $CORES"
(
  eval "$("$CONDA" shell.bash hook)" && conda activate "$ROOTENV" || { fail "root_6_28: activate"; exit 3; }
  PYR=$(command -v python)
  PIN="taskset -c $CORES"
  for spec in re2/tests:test_re2_data_file:4:4:driver re2/tests:test_re2_driver:9:9:driver cov2d/tests:test_null205:3:3:none; do
    IFS=: read -r dir mod tot ok drv <<< "$spec"
    s="$L/affinity_$mod.log"; : > "$s"
    sample "$s" & sp=$!
    run_file "$PYR" "2d-unfolding/$dir" "$mod" "$tot" "$ok" "$L/none.skips"
    kill "$sp"; wait "$sp" 2>/dev/null
    echo "$mod sampler: $(wc -l < "$s" | tr -d ' ') samples, $(grep -c ' kind=driver ' "$s") of a driver child, cpus seen: $(grep -o 'cpus=[^ ]*' "$s" | sort | uniq -c | tr '\n' ' ')driver threads (max): $(grep ' kind=driver ' "$s" | grep -o 'threads=[0-9]*' | cut -d= -f2 | sort -n | tail -1)"
    grep -o 'cpus=[^ ]*' "$s" | grep -qv "^cpus=$CORES\$" && fail "$mod: a sampled process ran outside $CORES"
    [ "$drv" = driver ] && ! grep -q ' kind=driver ' "$s" && fail "$mod: no driver child was sampled"
  done
)
porcelain_after
sha256sum "$L"/ut_*.log
echo "fail flags: $(wc -l < "$L/fail.flags" | tr -d ' ')"; cat "$L/fail.flags"
if [ -s "$L/fail.flags" ]; then echo "E3 FAIL"; else echo "E3 PASS"; fi
echo "end=$(date -u +%FT%TZ)"
echo DONE
