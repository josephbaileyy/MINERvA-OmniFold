#!/bin/bash
#SBATCH --job-name=w2a_evloop
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# W2a event-loop runs (publication packet W2; Joseph 2026-10-06 item 4). One variant per job:
#   sbatch --output=<NS>/logs/%x_%j.out --job-name=w2a_<variant> sbatch_w2a_evloop.sh \
#          <NS> <variant> <binary> <data manifest> <mc manifest>
# variant: base_cv | mod_cv | mod_rr0 | mod_rr1 | mod_rrzero
#   base_cv    base binary, no W2 env           (the reference)
#   mod_cv     mod binary, no W2 env            (must equal base_cv: the no-op proof)
#   mod_rr0/1  mod binary, delta 0.04, active RecoilResponse:0 (x0.96) / :1 (x1.04)
#   mod_rrzero mod binary, delta 0, active RecoilResponse:0 (identity scale through the lateral path)
# No point-cloud branches (not needed by the scalar chain). All paths are passed explicitly: sbatch
# runs a copy of this file, so it never locates itself.
set -o pipefail   # NOT set -u: setup_MAT.sh / conda references unset vars under nounset
NS="${1:?ns}"; VARIANT="${2:?variant}"; BIN="${3:?binary}"; DATA="${4:?data manifest}"; MC="${5:?mc manifest}"
CANON=/pscratch/sd/j/josephrb/MINERvA-OmniFold
OUT="${NS}/evloop/${VARIANT}.root"
[[ -e "${OUT}" ]] && { echo "[w2a] ${OUT} exists; refusing to overwrite"; exit 3; }
source "${CANON}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
unset MNV101_DUMP_UNIVERSES MNV101_DUMP_POINTCLOUD MNV101_FULL_PHASE_SPACE MNV101_SKIP_SYST MNV101_TRUTH_ONLY \
      MNV101_DISABLE_TRUTH_MISSES MNV101_DUMP_COMPONENTS MNV101_ACTIVE_UNIVERSE MNV101_RECOIL_RESPONSE_DELTA
case "${VARIANT}" in
  base_cv|mod_cv) ;;
  mod_rr0)    export MNV101_RECOIL_RESPONSE_DELTA=0.04 MNV101_ACTIVE_UNIVERSE=RecoilResponse:0 ;;
  mod_rr1)    export MNV101_RECOIL_RESPONSE_DELTA=0.04 MNV101_ACTIVE_UNIVERSE=RecoilResponse:1 ;;
  mod_rrzero) export MNV101_RECOIL_RESPONSE_DELTA=0    MNV101_ACTIVE_UNIVERSE=RecoilResponse:0 ;;
  *) echo "[w2a] unknown variant ${VARIANT}"; exit 2 ;;
esac
WORK="${NS}/work/${VARIANT}_${SLURM_JOB_ID}"
mkdir -p "${WORK}" "${NS}/evloop" && cd "${WORK}" || exit 4
echo "[w2a] ${VARIANT} job=${SLURM_JOB_ID} host=$(hostname) bin=${BIN} md5=$(md5sum "${BIN}" | cut -d' ' -f1)"
echo "[w2a] data=${DATA} ($(wc -l < "${DATA}") files) mc=${MC} ($(wc -l < "${MC}") files)"
echo "[w2a] env: ACTIVE=${MNV101_ACTIVE_UNIVERSE:-unset} DELTA=${MNV101_RECOIL_RESPONSE_DELTA:-unset}"
t0=$(date +%s)
"${BIN}" "${DATA}" "${MC}"; rc=$?
echo "[w2a] rc=${rc} elapsed=$(( $(date +%s) - t0 ))s"
[[ ${rc} -eq 0 && -s runEventLoopOmniFold.root ]] || exit 5
mv runEventLoopOmniFold.root "${OUT}.partial" && mv "${OUT}.partial" "${OUT}"
echo "[w2a] wrote ${OUT} ($(stat -c '%s' "${OUT}") bytes)"
