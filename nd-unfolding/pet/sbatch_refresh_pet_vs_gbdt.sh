#!/bin/bash
# Submit the full fixed point-cloud PET refresh chain:
#   build installed event-loop binary
#   -> per-playlist point-cloud event loops
#   -> merge + dump of_inputs_pc.npz
#   -> GPU PET train, saving pet_weights.npz
#   -> pet_vs_gbdt.png comparison
#
# Run from the repo root or nd-unfolding:
#   bash nd-unfolding/sbatch_refresh_pet_vs_gbdt.sh
#
# This is a submitter, not a compute payload. It uses --parsable job IDs and
# dependency gates so the old stale PET output is not reused.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
cd "${REPO}"

echo "[submit] refresh PET-vs-GBDT with corrected reco clusters"
echo "[submit] start $(date -u '+%F %T UTC')"

BUILD_JOB="$(sbatch --parsable 2d-unfolding/sbatch_build.sh)"
echo "[submit] build: ${BUILD_JOB}"

EVLOOP_JOB="$(sbatch --parsable --dependency=afterok:${BUILD_JOB} nd-unfolding/sbatch_evloop_array_pointcloud.sh)"
echo "[submit] point-cloud event-loop array: ${EVLOOP_JOB}"

DOWN_JOB="$(sbatch --parsable --dependency=afterok:${EVLOOP_JOB} --export=ALL,FORCE_PC_REBUILD=1 nd-unfolding/sbatch_pc_downstream.sh)"
echo "[submit] merge + dump: ${DOWN_JOB}"

PET_JOB="$(sbatch --parsable --dependency=afterok:${DOWN_JOB} --export=ALL,FORCE_PET_REBUILD=1 nd-unfolding/sbatch_pet_train.sh)"
echo "[submit] PET train: ${PET_JOB}"

CMP_JOB="$(sbatch --parsable --dependency=afterok:${PET_JOB} nd-unfolding/sbatch_pet_compare.sh)"
echo "[submit] PET-vs-GBDT compare: ${CMP_JOB}"

cat <<EOF

Submitted dependency chain:
  build       ${BUILD_JOB}
  evloop      ${EVLOOP_JOB}
  merge/dump  ${DOWN_JOB}
  pet train   ${PET_JOB}
  compare     ${CMP_JOB}

Monitor:
  squeue -j ${BUILD_JOB},${EVLOOP_JOB},${DOWN_JOB},${PET_JOB},${CMP_JOB}

Final expected outputs:
  nd-unfolding/of_inputs_pc.npz
  nd-unfolding/pet_weights.npz
  nd-unfolding/pet_vs_gbdt.png
EOF
