#!/bin/bash
# Refresh pet_vs_gbdt using an interactive CPU allocation for the fixed
# point-cloud event loop + dump, then submit the GPU PET training and comparison
# as dependency-gated sbatch jobs.
#
# Run from the login node:
#   bash nd-unfolding/run_pet_refresh_interactive.sh
#
# The CPU work runs INSIDE the salloc allocation and launches the 12 playlists as
# concurrent srun --overlap steps via run_pc_evloop_interactive.sh. The GPU step
# remains sbatch because it needs a GPU node and usually should outlive the CPU
# allocation.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ACCOUNT="${ACCOUNT:-m3246}"
INTERACTIVE_TIME="${INTERACTIVE_TIME:-04:00:00}"
INTERACTIVE_CPUS="${INTERACTIVE_CPUS:-128}"

cd "${REPO}"

echo "[pet-refresh] CPU interactive phase start $(date -u '+%F %T UTC')"
echo "[pet-refresh] account=${ACCOUNT} time=${INTERACTIVE_TIME} cpus=${INTERACTIVE_CPUS}"

salloc --account="${ACCOUNT}" --qos=interactive --constraint=cpu \
  --nodes=1 --ntasks=1 --cpus-per-task="${INTERACTIVE_CPUS}" \
  --time="${INTERACTIVE_TIME}" \
  bash -lc "
    set -eo pipefail
    REPO='${REPO}'
    source \"\${REPO}/setup_salloc_env.sh\"
    echo '[pet-refresh/cpu] node='\"\$(hostname)\"' job='\"\${SLURM_JOB_ID}\"' start '\"\$(date -u '+%F %T UTC')\"
    cd \"\${REPO}/MINERvA101/opt/build_MINERvA101\"
    cmake --build . --target runEventLoopOmniFold --parallel 8
    cmake --install .
    cd \"\${REPO}\"
    bash nd-unfolding/run_pc_evloop_interactive.sh
    cd \"\${REPO}/nd-unfolding\"
    FORCE_PC_REBUILD=1 bash sbatch_pc_downstream.sh
    echo '[pet-refresh/cpu] done '\"\$(date -u '+%F %T UTC')\"
  "

echo "[pet-refresh] CPU outputs ready; submitting GPU PET train + comparison"
PET_JOB="$(sbatch --parsable --export=ALL,FORCE_PET_REBUILD=1 nd-unfolding/sbatch_pet_train.sh)"
CMP_JOB="$(sbatch --parsable --dependency=afterok:${PET_JOB} nd-unfolding/sbatch_pet_compare.sh)"

cat <<EOF
[pet-refresh] submitted:
  PET train   ${PET_JOB}
  comparison  ${CMP_JOB}

Monitor:
  squeue -j ${PET_JOB},${CMP_JOB}

Final expected output:
  nd-unfolding/pet_vs_gbdt.png
EOF
