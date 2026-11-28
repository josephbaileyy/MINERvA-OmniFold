#!/bin/bash
# geanttw_connect.sh (Mac side): one geanttw step on a Perlmutter login node (DECLARATION.md §3, §8).
#   bash geanttw_connect.sh STEP M COV2D_ACK NUE_ACK [ARG]    STEP: deploy | build | p0 | check
# COV2D_ACK is the cov2d session's fresh ack for this connect (cov2d_fence.sh's header: sacct cannot see held jobs)
# and NUE_ACK the NuE exception's ack; both are tokens (no spaces), printed here and recorded by the remote step.
# Everything it runs is the committed bytes at M, read with `git show M:<path>` from this repository; nothing
# is taken from the working tree:
#   1. cov2d's fence (cov2d_fence.sh rev 3, at M) runs on the login node; any nonzero rc STOPs (ssh rc read unpiped).
#   2. deploy: geanttw_remote.sh at M is streamed to the login node, which clones the deploy at M.
#      build, p0, check: the deploy's geanttw_remote.sh must have the sha256 of the blob at M; then it runs from the
#      deploy.
# Prints the sha256 and path of each script before running it.
set -o pipefail
STEP="${1:?usage: geanttw_connect.sh STEP M COV2D_ACK NUE_ACK [ARG]}"; M="${2:?M}"
COV2D_ACK="${3:-}"; NUE_ACK="${4:-}"; ARG="${5:-}"
ACK_RE='^[A-Za-z0-9._:@/+=-]{8,200}$'
# A fresh connection every time: never an existing ssh master (one can outlive its certificate, which the director's
# rule of 2026-11-25 forbids using), no jump or proxy client (which would not inherit these options), and never a
# password or MFA prompt. Each call may land on a different login node; every step's state is on /pscratch. Only the
# tests may replace it.
SSH="ssh -o ControlMaster=no -o ControlPath=none -o BatchMode=yes -o ProxyJump=none -o ProxyCommand=none perlmutter.nersc.gov"
HERE="$(cd "$(dirname "$0")" && pwd)"
LOCAL="${GEANTTW_LOCAL_REPO:-$(git -C "${HERE}" rev-parse --show-toplevel)}"
B=/pscratch/sd/j/josephrb/geanttw-20261124
if [[ -n "${GEANTTW_TEST_B:-}" ]]; then   # the tests' only door
  B="${GEANTTW_TEST_B}"; SSH="${GEANTTW_SSH:-${SSH}}"
fi
CODE_REL=docs/orchestration/state/geanttw-20261124/code
FENCE_REL=docs/orchestration/state/2d-closeout/cov2d-fence-20261122/cov2d_fence.sh

bail() { echo "REFUSED: $*"; exit 9; }
stop() { echo "STOP: $*"; echo "== geanttw connect ${STEP} rc=8 $(date -u +%FT%TZ)"; exit 8; }

[[ -z "${GEANTTW_SSH:-}" || -n "${GEANTTW_TEST_B:-}" ]] || bail "GEANTTW_SSH is honoured only by the tests"
case "${STEP}" in deploy|build|p0|check|c2pre|p2pilot|p2run|p3slim|p3unf|p3extract) ;;
  *) bail "step must be deploy, build, p0, check, c2pre, p2pilot, p2run, p3slim, p3unf or p3extract, got '${STEP}'" ;; esac
[[ "${M}" =~ ^[0-9a-f]{40}$ ]] || bail "M '${M}' is not a 40-hex commit"
[[ "${COV2D_ACK}" =~ ${ACK_RE} ]] || bail "a fresh cov2d ack (a token) is required for every connect"
[[ "${NUE_ACK}" =~ ${ACK_RE} ]] || bail "the NuE exception's ack (a token) is required for every connect"
echo "ack: cov2d=${COV2D_ACK} nue=${NUE_ACK} utc=$(date -u +%FT%TZ)"
git -C "${LOCAL}" cat-file -e "${M}^{commit}" 2>/dev/null || bail "${M} is not a commit of ${LOCAL}"
WORK=$(mktemp -d) || stop "mktemp"
trap 'rm -rf "${WORK}"' EXIT
git -C "${LOCAL}" show "${M}:${FENCE_REL}" > "${WORK}/fence.sh" || stop "no ${FENCE_REL} at ${M}"
git -C "${LOCAL}" show "${M}:${CODE_REL}/geanttw_remote.sh" > "${WORK}/remote.sh" || stop "no geanttw_remote.sh at ${M}"
FSHA=$(shasum -a 256 "${WORK}/fence.sh" | cut -d' ' -f1)
RSHA=$(shasum -a 256 "${WORK}/remote.sh" | cut -d' ' -f1)
echo "script: ${FSHA} ${M}:${FENCE_REL}"
echo "script: ${RSHA} ${M}:${CODE_REL}/geanttw_remote.sh"

${SSH} bash -s < "${WORK}/fence.sh"; frc=$?
[[ ${frc} -eq 0 ]] || stop "cov2d_fence.sh exited ${frc}"
echo "fence: clear"

if [[ "${STEP}" == deploy ]]; then
  ${SSH} bash -s -- deploy "${M}" "${COV2D_ACK}" "${NUE_ACK}" < "${WORK}/remote.sh"; rc=$?
else
  got=$(${SSH} sha256sum "${B}/deploy/${CODE_REL}/geanttw_remote.sh" | cut -d' ' -f1)
  [[ "${got}" == "${RSHA}" ]] || stop "the deploy's geanttw_remote.sh is '${got}', not ${RSHA}"
  ${SSH} bash "${B}/deploy/${CODE_REL}/geanttw_remote.sh" "${STEP}" "${M}" "${COV2D_ACK}" "${NUE_ACK}" ${ARG:+"${ARG}"}; rc=$?
fi
[[ ${rc} -eq 0 ]] || stop "remote ${STEP} exited ${rc}"
echo "== geanttw connect ${STEP} rc=0 $(date -u +%FT%TZ)"
