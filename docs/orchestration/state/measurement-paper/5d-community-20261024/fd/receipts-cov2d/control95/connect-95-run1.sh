#!/bin/bash
# COV2D connect 95: section 9.5's control (COV2D-DECLARATION.md section 9.5; the director's R2 of 2026-11-04: "a login
# connect in root_6_28 before the pilot, sha first, threads capped"). The amendment's block code (cov2d_blocks.py,
# blob 23495e89, at M = the amendment branch's 6efd7a18; not yet bound) applies the RE-2 rollup's own functions to part
# B's products and must reproduce part B's S5_R blocks (s5/production_cov.npz, 631cf255...: band_<b>, universe, stat)
# to 1e-12, with E_R's reported cells equal to cmodel_2d.json's.
#   * Every product is copied through O_NOATIME and checked against part B's committed sums before ROOT opens the copy;
#     the rollup's own inputs (constraint, VL175 build json and MINOS npz, MEFHC flux, 24 per-playlist flux/POT files)
#     likewise; every input's atime is checked unchanged.
#   * The rollup (re2c_rollup.py e41940cb) and build_cmodel.py (7a987e25) are the blobs part C ran (deploy 903fb78b),
#     asserted here; the five bound blobs (writer at A1's bb3892e5) are asserted unchanged.
#   * The director's open audit: builtins.open, io.open, os.open and ROOT.TFile.Open are wrapped before the rollup
#     is imported; every open is logged and one under /global/cfs or /pscratch that is not a sanctioned O_NOATIME read
#     is refused (INVALID); bypass_scan's list (subprocess, os.system, TFile constructors, copied constants) is recorded.
#   * nice 19, taskset -c 8-11, OMP/OPENBLAS/MKL/NUMEXPR threads 1. A login node, 0 node-h, no job. A fresh clone at M
#     in /dev/shm; porcelain and blobs before and after; the clone removed at the end, logged.
# Verdict: CONTROL-95 PASS (rc 0, "COV2D-9.5 PASS"), FAIL (the control's own STOP, rc 3), else INVALID.
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-95.sh >/dev/null 2>&1 </dev/null &
M=6efd7a18939318deb75cbaa603363ede36bd6121
W=/dev/shm/josephrb-cov2d-95; DD=$W/deploy
CONDA=/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda
ROOTENV=$HOME/.conda/envs/root_6_28
RUN="nice -n 19 taskset -c 8-11"
verdict() { echo "CONTROL-95 $1"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit "$2"; }
cleanup() { echo "removal: host=$(hostname) $(date -u +%FT%TZ) $(du -sh "$DD" 2>/dev/null | cut -f1) $DD"; rm -rf "$DD"; echo "rc=$?"; ls -d "$DD" 2>&1; }
stop() { echo "STOP $*"; cleanup; verdict INVALID 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" "$W/tmp" || exit 2
exec >> "$W/connect-95.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
blobs() {
  (cd "$DD" && git ls-tree HEAD 2d-unfolding/re2/re2_driver.py 2d-unfolding/cov2d/cov2d.py 2d-unfolding/cov2d/cov2d_receipt.py \
    2d-unfolding/cov2d/cov2d_writer.py nd-unfolding/fd_1b_null.py 2d-unfolding/re2/partc/re2c_rollup.py \
    2d-unfolding/pv2d/cmodel/build_cmodel.py 2d-unfolding/cov2d/cov2d_blocks.py) > "$W/blobs.$1"
  cat "$W/blobs.$1"
  for b in 97f26a1d03be8cf14cdb6e0ce05e794f66f9b571 7dafdd3ff827378554931bd1b3d1f19aeeabe11d \
           d5718bf44c2084c20c30a8b8614e9c40e6fbeee3 bb3892e5447d37ee524c720c5ab623baa7184f30 \
           1810161d53c6b849d0dce7fb506d88d551d89900 e41940cb3b4af8f273f34723fb4389d4dac86e0a \
           7a987e25924895803bea756f3e63e3b8b21cd25c 23495e896824a0eaab59584b67a430044cc258d7; do
    grep -q " $b	" "$W/blobs.$1" || stop "blob $b missing at M ($1)"
  done
  echo "blobs ($1): 8 of 8"
}
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "porcelain_before_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
blobs before
(
  eval "$("$CONDA" shell.bash hook)" && conda activate "$ROOTENV" || exit 3
  python -c "import sys, numpy, ROOT; print(sys.version.split()[0], 'numpy', numpy.__version__, 'ROOT', ROOT.gROOT.GetVersion())" || exit 4
  cd "$DD/2d-unfolding/cov2d" && $RUN python -B cov2d_blocks.py control95 --out "$W/control95.json"
) > "$W/control95.log" 2>&1; rc=$?
cat "$W/control95.log"
n=$(git -C "$DD" status --porcelain | wc -l); echo "porcelain_after_lines=$n head=$(git -C "$DD" rev-parse HEAD)"
git -C "$DD" status --porcelain | head -20
[ "$n" = "0" ] || stop "porcelain after: $n lines"
blobs after
if [ "$rc" = 0 ] && grep -q "^COV2D-9.5 PASS" "$W/control95.log"; then V=PASS; X=0
elif [ "$rc" = 3 ] && grep -q "^COV2D-9.5 STOP" "$W/control95.log"; then V=FAIL; X=3
else V=INVALID; X=2; fi
sha256sum "$W/control95.json" 2>&1
cleanup
verdict "$V" "$X"
