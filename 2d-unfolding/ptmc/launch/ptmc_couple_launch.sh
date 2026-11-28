#!/bin/bash
# PTMC: the read-only C-COUPLE measurement on the real CV omnifile (ptmc_couple_check.py), at 0 node-h, on a login node,
# in oofvc_cleanup_launch.sh's form. One ssh session: it enters at saul.nersc.gov and hops to NODE. stdin carries
# ptmc_couple_check.py, staged in a private mktemp file in /dev/shm whose sha256 must equal the approved one, or NODE
# deletes it and exits 8 before anything runs. The CV copy read is r3's staged copy (this lane's own file, which Joseph
# kept), and its sha256 must be 43f8cc16 before the check opens it. Nothing is written on /pscratch.
# The root_6_28 env is activated (conda's shell hook) before python, as every working root_6_28 run does: without it,
# ROOT's interpreter finds no standard-library include paths and segfaults at import (run 1, 2026-11-27T17:29Z).
# Usage: bash ptmc_couple_launch.sh <new empty session dir> <login node>
F=${1:?session dir}; NODE=${2:-}
HERE=$(cd "$(dirname "$0")" && pwd)
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
S="$HERE/ptmc_couple_check.py"; SHA=13901cbe0bddbe27fce515c9b37ad01fec8c48e3440485f62754c56f9fe32262
CV=/pscratch/sd/j/josephrb/oofvc-20261126-r3/stage/runEventLoopOmniFold_MEFHC.root
CV_SHA=43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
case "$SHA" in *__*) echo "STOP: the approved sha256 is not filled in"; exit 9;; esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
h=$(shasum -a 256 "$S" | cut -d' ' -f1) && [ "$h" = "$SHA" ] || { echo "STOP: the local check is not the approved one"; exit 8; }
R="umask 077; set -o pipefail; [ \"\$(id -un)\" = josephrb ] || exit 7; f=\$(mktemp /dev/shm/ptmc-couple.XXXXXXXX) || exit 8; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: staged copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) \$(date -u +%FT%TZ) staged sha256 \$h\"; [ -f $CV ] && [ ! -L $CV ] || { rm -f -- \"\$f\"; echo 'STOP: the CV copy is absent or a symlink'; exit 7; }; c=\$(sha256sum < $CV | cut -d' ' -f1) || { rm -f -- \"\$f\"; echo 'STOP: sha256 of the CV copy failed'; exit 7; }; if [ \"\$c\" != $CV_SHA ]; then rm -f -- \"\$f\"; echo \"STOP: the CV copy is \$c\"; exit 7; fi; echo \"CV copy sha256 \$c\"; eval \"\$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)\" && conda activate \"\$HOME/.conda/envs/root_6_28\" || { rm -f -- \"\$f\"; echo 'STOP: conda activate failed'; exit 7; }; cd /dev/shm && OMP_NUM_THREADS=1 nice -n 19 $PY -B \"\$f\" $CV; r=\$?; rm -f -- \"\$f\"; echo \"check rc=\$r \$(date -u +%FT%TZ)\"; exit \$r"
ssh "${SSH[@]}" -o ServerAliveInterval=15 -o ServerAliveCountMax=40 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
