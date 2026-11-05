#!/bin/bash
# REF-C2C1's test run with RooUnfold (the director's ruling of 2026-11-05 on #787), on a login node, 0 node-h: a fresh
# clean clone at #787's head H, with the six files of 2d-unfolding/ref_c2c1/ verified by blob
# (run_tests.sh is ac786355... by sha256); libRooUnfold.so (0b34e1e3...)
# with its rdict .pcm and .rootmap copied by O_NOATIME read into $P/libcopy/, as the preconditions run did (#779); then
# `bash 2d-unfolding/ref_c2c1/run_tests.sh <the copy> <root_6_28 python3>` in the root_6_28 environment, pinned by
# taskset to 8 CPUs (LightGBM sizes its pool from the affinity) at nice 19. PASS needs run_tests.sh's own line "RUN
# PASS: 21 tests, none skipped, C-ROO ran". Porcelain, with --ignored, before and after. Writes only under a NEW $P
# (test.log, test.done, the library copies and this script's copy). No set -u. Launched from a /dev/shm copy of
# itself (its path is $1), which it deletes at exit.
SELF=$1
H=5666f58c8231a1350439af3976bb5390f6b3880b
P=/pscratch/sd/j/josephrb/ref-c2c1-20261105/tests-5666f58c
D=$P/deploy
LIBDIR=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
[ ! -e "$P" ] && [ -x "$PY" ] || bail
mkdir -p "$P/libcopy" || bail
exec > "$P/test.log" 2>&1
finish() { echo "ref-c2c1 test run rc=$1"; date -u +%FT%TZ; echo "$1" > "$P/test.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$P/refc2c1_tests_login.sh"
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
829286a81d8ebbdb706900ef3faeec5c6b39c869 2d-unfolding/ref_c2c1/config.json
011c6c161666928306e98ff19d5a6065b6379bb0 2d-unfolding/ref_c2c1/ref_c2c1.py
eed846181a9b8fda1dc17d3c0dc27ff5409aba4a 2d-unfolding/ref_c2c1/ref_c2c1_mutation.py
0f7c7b0250f6a99626a269134b9144237742d959 2d-unfolding/ref_c2c1/ref_c2c1_read.py
3d40c0a1578a42bbd6f623d8a236b451c90b3868 2d-unfolding/ref_c2c1/run_tests.sh
214a5f1bcae1381c197385abce05b937bfb927db 2d-unfolding/ref_c2c1/test_ref_c2c1.py
BLOBS
rt=$(sha256sum "$D/2d-unfolding/ref_c2c1/run_tests.sh" | cut -d' ' -f1); echo "run_tests.sh sha256 $rt"
[ "$rt" = ac786355a244f71e7146cd7a5ca2861a7514cd79964621aad12da5e0c3c4fa56 ] || bad=$((bad + 1))
echo "pinned blobs: $bad mismatches"; [ "$bad" -eq 0 ] || { echo "STOP: the pinned bytes differ"; finish 9; }
for f in libRooUnfold.so libRooUnfold_rdict.pcm libRooUnfold.rootmap; do
  dd if="$LIBDIR/$f" iflag=noatime status=none of="$P/libcopy/$f" || { echo "STOP: copying $f"; finish 4; }
  echo "$f copied: sha256 $(sha256sum "$P/libcopy/$f" | cut -d' ' -f1)"
done
[ "$(sha256sum "$P/libcopy/libRooUnfold.so" | cut -d' ' -f1)" = 0b34e1e39102b0dddc5923dad7f69e59c70cd6a2fcbcef07728b72cf2933fefd ] || { echo "STOP: libRooUnfold.so is not the listed 0b34e1e3"; finish 4; }
(
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 2; }
  export LD_LIBRARY_PATH="$P/libcopy:${LD_LIBRARY_PATH:-}"
  echo "== taskset -c 0-7, nice 19"
  taskset -c 0-7 nice -n 19 bash "$D/2d-unfolding/ref_c2c1/run_tests.sh" "$P/libcopy/libRooUnfold.so" "$PY"
)
rc=$?
echo "run_tests.sh rc=$rc"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
git -C "$D" status --porcelain --ignored | head -10
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
grep -q '^RUN PASS: 21 tests, none skipped, C-ROO ran$' "$P/test.log" && [ $rc = 0 ] || { echo "RUN FAIL (to the director, unrepaired)"; finish 1; }
finish 0
