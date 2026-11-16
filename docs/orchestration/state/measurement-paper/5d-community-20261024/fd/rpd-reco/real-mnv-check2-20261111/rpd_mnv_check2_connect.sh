#!/bin/bash
# RPD-RECO real-MnvH1D class check, attempt 2 (Joseph's go via the director, 2026-11-11): #848's
#   MAT_PYTHON nd-unfolding/tests/fd_rpd_reco_mat_check.py --probe <committed non-input probe> --run PROBE_RUN
# at #848's head 9634aadf, from a fresh clone, on one login node at 0 node-h, after cov2d_fence.sh CLEAR. Attempt 1
# (d9740563, 2026-11-06) segfaulted in TFile::Close. 9634aadf runs the check in a ROOT worker subprocess, and it
# publishes PASS only after the worker exits 0, teardown included.
# It reads only the committed non-input probe (d9704aa4) and the pinned MAT setup and library files. It reads no declared
# RPD-RECO input and no COV2D input. The MAT environment is entered as fd_rpd_reco_flux_connect.sh @ 9634aadf enters it:
# check-mat-setup first, then source the pinned setup_salloc_env.sh, then TMPDIR restored to the run.
# Everything is written under the literal scratch root /dev/shm/limres-rpd-mnv2-20261111 (refused if it exists),
# printed, then removed by its literal path. Nothing is written to pscratch or CFS. No set -u.
# Launched from a /dev/shm copy of itself ($1), which it deletes at exit.
SELF=$1
S=9634aadfa3564e0090caecc4dbf415e1318a2f5f
PROBE_REL=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/timing-20261106/flux-gen2thin-pdg-14-minervame1M_rearrangedUniverses.root
PROBE_SHA=d9704aa45c016b044284d9e3cfc8c6d5c07cda0835a445866d5f792c8ac82840
MATENV=/pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
MAT_PYTHON=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
finish() { echo "== rpd-mnv-check2 rc=$1 $(date -u +%FT%TZ)"; rm -rf -- /dev/shm/limres-rpd-mnv2-20261111; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; rm -f -- "$SELF"; exit 9 ;; esac
[ ! -e /dev/shm/limres-rpd-mnv2-20261111 ] || { echo "STOP: /dev/shm/limres-rpd-mnv2-20261111 exists"; rm -f -- "$SELF"; exit 9; }
q=$(squeue --me -h -o '%i|%j|%T') || { echo "STOP: squeue failed"; rm -f -- "$SELF"; exit 9; }
printf '%s\n' "$q" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ {f=1} END {exit !f}' && { echo "STOP: a cov2d/t2a job is queued"; rm -f -- "$SELF"; exit 9; }
mkdir /dev/shm/limres-rpd-mnv2-20261111 || { rm -f -- "$SELF"; exit 9; }
echo "node $(hostname) $(date -u +%FT%TZ); connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== fresh clone at $S"
git clone --quiet --filter=blob:none --no-checkout https://github.com/josephbaileyy/MINERvA-OmniFold.git \
  /dev/shm/limres-rpd-mnv2-20261111/repo || { echo "STOP: clone failed"; finish 5; }
git -C /dev/shm/limres-rpd-mnv2-20261111/repo fetch --quiet origin "$S" || { echo "STOP: fetch of $S failed"; finish 5; }
git -C /dev/shm/limres-rpd-mnv2-20261111/repo -c advice.detachedHead=false checkout --quiet "$S" || { echo "STOP: checkout failed"; finish 5; }
head=$(git -C /dev/shm/limres-rpd-mnv2-20261111/repo rev-parse HEAD)
porc=$(git -C /dev/shm/limres-rpd-mnv2-20261111/repo status --porcelain | wc -l)
echo "HEAD $head; porcelain lines $porc"
[ "$head" = "$S" ] && [ "$porc" -eq 0 ] || { echo "STOP: the clone is not $S clean"; finish 5; }
got=$(sha256sum "/dev/shm/limres-rpd-mnv2-20261111/repo/$PROBE_REL" | cut -d' ' -f1)
echo "probe sha256 $got (pin $PROBE_SHA)"
[ "$got" = "$PROBE_SHA" ] || { echo "STOP: probe digest"; finish 5; }
for pair in "nd-unfolding/tests/fd_rpd_reco_mat_check.py 06360100038f0203b0d994f71c171b12cd955697edf32d1d744c4ce271ceb26d" \
            "nd-unfolding/fd_rpd_reco.py f748c8971919dfc39ecf111920bb01ef2479082e98134f26c83569d60d79627c" \
            "nd-unfolding/fd_rpd_inputs.py 6e4ed0f1d7f55b7bfe2f26752eeb28bb9cbe33325a9d91cc7c06d9494a0b0a70"; do
  set -- $pair
  got=$(sha256sum "/dev/shm/limres-rpd-mnv2-20261111/repo/$1" | cut -d' ' -f1)
  echo "sha256 $got $1"
  [ "$got" = "$2" ] || { echo "STOP: $1 is not at its pinned sha256"; finish 5; }
done
mkdir -p /dev/shm/limres-rpd-mnv2-20261111/run/tmp
(
  export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
  echo "== check-mat-setup (before sourcing)"
  "$MAT_PYTHON" /dev/shm/limres-rpd-mnv2-20261111/repo/nd-unfolding/fd_rpd_inputs.py check-mat-setup \
    --r /dev/shm/limres-rpd-mnv2-20261111/run; c=$?
  echo "check-mat-setup rc=$c"
  [ "$c" -eq 0 ] || exit 7
  source "$MATENV" > /dev/shm/limres-rpd-mnv2-20261111/run/matenv.log 2>&1
  echo "source rc=$?; setup log lines $(wc -l < /dev/shm/limres-rpd-mnv2-20261111/run/matenv.log)"
  export TMPDIR=/dev/shm/limres-rpd-mnv2-20261111/run/tmp
  echo "env: MAT_PYTHON=$MAT_PYTHON $("$MAT_PYTHON" -V 2>&1); PLOTUTILSROOT=[$PLOTUTILSROOT]; MINERVA_PREFIX=[$MINERVA_PREFIX]; ROOTSYS=[$ROOTSYS]"
  cd /dev/shm/limres-rpd-mnv2-20261111/repo || exit 5
  echo "== $MAT_PYTHON nd-unfolding/tests/fd_rpd_reco_mat_check.py --probe $PROBE_REL --run /dev/shm/limres-rpd-mnv2-20261111/run/probe"
  nice -n 19 "$MAT_PYTHON" nd-unfolding/tests/fd_rpd_reco_mat_check.py --probe "$PROBE_REL" \
    --run /dev/shm/limres-rpd-mnv2-20261111/run/probe
  m=$?
  echo "mat_check rc=$m"
  exit "$m"
)
sub=$?
echo "== subshell rc=$sub"
for f in /dev/shm/limres-rpd-mnv2-20261111/run/matenv.log /dev/shm/limres-rpd-mnv2-20261111/run/probe/worker.stdout.txt \
         /dev/shm/limres-rpd-mnv2-20261111/run/probe/worker.stderr.txt /dev/shm/limres-rpd-mnv2-20261111/run/probe/real-mnv-worker.json \
         /dev/shm/limres-rpd-mnv2-20261111/run/probe/real-mnv-check.json; do
  if [ -f "$f" ]; then echo "== FILE $f sha256 $(sha256sum "$f" | cut -d' ' -f1)"; cat "$f"; echo "== END $f"; else echo "== ABSENT $f"; fi
done
ls -la /dev/shm/limres-rpd-mnv2-20261111/run/probe 2>&1
finish "$sub"
