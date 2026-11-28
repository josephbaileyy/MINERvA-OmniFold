#!/bin/bash
# geanttw P2-P3 D1: run dump_header.py once on a Perlmutter login node. From the Mac:
#   bash run_d1.sh SCRIPT_SHA256 > d1.out 2>&1
# It refuses unless dump_header.py beside it has SCRIPT_SHA256 (the director's pin) and the NERSC cert is valid now.
# Then it opens one fresh ssh (never an existing master, never a prompt), checks that the conda ROOT env's python3
# imports uproot, and streams the script to it with -I. The script reads the production dump's header only, with
# O_NOATIME, and writes nothing.
set -o pipefail
WANT="${1:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
SSH="ssh -o ControlMaster=no -o ControlPath=none -o BatchMode=yes -o ProxyJump=none -o ProxyCommand=none perlmutter.nersc.gov"
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
[[ "${WANT}" =~ ^[0-9a-f]{64}$ ]] || { echo "REFUSED: give the pinned sha256 of dump_header.py"; exit 9; }
GOT=$(shasum -a 256 "${HERE}/dump_header.py" | cut -d' ' -f1)
[[ "${GOT}" == "${WANT}" ]] || { echo "REFUSED: dump_header.py is ${GOT}, not ${WANT}"; exit 9; }
VALID=$(ssh-keygen -L -f "${HOME}/.ssh/nersc-cert.pub" | grep -i 'valid:') || { echo "REFUSED: no cert"; exit 9; }
EXP=$(printf '%s' "${VALID}" | sed -n 's/.* to \([0-9T:-]*\).*/\1/p')   # local time, as ssh-keygen prints it
NOW=$(date +%Y-%m-%dT%H:%M:%S)
[[ -n "${EXP}" && "${NOW}" < "${EXP}" ]] || { echo "REFUSED: cert '${VALID}' is not valid at ${NOW}"; exit 9; }
echo "cert:${VALID} (now ${NOW} local)"
echo "script: ${GOT} dump_header.py; mac_utc=$(date -u +%FT%TZ)"
${SSH} "echo host=\$(hostname -s) utc=\$(date -u +%FT%TZ); ${PY} -I -c 'import sys, uproot; print(\"python\", sys.version.split()[0], \"uproot\", uproot.__version__)' && ${PY} -I -" \
  < "${HERE}/dump_header.py"; rc=$?
echo "== d1 rc=${rc} $(date -u +%FT%TZ)"
exit ${rc}
