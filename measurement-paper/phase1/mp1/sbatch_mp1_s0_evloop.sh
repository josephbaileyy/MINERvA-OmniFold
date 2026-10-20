#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=01:55:00
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# MP1-A S0 event loop, full playlist 1A, one variant per job (mirrors publication/w2/sbatch_w2b_evloop.sh).
#   sbatch --job-name=mp1s0_<variant> --output=<NS>/logs/%x_%j.out sbatch_mp1_s0_evloop.sh \
#          <NS> <variant> <binary> <expected md5> <q0 convention> <fuzz convention> <F table>
# variant: base_cv          base binary, no species environment (the G1 reference; the last three args "-")
#          zero             mod binary, active SpeciesResponse_zero:0 (k = 0, the G1 control)
#          <s>_m1 | <s>_p1  mod binary, active SpeciesResponse_<s>:0 (-1 sigma) | :1 (+1 sigma),
#                           s in {proton, meson, em, other, xtalk}
# q0 convention: fprop | fractional | legacy; fuzz convention: prorata | none | all (BINDING-PHASE1-ADDENDUM-2
# R1-R2); F table: the playlist's tabulated F (s0_g0_ftable.py) for fprop, "-" otherwise.
# Output: <NS>/evloop/<variant>.root for base_cv and zero, <NS>/evloop/<variant>_<q0>_<fuzz>.root otherwise.
# SPECIES_ENV_CHECK_ONLY=1 runs only the argument and environment guards and exits.
# Outputs only under /pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/. sbatch runs a copy of this file,
# so every path is an explicit argument and the script never locates itself.
set -o pipefail   # NOT set -u: setup_MAT.sh / conda references unset vars under nounset
NS="${1:?ns}"; VARIANT="${2:?variant}"; BIN="${3:?binary}"; EXPECT_MD5="${4:?expected md5}"
Q0C="${5:?q0 convention or -}"; FZC="${6:?fuzz convention or -}"; FTAB="${7:?F table or -}"
ROOT_NS=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/
case "${NS}" in "${ROOT_NS}"?*) ;; *) echo "[mp1s0] REFUSE: namespace must be under ${ROOT_NS}" >&2; exit 2 ;; esac

ACTIVE=""
case "${VARIANT}" in
  base_cv) [[ "${Q0C}" == "-" && "${FZC}" == "-" && "${FTAB}" == "-" ]] || { echo "[mp1s0] REFUSE: base_cv takes '-' '-' '-'" >&2; exit 2; } ;;
  zero) ACTIVE=SpeciesResponse_zero:0 ;;
  proton_m1|meson_m1|em_m1|other_m1|xtalk_m1) ACTIVE="SpeciesResponse_${VARIANT%_m1}:0" ;;
  proton_p1|meson_p1|em_p1|other_p1|xtalk_p1) ACTIVE="SpeciesResponse_${VARIANT%_p1}:1" ;;
  *) echo "[mp1s0] unknown variant ${VARIANT}" >&2; exit 2 ;;
esac
if [[ -n "${ACTIVE}" ]]; then
  case "${Q0C}" in fprop|fractional|legacy) ;; *) echo "[mp1s0] REFUSE: q0 convention '${Q0C}'" >&2; exit 2 ;; esac
  case "${FZC}" in prorata|none|all) ;; *) echo "[mp1s0] REFUSE: fuzz convention '${FZC}'" >&2; exit 2 ;; esac
  if [[ "${Q0C}" == fprop ]]; then
    [[ "${FTAB}" != "-" ]] || { echo "[mp1s0] REFUSE: fprop needs an F table" >&2; exit 2; }
  else
    [[ "${FTAB}" == "-" ]] || { echo "[mp1s0] REFUSE: an F table is only for fprop" >&2; exit 2; }
  fi
fi
# W2 review F5: the shadow-universe and point-cloud dumps read unshifted getters (the binary also refuses).
if [[ -n "${MNV101_DUMP_UNIVERSES+x}" || -n "${MNV101_DUMP_POINTCLOUD+x}" ]]; then
  echo "[mp1s0] REFUSE: MNV101_DUMP_UNIVERSES or MNV101_DUMP_POINTCLOUD is set in the submission environment" >&2
  exit 6
fi
[[ "${SPECIES_ENV_CHECK_ONLY:-0}" == "1" ]] && { echo "[mp1s0] env check passed (${VARIANT} ${ACTIVE:-cv} ${Q0C} ${FZC} ${FTAB})"; exit 0; }
[[ "${FTAB}" == "-" || -s "${FTAB}" ]] || { echo "[mp1s0] REFUSE: F table ${FTAB} missing" >&2; exit 7; }

