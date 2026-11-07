#!/bin/bash
# RPD-RECO standalone real-class check (the director's go, 2026-11-06): Codex2's
#   MAT_PYTHON nd-unfolding/tests/fd_rpd_reco_mat_check.py --probe <committed non-input copy> --run PROBE_RUN
# at #848's frozen code head d9740563, from a fresh clone, on a login node at 0 node-h. It reads only the committed
# non-input probe (flux-gen2thin-pdg-14-minervame1M_rearrangedUniverses.root, d9704aa4...) and the pinned MAT setup and
# library files (digested by the code); no declared RPD-RECO input and no COV2D input. The COV2D fence is a RECORDED
# line. The MAT environment is entered as fd_rpd_reco_flux_connect.sh @ d9740563 enters it: check-mat-setup first,
# then source the pinned setup_salloc_env.sh, then TMPDIR restored to the run. MAT_PYTHON is the interpreter
# root_tests_login.log measured in that environment (B: root_6_28's python3, Python 3.11.14). Everything is written
# under the literal scratch root /dev/shm/limres-rpd-mnv-20261106 (refused if it exists), printed, then removed by
# its literal path. Launched from a /dev/shm copy of itself ($1), which it deletes at exit.
SELF=$1
S=d9740563f014c1642546edf314559887003b9920
PROBE_REL=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/timing-20261106/flux-gen2thin-pdg-14-minervame1M_rearrangedUniverses.root
PROBE_SHA=d9704aa45c016b044284d9e3cfc8c6d5c07cda0835a445866d5f792c8ac82840
MATENV=/pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
MAT_PYTHON=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
finish() { echo "== rpd-mnv-check rc=$1 $(date -u +%FT%TZ)"; rm -rf -- /dev/shm/limres-rpd-mnv-20261106; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; rm -f -- "$SELF"; exit 9 ;; esac
[ ! -e /dev/shm/limres-rpd-mnv-20261106 ] || { echo "STOP: /dev/shm/limres-rpd-mnv-20261106 exists"; rm -f -- "$SELF"; exit 9; }
mkdir /dev/shm/limres-rpd-mnv-20261106 || { rm -f -- "$SELF"; exit 9; }
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== COV2D fence (RECORDED line; this check reads no COV2D input)"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' | awk -F'|' '$2 ~ /^cov2d-/'; echo "fence squeue rc=${PIPESTATUS[0]}"
echo "== fresh clone at $S"
git clone --quiet --filter=blob:none --no-checkout https://github.com/josephbaileyy/MINERvA-OmniFold.git \
  /dev/shm/limres-rpd-mnv-20261106/repo || { echo "STOP: clone failed"; finish 5; }
git -C /dev/shm/limres-rpd-mnv-20261106/repo -c advice.detachedHead=false checkout --quiet "$S" || { echo "STOP: checkout failed"; finish 5; }
head=$(git -C /dev/shm/limres-rpd-mnv-20261106/repo rev-parse HEAD)
porc=$(git -C /dev/shm/limres-rpd-mnv-20261106/repo status --porcelain | wc -l)
echo "HEAD $head; porcelain lines $porc"
[ "$head" = "$S" ] && [ "$porc" -eq 0 ] || { echo "STOP: the clone is not $S clean"; finish 5; }
got=$(sha256sum "/dev/shm/limres-rpd-mnv-20261106/repo/$PROBE_REL" | cut -d' ' -f1)
echo "probe sha256 $got (pin $PROBE_SHA)"
[ "$got" = "$PROBE_SHA" ] || { echo "STOP: probe digest"; finish 5; }
for f in nd-unfolding/tests/fd_rpd_reco_mat_check.py nd-unfolding/fd_rpd_reco.py nd-unfolding/fd_rpd_inputs.py; do
  echo "blob $(git -C /dev/shm/limres-rpd-mnv-20261106/repo rev-parse "$S:$f") sha256 $(sha256sum "/dev/shm/limres-rpd-mnv-20261106/repo/$f" | cut -d' ' -f1) $f"
done
mkdir -p /dev/shm/limres-rpd-mnv-20261106/run/tmp
(
  export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
  echo "== check-mat-setup (before sourcing)"
  "$MAT_PYTHON" /dev/shm/limres-rpd-mnv-20261106/repo/nd-unfolding/fd_rpd_inputs.py check-mat-setup \
    --r /dev/shm/limres-rpd-mnv-20261106/run; c=$?
  echo "check-mat-setup rc=$c"
  [ "$c" -eq 0 ] || exit 7
  source "$MATENV" > /dev/shm/limres-rpd-mnv-20261106/run/matenv.log 2>&1
  echo "source rc=$?; setup log lines $(wc -l < /dev/shm/limres-rpd-mnv-20261106/run/matenv.log)"
  export TMPDIR=/dev/shm/limres-rpd-mnv-20261106/run/tmp
  echo "env: MAT_PYTHON=$MAT_PYTHON $("$MAT_PYTHON" -V 2>&1); python3 on PATH $(command -v python3); PLOTUTILSROOT=[$PLOTUTILSROOT]; MINERVA_PREFIX=[$MINERVA_PREFIX]; ROOTSYS=[$ROOTSYS]"
  cd /dev/shm/limres-rpd-mnv-20261106/repo || exit 5
  echo "== $MAT_PYTHON nd-unfolding/tests/fd_rpd_reco_mat_check.py --probe $PROBE_REL --run /dev/shm/limres-rpd-mnv-20261106/run/probe"
  nice -n 19 "$MAT_PYTHON" nd-unfolding/tests/fd_rpd_reco_mat_check.py --probe "$PROBE_REL" \
    --run /dev/shm/limres-rpd-mnv-20261106/run/probe
  m=$?
  echo "mat_check rc=$m"
  exit "$m"
)
sub=$?
echo "== subshell rc=$sub"
for f in /dev/shm/limres-rpd-mnv-20261106/run/matenv.log /dev/shm/limres-rpd-mnv-20261106/run/probe/real-mnv-check.json; do
  if [ -f "$f" ]; then echo "== FILE $f sha256 $(sha256sum "$f" | cut -d' ' -f1)"; cat "$f"; echo "== END $f"; else echo "== ABSENT $f"; fi
done
ls -la /dev/shm/limres-rpd-mnv-20261106/run/probe 2>&1
finish "$sub"
