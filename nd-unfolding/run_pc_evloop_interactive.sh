#!/bin/bash
# Runs INSIDE an salloc: 12 PC event loops as concurrent srun --overlap steps.
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"
echo "[pc-inside] SLURM_JOB_ID=$SLURM_JOB_ID node=$(hostname) start $(date -u +%H:%M:%S)"
for PL in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
  W="${REPO}/nd-unfolding/evloop_work_pcint_${PL}"; mkdir -p "$W"
  D="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
  M="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"
  OUT="${REPO}/nd-unfolding/runEventLoopOmniFold_PC_${PL}.root"
  srun --overlap --exact -n1 -c8 bash -lc \
    "source '${REPO}/setup_salloc_env.sh' >/dev/null 2>&1; export MNV101_DUMP_POINTCLOUD=1 OMP_NUM_THREADS=8; cd '$W' && '$BIN' '$D' '$M' >run.log 2>&1 && mv -f runEventLoopOmniFold.root '$OUT' && echo '[done] $PL $(date -u +%H:%M:%S)'" &
  sleep 1
done
wait
echo "[pc-inside] all finished $(date -u +%H:%M:%S)"
