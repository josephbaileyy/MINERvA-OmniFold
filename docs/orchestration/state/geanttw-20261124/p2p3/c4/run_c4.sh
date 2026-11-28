#!/bin/bash
# geanttw P2-P3: ONE read-only connect with two independent parts (the director's terms of 2026-11-27). From the Mac:
#   bash run_c4.sh C4_SHA256 GREP_SHA256 > c4.out 2>&1
# It refuses unless c4_header.py and nue_grep.sh beside it have the pinned sha256s and the NERSC cert is valid now.
# Then it opens one fresh ssh (never an existing master, never a prompt) and runs:
#   part 1: c4_header.py under omnifold_py310's python3 -I (cov2d's C4 header reads), then "== part1 rc=N"
#   part 2: nue_grep.sh over geanttw's own B/src trees, then "== part2 rc=N"
# Each part's rc is printed on its own line, so a STOP in one does not hide the other. Nothing is written remotely.
set -o pipefail
W1="${1:-}"; W2="${2:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
SSH="ssh -o ControlMaster=no -o ControlPath=none -o BatchMode=yes -o ProxyJump=none -o ProxyCommand=none perlmutter.nersc.gov"
PY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python3
for pair in "c4_header.py:${W1}" "nue_grep.sh:${W2}"; do
  f="${pair%%:*}"; want="${pair#*:}"
  [[ "${want}" =~ ^[0-9a-f]{64}$ ]] || { echo "REFUSED: give the pinned sha256 of ${f}"; exit 9; }
  got=$(shasum -a 256 "${HERE}/${f}" | cut -d' ' -f1)
  [[ "${got}" == "${want}" ]] || { echo "REFUSED: ${f} is ${got}, not ${want}"; exit 9; }
  echo "script: ${got} ${f}"
done
VALID=$(ssh-keygen -L -f "${HOME}/.ssh/nersc-cert.pub" | grep -i 'valid:') || { echo "REFUSED: no cert"; exit 9; }
EXP=$(printf '%s' "${VALID}" | sed -n 's/.* to \([0-9T:-]*\).*/\1/p')   # local time, as ssh-keygen prints it
NOW=$(date +%Y-%m-%dT%H:%M:%S)
[[ -n "${EXP}" && "${NOW}" < "${EXP}" ]] || { echo "REFUSED: cert '${VALID}' is not valid at ${NOW}"; exit 9; }
echo "cert:${VALID} (now ${NOW} local); mac_utc=$(date -u +%FT%TZ)"
{
  echo 'echo "host=$(hostname -s) utc=$(date -u +%FT%TZ)"'
  echo "${PY} -I -c 'import sys, uproot; print(\"python\", sys.version.split()[0], \"uproot\", uproot.__version__)' && ${PY} -I - <<'C4PYEOF'"
  cat "${HERE}/c4_header.py"
  echo "C4PYEOF"
  echo 'echo "== part1 rc=$? $(date -u +%FT%TZ)"'
  echo "bash -s <<'GREPEOF'"
  cat "${HERE}/nue_grep.sh"
  echo "GREPEOF"
  echo 'echo "== part2 rc=$? $(date -u +%FT%TZ)"'
} | ${SSH} bash -s; rc=$?
echo "== c4 connect rc=${rc} $(date -u +%FT%TZ)"
exit ${rc}
