#!/bin/bash
# REF-C2C1's test run with RooUnfold, attempt 5: the C-PUB operand PR's head H (the director's ruling of 2026-11-06 on
# the 3b control STOP; attempts 1-4 are fd/receipts-ref-c2c1/code-cluster/attempt-1..4/), on a login node, 0 node-h: a
# fresh clean clone at H, with the eight files of 2d-unfolding/ref_c2c1/ verified by blob
# (run_tests.sh is a8fbffd7... by sha256, EXPECT=33); libRooUnfold.so (0b34e1e3...)
# with its rdict .pcm and .rootmap copied by O_NOATIME read into $P/libcopy/, as the preconditions run did (#779); then
# `bash 2d-unfolding/ref_c2c1/run_tests.sh <the copy> <root_6_28 python3>` in the root_6_28 environment, pinned by
# taskset to 8 CPUs (LightGBM sizes its pool from the affinity) at nice 19. PASS needs rc 0 and run_tests.sh's own line (printed by
# run_suite.py check from unittest's result object) "RUN PASS: 33 tests, none skipped, failed or errored; Ibu.test_roounfold_bayes_is_the_same_update ok".
# Then, after the suite and never beside it, the mutation harness (ref_c2c1_mutation.py) in the same environment and
# pinning; PASS also needs its rc 0 and "MUTATION CHECK :: PASS (45 mutations)", unittest's own summary "Ran 33
# tests in" (once) and "OK" (no skips), and porcelain 0. Each run prints its child's env (PYTHONDONTWRITEBYTECODE=1).
# COV2D fence: a recorded line (the director's ruling of 2026-11-06 for guarded readers: the tests read only their own
# temporary fixtures and the repository), the full squeue at launch; stats (no read) the flux constraint, E_R's products
# and the publication before and after, and STOPs if any atime moved.
# Also stats (no read) owner, mode and atime of the two CFS sources step two's staging will read ($CV, $MC).
# TMPDIR is $P/tmp, so run_tests.sh's mktemp and the tests' temporary directories stay under $P. Porcelain, with --ignored, before and after. Writes only under a NEW $P
# (test.log, test.done, the library copies and this script's copy). No set -u. Launched from a /dev/shm copy of
# itself (its path is $1), which it deletes at exit.
SELF=$1
H=5938a1679e25f64e63ea1bbd4826008f43de4360
P=/pscratch/sd/j/josephrb/ref-c2c1-20261106/tests-5938a167
D=$P/deploy
LIBDIR=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
fence=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l') || bail           # the COV2D fence, recorded below
WATCH=(/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
       /pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/ER/xsec.root
       /pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/S1_*/xsec.root
       /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root)
[ ! -e "$P" ] && [ -x "$PY" ] || bail
mkdir -p "$P/libcopy" || bail
exec > "$P/test.log" 2>&1
finish() { echo "ref-c2c1 test run rc=$1"; date -u +%FT%TZ; echo "$1" > "$P/test.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$P/refc2c1_tests_login.sh"
echo "COV2D fence, recorded (the director's ruling of 2026-11-06): squeue -u josephrb at $(date -u +%FT%TZ):"
printf '%s\n' "$fence" | sed 's/^/  /'
# the step-two staging sources on CFS (the director, 2026-11-05): owner, mode, atime by stat only; O_NOATIME needs the
# running user to own the file, so a source not owned by josephrb is reported (staging would refuse)
for f in /global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root \
         /global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/fig_products/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root; do
  o=$(stat -c '%U %a %X' "$f") || { echo "staging source: stat failed for $f"; continue; }
  echo "staging source: $o $f"; case "$o" in "josephrb "*) ;; *) echo "STAGING-OWNER: $f is not owned by josephrb";; esac
