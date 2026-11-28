#!/bin/bash
# geanttw P0: before the check re-run, move the first check's deploy and its JSON aside, inside B. This is the
# director's ruling of 2026-11-26 on the C0e revision.
#   bash aside_first_check.sh M COV2D_ACK
# It runs from the Mac. It first runs cov2d's fence (cov2d_fence.sh rev 3, read with `git show M:`) on a login node,
# and STOPs on any nonzero rc. Then, in one fresh ssh, it renames only inside B:
#   B/deploy                -> B/deploy-4fe6add5
#   B/run/p0/p0_check.json  -> B/run/p0/p0_check-4fe6add5.json
# Both renames are checked before either runs: a missing source or an existing target refuses, and nothing moves.
# Each runs as `mv -n`, and is then checked (source gone, target there). Nothing is deleted, and nothing else is
# written.
set -o pipefail
M="${1:-}"; ACK="${2:-}"
SSH="ssh -o ControlMaster=no -o ControlPath=none -o BatchMode=yes -o ProxyJump=none -o ProxyCommand=none perlmutter.nersc.gov"
B=/pscratch/sd/j/josephrb/geanttw-20261124
HERE="$(cd "$(dirname "$0")" && pwd)"
LOCAL="$(git -C "${HERE}" rev-parse --show-toplevel)"
if [[ -n "${GEANTTW_TEST_B:-}" ]]; then   # the tests' only door
  B="${GEANTTW_TEST_B}"; SSH="${GEANTTW_SSH:-${SSH}}"; LOCAL="${GEANTTW_LOCAL_REPO:-${LOCAL}}"
fi
FENCE_REL=docs/orchestration/state/2d-closeout/cov2d-fence-20261122/cov2d_fence.sh

bail() { echo "REFUSED: $*"; exit 9; }
stop() { echo "STOP: $*"; echo "== geanttw aside rc=8 $(date -u +%FT%TZ)"; exit 8; }

[[ -z "${GEANTTW_SSH:-}" || -n "${GEANTTW_TEST_B:-}" ]] || bail "GEANTTW_SSH is honoured only by the tests"
[[ "${M}" =~ ^[0-9a-f]{40}$ ]] || bail "M '${M}' is not a 40-hex commit"
[[ "${ACK}" =~ ^[A-Za-z0-9._:@/+=-]{8,200}$ ]] || bail "a fresh cov2d ack (a token) is required"
echo "ack: cov2d=${ACK} utc=$(date -u +%FT%TZ)"
git -C "${LOCAL}" cat-file -e "${M}^{commit}" 2>/dev/null || bail "${M} is not a commit of ${LOCAL}"
WORK=$(mktemp -d) || stop "mktemp"
trap 'rm -rf "${WORK}"' EXIT
git -C "${LOCAL}" show "${M}:${FENCE_REL}" > "${WORK}/fence.sh" || stop "no ${FENCE_REL} at ${M}"
echo "script: $(shasum -a 256 "${WORK}/fence.sh" | cut -d' ' -f1) ${M}:${FENCE_REL}"

${SSH} bash -s < "${WORK}/fence.sh"; frc=$?
[[ ${frc} -eq 0 ]] || stop "cov2d_fence.sh exited ${frc}"
echo "fence: clear"

${SSH} bash -s -- "${B}" <<'EOF'; rc=$?
B="$1"
pairs=("${B}/deploy" "${B}/deploy-4fe6add5" "${B}/run/p0/p0_check.json" "${B}/run/p0/p0_check-4fe6add5.json")
echo "host=$(hostname -s) utc=$(date -u +%FT%TZ)"
for i in 0 2; do
  [[ -e "${pairs[i]}" ]] || { echo "REFUSED: ${pairs[i]} is missing"; exit 9; }
  [[ ! -e "${pairs[i+1]}" ]] || { echo "REFUSED: ${pairs[i+1]} exists"; exit 9; }
done
for i in 0 2; do
  mv -n "${pairs[i]}" "${pairs[i+1]}" || { echo "STOP: mv ${pairs[i]} failed"; exit 8; }
  [[ ! -e "${pairs[i]}" && -e "${pairs[i+1]}" ]] || { echo "STOP: ${pairs[i]} -> ${pairs[i+1]} did not take"; exit 8; }
  echo "moved ${pairs[i]} -> ${pairs[i+1]}"
done
EOF
[[ ${rc} -eq 0 ]] || stop "the remote renames exited ${rc}"
echo "== geanttw aside rc=0 $(date -u +%FT%TZ)"