[[ "$(md5sum "${BIN}" | cut -d' ' -f1)" == "${EXPECT_MD5}" ]] || { echo "[mp1s0] REFUSE: ${BIN} md5 is not ${EXPECT_MD5}" >&2; exit 7; }
CANON=/pscratch/sd/j/josephrb/MINERvA-OmniFold
DATA="${CANON}/2d-unfolding/playlist_manifests/1A_Data.txt"
MC="${CANON}/2d-unfolding/playlist_manifests/1A_MC.txt"
for m in "${DATA}:b74d89654a4fc0400e100c3f6d30d6b87082e3fba0444b7f2dcfda8682488495" \
         "${MC}:4100dca453de1beef0213a0feac1fe4faa77d769f2dd5f36f4e11c6cea4894f8"; do
  [[ "$(sha256sum "${m%%:*}" | cut -d' ' -f1)" == "${m##*:}" ]] || { echo "[mp1s0] REFUSE: manifest ${m%%:*} changed" >&2; exit 7; }
done
case "${VARIANT}" in base_cv|zero) OUT="${NS}/evloop/${VARIANT}.root" ;; *) OUT="${NS}/evloop/${VARIANT}_${Q0C}_${FZC}.root" ;; esac
[[ -e "${OUT}" ]] && { echo "[mp1s0] ${OUT} exists; refusing to overwrite" >&2; exit 3; }
source "${CANON}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
# The W2 unset list, plus this band's variables.
unset MNV101_DUMP_UNIVERSES MNV101_DUMP_POINTCLOUD MNV101_FULL_PHASE_SPACE MNV101_SKIP_SYST MNV101_TRUTH_ONLY \
      MNV101_DISABLE_TRUTH_MISSES MNV101_DUMP_COMPONENTS MNV101_ACTIVE_UNIVERSE MNV101_RECOIL_RESPONSE_DELTA \
      MNV101_SPECIES_RESPONSE_Q0 MNV101_SPECIES_RESPONSE_FUZZ MNV101_SPECIES_RESPONSE_FTABLE
if [[ -n "${ACTIVE}" ]]; then
  export MNV101_SPECIES_RESPONSE_Q0="${Q0C}" MNV101_SPECIES_RESPONSE_FUZZ="${FZC}" MNV101_ACTIVE_UNIVERSE="${ACTIVE}"
  [[ "${FTAB}" != "-" ]] && export MNV101_SPECIES_RESPONSE_FTABLE="${FTAB}"
fi
WORK="${NS}/work/${VARIANT}_${Q0C}_${FZC}_${SLURM_JOB_ID:-nojob}_$$"   # unique per process: several passes may share one job
mkdir -p "${WORK}" "${NS}/evloop" && cd "${WORK}" || exit 4
echo "[mp1s0] ${VARIANT} job=${SLURM_JOB_ID} host=$(hostname) bin=${BIN} md5=${EXPECT_MD5}"
echo "[mp1s0] env: ACTIVE=${MNV101_ACTIVE_UNIVERSE:-unset} Q0=${MNV101_SPECIES_RESPONSE_Q0:-unset} FUZZ=${MNV101_SPECIES_RESPONSE_FUZZ:-unset} FTABLE=${MNV101_SPECIES_RESPONSE_FTABLE:-unset}"
[[ "${FTAB}" != "-" ]] && echo "[mp1s0] F table sha256 $(sha256sum "${FTAB}" | cut -d' ' -f1)"
echo "[mp1s0] data=${DATA} ($(wc -l < "${DATA}") files) mc=${MC} ($(wc -l < "${MC}") files)"
t0=$(date +%s)
"${BIN}" "${DATA}" "${MC}"; rc=$?
echo "[mp1s0] rc=${rc} elapsed=$(( $(date +%s) - t0 ))s"
[[ ${rc} -eq 0 && -s runEventLoopOmniFold.root ]] || exit 5
mv runEventLoopOmniFold.root "${OUT}.partial" && mv "${OUT}.partial" "${OUT}"
echo "[mp1s0] wrote ${OUT} ($(stat -c '%s' "${OUT}") bytes) sha256 $(sha256sum "${OUT}" | cut -d' ' -f1)"
cd "${NS}" && rm -rf "${WORK}"
