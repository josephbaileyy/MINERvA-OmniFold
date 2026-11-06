#!/bin/bash
# REF-C2C1's test run with RooUnfold, attempt 2 (the director's ruling of 2026-11-05 on #787; attempt 1's RUN FAIL is
# fd/receipts-ref-c2c1/code-cluster/attempt-1/, #793), on a login node, 0 node-h: a fresh
# clean clone at #787's head H, with the eight files of 2d-unfolding/ref_c2c1/ verified by blob
# (run_tests.sh is a7dd2373... by sha256, EXPECT=29); libRooUnfold.so (0b34e1e3...)
# with its rdict .pcm and .rootmap copied by O_NOATIME read into $P/libcopy/, as the preconditions run did (#779); then
# `bash 2d-unfolding/ref_c2c1/run_tests.sh <the copy> <root_6_28 python3>` in the root_6_28 environment, pinned by
# taskset to 8 CPUs (LightGBM sizes its pool from the affinity) at nice 19. PASS needs rc 0 and run_tests.sh's own line (printed by
# run_suite.py check from unittest's result object) "RUN PASS: 29 tests, none skipped, failed or errored; Ibu.test_roounfold_bayes_is_the_same_update ok".
# COV2D fence (#798): refuses before writing anything if any cov2d-* job is queued or running (or squeue fails); stats
# (no read) the flux constraint, E_R's products and the publication before and after, and STOPs if any atime moved.
# Also stats (no read) owner, mode and atime of the two CFS sources step two's staging will read ($CV, $MC).
# TMPDIR is $P/tmp, so run_tests.sh's mktemp and the tests' temporary directories stay under $P. Porcelain, with --ignored, before and after. Writes only under a NEW $P
# (test.log, test.done, the library copies and this script's copy). No set -u. Launched from a /dev/shm copy of
# itself (its path is $1), which it deletes at exit.
SELF=$1
H=9f593aa5abc5760e6ca96f22e0fc912ce93164a3
P=/pscratch/sd/j/josephrb/ref-c2c1-20261105/tests-9f593aa5
D=$P/deploy
LIBDIR=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
fence=$(squeue -u josephrb -h -o '%i|%j|%T') || bail                  # the COV2D fence (#798)
printf '%s\n' "$fence" | awk -F'|' '$2 ~ /^cov2d-/ {f=1} END {exit f}' || bail
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
echo "COV2D fence: no cov2d-* job in squeue at $(date -u +%FT%TZ)"
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
96dbbaa223a3dec4ceba80686f07721e87ec9045 2d-unfolding/ref_c2c1/config.json
128b4e00505f82153d1d400a482b7b1a5a3d56be 2d-unfolding/ref_c2c1/ref_c2c1.py
0e80efd2d927390e4360cf10134e5b74e7554deb 2d-unfolding/ref_c2c1/ref_c2c1_mutation.py
e51367aa3d9d68b8c89f76cd7f556c70bd4a226f 2d-unfolding/ref_c2c1/ref_c2c1_read.py
f2711d4ea81141205f6ef8a450707051713faf20 2d-unfolding/ref_c2c1/run_suite.py
f4dbaf1fe57bcf4ab0f128d70c1725aa64ae8d29 2d-unfolding/ref_c2c1/run_tests.sh
0d2f1a2445fe22130be94635cabb280837be4edb 2d-unfolding/ref_c2c1/test_ref_c2c1.py
990ec7894a982709298ce3550ffa3fa1e73fe1b9 2d-unfolding/ref_c2c1/test_run_suite.py
BLOBS
rt=$(sha256sum "$D/2d-unfolding/ref_c2c1/run_tests.sh" | cut -d' ' -f1); echo "run_tests.sh sha256 $rt"
[ "$rt" = a7dd23736278bc4201dfdc2251b3398ea354493196b2ed9066ec9ea750f1b5af ] || bad=$((bad + 1))
grep -qx 'EXPECT=29' "$D/2d-unfolding/ref_c2c1/run_tests.sh" || { echo "EXPECT is not 29"; bad=$((bad + 1)); }
echo "pinned blobs: $bad mismatches"; [ "$bad" -eq 0 ] || { echo "STOP: the pinned bytes differ"; finish 9; }
for f in libRooUnfold.so libRooUnfold_rdict.pcm libRooUnfold.rootmap; do
  dd if="$LIBDIR/$f" iflag=noatime status=none of="$P/libcopy/$f" || { echo "STOP: copying $f"; finish 4; }
  echo "$f copied: sha256 $(sha256sum "$P/libcopy/$f" | cut -d' ' -f1)"
done
[ "$(sha256sum "$P/libcopy/libRooUnfold.so" | cut -d' ' -f1)" = 0b34e1e39102b0dddc5923dad7f69e59c70cd6a2fcbcef07728b72cf2933fefd ] || { echo "STOP: libRooUnfold.so is not the listed 0b34e1e3"; finish 4; }
(
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 2; }
  export LD_LIBRARY_PATH="$P/libcopy:${LD_LIBRARY_PATH:-}" TMPDIR="$P/tmp"; mkdir -p "$TMPDIR"
  echo "== taskset -c 0-7, nice 19"
  taskset -c 0-7 nice -n 19 bash "$D/2d-unfolding/ref_c2c1/run_tests.sh" "$P/libcopy/libRooUnfold.so" "$PY"
)
rc=$?
echo "run_tests.sh rc=$rc"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
git -C "$D" status --porcelain --ignored | head -10
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
stat -c '%X %n' "${WATCH[@]}" > "$P/watch-after.txt"
if cmp -s "$P/watch-before.txt" "$P/watch-after.txt"; then echo "watched COV2D inputs: no atime moved"; else echo "STOP: a watched COV2D input's atime moved:"; diff "$P/watch-before.txt" "$P/watch-after.txt"; finish 8; fi
grep -qxF 'RUN PASS: 29 tests, none skipped, failed or errored; Ibu.test_roounfold_bayes_is_the_same_update ok' "$P/test.log" && [ $rc = 0 ] || { echo "RUN FAIL (to the director, unrepaired)"; finish 1; }
finish 0