done
stat -c '%X %n' "${WATCH[@]}" > "$P/watch-before.txt"; echo "watched COV2D inputs (stat only): $(wc -l < "$P/watch-before.txt") files"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$P/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" fetch -q origin "$H" >> "$P/clone.log" 2>&1
git -C "$D" -c advice.detachedHead=false checkout -q "$H" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$H" ] || { echo "STOP: HEAD is not H"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $H; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$H:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
f27545e9ca70382a318eb284a0c9ea01cc0e5891 2d-unfolding/ref_c2c1/config.json
128b4e00505f82153d1d400a482b7b1a5a3d56be 2d-unfolding/ref_c2c1/ref_c2c1.py
a2ce6e48a0d3b65b3d7467bd7b72dfd0cf436817 2d-unfolding/ref_c2c1/ref_c2c1_mutation.py
1baf74b5163ff36e22fb66c4b13dc17c6a92d400 2d-unfolding/ref_c2c1/ref_c2c1_read.py
f2711d4ea81141205f6ef8a450707051713faf20 2d-unfolding/ref_c2c1/run_suite.py
1d3f971f2b2a3a0cc9cf477b6f11061d8f35f07e 2d-unfolding/ref_c2c1/run_tests.sh
4633f384392cbb7d18e159d72bffbe81aca19a8d 2d-unfolding/ref_c2c1/test_ref_c2c1.py
990ec7894a982709298ce3550ffa3fa1e73fe1b9 2d-unfolding/ref_c2c1/test_run_suite.py
BLOBS
rt=$(sha256sum "$D/2d-unfolding/ref_c2c1/run_tests.sh" | cut -d' ' -f1); echo "run_tests.sh sha256 $rt"
[ "$rt" = a8fbffd781b45e9cbead9d6f940603165662d21cd50c52b5c736c17a649f8c12 ] || bad=$((bad + 1))
grep -qx 'EXPECT=33' "$D/2d-unfolding/ref_c2c1/run_tests.sh" || { echo "EXPECT is not 33"; bad=$((bad + 1)); }
echo "pinned blobs: $bad mismatches"; [ "$bad" -eq 0 ] || { echo "STOP: the pinned bytes differ"; finish 9; }
for f in libRooUnfold.so libRooUnfold_rdict.pcm libRooUnfold.rootmap; do
  dd if="$LIBDIR/$f" iflag=noatime status=none of="$P/libcopy/$f" || { echo "STOP: copying $f"; finish 4; }
  echo "$f copied: sha256 $(sha256sum "$P/libcopy/$f" | cut -d' ' -f1)"
done
[ "$(sha256sum "$P/libcopy/libRooUnfold.so" | cut -d' ' -f1)" = 0b34e1e39102b0dddc5923dad7f69e59c70cd6a2fcbcef07728b72cf2933fefd ] || { echo "STOP: libRooUnfold.so is not the listed 0b34e1e3"; finish 4; }
(
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 2; }
  export LD_LIBRARY_PATH="$P/libcopy:${LD_LIBRARY_PATH:-}" TMPDIR="$P/tmp" PYTHONDONTWRITEBYTECODE=1; mkdir -p "$TMPDIR"
  echo "== taskset -c 0-7, nice 19"
  taskset -c 0-7 nice -n 19 "$PY" -c 'import os; print("child env: PYTHONDONTWRITEBYTECODE=%s OMP_NUM_THREADS=%s affinity=%s nice=%d" % (os.environ.get("PYTHONDONTWRITEBYTECODE"), os.environ.get("OMP_NUM_THREADS"), sorted(os.sched_getaffinity(0)), os.nice(0)))'
  taskset -c 0-7 nice -n 19 bash "$D/2d-unfolding/ref_c2c1/run_tests.sh" "$P/libcopy/libRooUnfold.so" "$PY"
)
rc=$?
echo "run_tests.sh rc=$rc"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after the suite: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
(
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 2; }
  export LD_LIBRARY_PATH="$P/libcopy:${LD_LIBRARY_PATH:-}" TMPDIR="$P/tmp" REF_C2C1_ROOUNFOLD="$P/libcopy/libRooUnfold.so" PYTHONDONTWRITEBYTECODE=1
  echo "== the mutation harness: taskset -c 0-7, nice 19, $(date -u +%FT%TZ)"
  taskset -c 0-7 nice -n 19 "$PY" -c 'import os; print("child env: PYTHONDONTWRITEBYTECODE=%s OMP_NUM_THREADS=%s affinity=%s nice=%d" % (os.environ.get("PYTHONDONTWRITEBYTECODE"), os.environ.get("OMP_NUM_THREADS"), sorted(os.sched_getaffinity(0)), os.nice(0)))'
  cd "$D" && taskset -c 0-7 nice -n 19 "$PY" -B 2d-unfolding/ref_c2c1/ref_c2c1_mutation.py
)
mrc=$?
echo "ref_c2c1_mutation.py rc=$mrc $(date -u +%FT%TZ)"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
git -C "$D" status --porcelain --ignored | head -10
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
stat -c '%X %n' "${WATCH[@]}" > "$P/watch-after.txt"
if cmp -s "$P/watch-before.txt" "$P/watch-after.txt"; then echo "watched COV2D inputs: no atime moved"; else echo "STOP: a watched COV2D input's atime moved:"; diff "$P/watch-before.txt" "$P/watch-after.txt"; finish 8; fi
grep -qxF 'RUN PASS: 33 tests, none skipped, failed or errored; Ibu.test_roounfold_bayes_is_the_same_update ok' "$P/test.log" && [ $rc = 0 ] || { echo "RUN FAIL (to the director, unrepaired)"; finish 1; }
[ "$(grep -c '^Ran 33 tests in ' "$P/test.log")" = 1 ] && grep -qx 'OK' "$P/test.log" || { echo "RUN FAIL: unittest's own summary is not 'Ran 33 tests' and 'OK' (to the director, unrepaired)"; finish 1; }
grep -qxF 'MUTATION CHECK :: PASS (45 mutations)' "$P/test.log" && [ $mrc = 0 ] || { echo "MUTATION FAIL (to the director, unrepaired)"; finish 1; }
finish 0
