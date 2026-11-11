#!/bin/bash
# V-HALF-R's first-build precondition (V-HALF-R-BINDING-1): vhr_wtruth_check.py on the pinned 5D MC npz, on one
# Perlmutter login node in the foreground, at 0 node-h. It runs only after Tier 3 reports, after cov2d_fence.sh CLEAR,
# and on the director's go for this script's sha256 and the launcher's.
# A fresh clone at S (clean, HEAD = S) supplies the checker and its two dependencies, each checked against its sha256
# below. The checker reads MCgen, pass_truth and w_truth of $NPZ through O_NOATIME after its own sha256 check, and
# writes one JSON record under the literal scratch root $W. The record is printed, and $W is removed by its literal
# path. Nothing is written to pscratch or CFS. Threads 1, nice 19. No set -u.
# Launched from a /dev/shm copy of itself, whose path is $1; the copy is deleted at exit.
SELF=$1
S=f3d02e6de91c21fb71b43f4cdbd54ba4bcf86775
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
W=/dev/shm/limres-vhr-wtruth
CHECK=docs/orchestration/state/2d-closeout/valid-region-20261107/v-half-r/code/vhr_wtruth_check.py
CHECK_SHA=514488139bdc60e315eede3a3df269233199b1953a331b6bdc04bcd64afe1ade
S1=nd-unfolding/s5p_stage1_inspect.py
S1_SHA=26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71
H2=nd-unfolding/pv-ladder/readouts/h2_definition.json
H2_SHA=b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89
finish() { echo "== vhr-wtruth rc=$1 $(date -u +%FT%TZ)"; rm -rf -- /dev/shm/limres-vhr-wtruth; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; rm -f -- "$SELF"; exit 9 ;; esac
[ ! -e /dev/shm/limres-vhr-wtruth ] || { echo "STOP: /dev/shm/limres-vhr-wtruth exists"; rm -f -- "$SELF"; exit 9; }
q=$(squeue --me -h -o '%i|%j|%T') || { echo "STOP: squeue failed"; rm -f -- "$SELF"; exit 9; }
printf '%s\n' "$q" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ {f=1} END {exit !f}' && { echo "STOP: a cov2d/t2a job is queued"; rm -f -- "$SELF"; exit 9; }
mkdir /dev/shm/limres-vhr-wtruth || { rm -f -- "$SELF"; exit 9; }
echo "node $(hostname) $(date -u +%FT%TZ); connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== fresh clone at $S"
git clone --quiet --filter=blob:none --no-checkout https://github.com/josephbaileyy/MINERvA-OmniFold.git \
  /dev/shm/limres-vhr-wtruth/repo || { echo "STOP: clone failed"; finish 5; }
git -C /dev/shm/limres-vhr-wtruth/repo -c advice.detachedHead=false checkout --quiet "$S" || { echo "STOP: checkout failed"; finish 5; }
head=$(git -C /dev/shm/limres-vhr-wtruth/repo rev-parse HEAD)
porc=$(git -C /dev/shm/limres-vhr-wtruth/repo status --porcelain | wc -l)
echo "HEAD $head; porcelain lines $porc"
[ "$head" = "$S" ] && [ "$porc" -eq 0 ] || { echo "STOP: the clone is not $S clean"; finish 5; }
for pair in "$CHECK $CHECK_SHA" "$S1 $S1_SHA" "$H2 $H2_SHA"; do
  set -- $pair
  got=$(sha256sum "/dev/shm/limres-vhr-wtruth/repo/$1" | cut -d' ' -f1)
  echo "sha256 $got $1"
  [ "$got" = "$2" ] || { echo "STOP: $1 is not at its pinned sha256 $2"; finish 5; }
done
echo "npz stat before: $(stat -c '%s %Y %X' "$NPZ")"
(
  export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
  echo "python $("$PY310" -V 2>&1); numpy $("$PY310" -I -B -c 'import numpy; print(numpy.__version__)')"
  nice -n 19 "$PY310" -I -B "/dev/shm/limres-vhr-wtruth/repo/$CHECK" --npz "$NPZ" --out /dev/shm/limres-vhr-wtruth/wtruth.json
)
rc=$?
echo "checker rc=$rc"
echo "npz stat after:  $(stat -c '%s %Y %X' "$NPZ")"
if [ -f /dev/shm/limres-vhr-wtruth/wtruth.json ]; then
  echo "== FILE wtruth.json sha256 $(sha256sum /dev/shm/limres-vhr-wtruth/wtruth.json | cut -d' ' -f1)"
  cat /dev/shm/limres-vhr-wtruth/wtruth.json
  echo "== END wtruth.json"
else
  echo "== ABSENT wtruth.json"
fi
finish "$rc"
