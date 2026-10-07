#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# W2b event loop, one (variant, playlist) per job (publication packet W2; Joseph 2026-10-06 item 4).
# Submitted ONLY by submit_w2b.sh, which sets --time per playlist (C1) and runs the budget check first:
#   sbatch --time=<limit> --job-name=w2b_ev_<variant>_<PL> --output=<NS>/w2b/logs/%x_%j.out \
#          sbatch_w2b_evloop.sh <NS> <variant> <binary> <PL>
# variant: rr0 (RecoilResponse:0, x0.96) | rr1 (RecoilResponse:1, x1.04) | rrzero (delta 0, RecoilResponse:0)
# The binary must be the reviewed mod build (md5 f3e9c97b82456d3fc7e898ea1d0579ee).
# W2B_ENV_CHECK_ONLY=1 runs only the environment guards (C2) and exits; nothing else is touched.
# All paths are explicit arguments: sbatch runs a copy of this file, so it never locates itself.
set -o pipefail   # NOT set -u: setup_MAT.sh / conda references unset vars under nounset

# ---- C2: the RecoilResponse band is unsafe with the shadow-universe or point-cloud dumps (review F5):
# their branches are built from unshifted getters. Refuse if either is requested together with delta.
w2b_env_guard () {   # $1 = the delta this job will set ("" if none)
  local delta="${MNV101_RECOIL_RESPONSE_DELTA:-$1}"
  if [[ -n "${delta}" && ( -n "${MNV101_DUMP_UNIVERSES+x}" || -n "${MNV101_DUMP_POINTCLOUD+x}" ) ]]; then
    echo "[w2b] REFUSE: MNV101_DUMP_UNIVERSES or MNV101_DUMP_POINTCLOUD is set together with MNV101_RECOIL_RESPONSE_DELTA" >&2
    return 6
  fi
  return 0
}

NS="${1:?ns}"; VARIANT="${2:?variant}"; BIN="${3:?binary}"; PL="${4:?playlist}"
case "${VARIANT}" in
  rr0)    W_DELTA=0.04; W_ACTIVE=RecoilResponse:0 ;;
  rr1)    W_DELTA=0.04; W_ACTIVE=RecoilResponse:1 ;;
  rrzero) W_DELTA=0;    W_ACTIVE=RecoilResponse:0 ;;
  *) echo "[w2b] unknown variant ${VARIANT}" >&2; exit 2 ;;
esac
w2b_env_guard "${W_DELTA}" || exit 6           # the inherited (submission) environment
[[ "${W2B_ENV_CHECK_ONLY:-0}" == "1" ]] && { echo "[w2b] env check passed (${VARIANT})"; exit 0; }

EXPECT_MD5=f3e9c97b82456d3fc7e898ea1d0579ee
[[ "$(md5sum "${BIN}" | cut -d' ' -f1)" == "${EXPECT_MD5}" ]] || { echo "[w2b] REFUSE: ${BIN} is not the reviewed binary" >&2; exit 7; }
CANON=/pscratch/sd/j/josephrb/MINERvA-OmniFold
DATA="${CANON}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC="${CANON}/2d-unfolding/playlist_manifests/${PL}_MC.txt"
OUT="${NS}/w2b/evloop/${VARIANT}/runEventLoopOmniFold_5D_${PL}_w2b_${VARIANT}.root"
[[ -e "${OUT}" ]] && { echo "[w2b] ${OUT} exists; refusing to overwrite"; exit 3; }
source "${CANON}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
# The W2a unset list, kept verbatim.
unset MNV101_DUMP_UNIVERSES MNV101_DUMP_POINTCLOUD MNV101_FULL_PHASE_SPACE MNV101_SKIP_SYST MNV101_TRUTH_ONLY \
      MNV101_DISABLE_TRUTH_MISSES MNV101_DUMP_COMPONENTS MNV101_ACTIVE_UNIVERSE MNV101_RECOIL_RESPONSE_DELTA
export MNV101_RECOIL_RESPONSE_DELTA="${W_DELTA}" MNV101_ACTIVE_UNIVERSE="${W_ACTIVE}"
w2b_env_guard "${W_DELTA}" || exit 6           # the environment the binary will actually see
WORK="${NS}/w2b/work/${VARIANT}_${PL}_${SLURM_JOB_ID}"
mkdir -p "${WORK}" "$(dirname "${OUT}")" && cd "${WORK}" || exit 4
echo "[w2b] ${VARIANT} ${PL} job=${SLURM_JOB_ID} host=$(hostname) bin md5=${EXPECT_MD5}"
echo "[w2b] env: ACTIVE=${MNV101_ACTIVE_UNIVERSE} DELTA=${MNV101_RECOIL_RESPONSE_DELTA}"
t0=$(date +%s)
"${BIN}" "${DATA}" "${MC}"; rc=$?
echo "[w2b] rc=${rc} elapsed=$(( $(date +%s) - t0 ))s"
[[ ${rc} -eq 0 && -s runEventLoopOmniFold.root ]] || exit 5
mv runEventLoopOmniFold.root "${OUT}.partial" && mv "${OUT}.partial" "${OUT}"
echo "[w2b] wrote ${OUT} ($(stat -c '%s' "${OUT}") bytes)"
cd "${NS}" && rm -rf "${WORK}"
