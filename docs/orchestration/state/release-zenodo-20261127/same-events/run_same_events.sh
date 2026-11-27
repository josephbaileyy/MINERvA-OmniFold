#!/bin/bash
# Run same_events.py once on a Perlmutter login node (PLAN.md). From the Mac:
#   bash run_same_events.sh SCRIPT_SHA256 > same_events.out 2>&1
# It refuses unless same_events.py beside it has SCRIPT_SHA256, the director's pinned sha. Then it opens one fresh
# ssh (never an existing master, never a prompt) and streams the script to the conda ROOT env's python3 with -I.
# The script reads its four files with O_NOATIME and writes nothing on the cluster; its report comes back on stdout.
set -o pipefail
WANT="${1:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
SSH="ssh -o ControlMaster=no -o ControlPath=none -o BatchMode=yes -o ProxyJump=none -o ProxyCommand=none perlmutter.nersc.gov"
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
[[ "${WANT}" =~ ^[0-9a-f]{64}$ ]] || { echo "REFUSED: give the pinned sha256 of same_events.py"; exit 9; }
GOT=$(shasum -a 256 "${HERE}/same_events.py" | cut -d' ' -f1)
[[ "${GOT}" == "${WANT}" ]] || { echo "REFUSED: same_events.py is ${GOT}, not ${WANT}"; exit 9; }
echo "script: ${GOT} same_events.py; mac_utc=$(date -u +%FT%TZ)"
${SSH} "echo host=\$(hostname -s) utc=\$(date -u +%FT%TZ); ${PY} -I -c 'import sys, numpy; print(\"python\", sys.version.split()[0], \"numpy\", numpy.__version__)' && ${PY} -I -" \
  < "${HERE}/same_events.py"; rc=$?
echo "== same-events rc=${rc} $(date -u +%FT%TZ)"
exit ${rc}
