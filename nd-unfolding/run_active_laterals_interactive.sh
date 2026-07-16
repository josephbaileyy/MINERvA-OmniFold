#!/bin/bash
# P3S standard active-universe event loops — runs INSIDE a gpu_interactive salloc.
# Sweeps 5 bands x 2 endpoints x 12 playlists = 120 units as concurrent
# `srun --overlap --exact` steps (distributed across the allocation nodes), CPU-only
# on GPU-node host cores. skip-if-exists -> safe to re-run across salloc walls.
# Each unit runs the promoted-universe event loop in its OWN workdir (the binary
# writes runEventLoopOmniFold.root in cwd) with MNV101_ACTIVE_UNIVERSE + pointcloud.
# Set FPS=1 to run the P3F full-phase-space campaign into active_universe_5d/fps/.
# NO set -u (breaks conda activate); HOME fix inline.
set -o pipefail
export HOME=/global/homes/j/josephrb

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ND="${REPO}/nd-unfolding"
BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
BANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)
MAX="${MAX:-20}"                        # concurrent event loops across the allocation
CPT="${CPT:-8}"                         # cores per step
if [[ "${FPS:-0}" == "1" ]]; then MODE=fps; else MODE=standard; fi

echo "[p3s-inside] SLURM_JOB_ID=$SLURM_JOB_ID nodes=$SLURM_JOB_NUM_NODES MAX=$MAX MODE=$MODE start $(date -u +%T)"
echo "[p3s-inside] binary md5=$(md5sum "$BIN" | cut -d' ' -f1)"

for BAND in "${BANDS[@]}"; do
  for EP in 0 1; do
    OUTDIR="${ND}/active_universe_5d/${MODE}/${BAND}_${EP}"
    mkdir -p "${OUTDIR}"
    for PL in "${PLAYLISTS[@]}"; do
      FINAL="${OUTDIR}/runEventLoopOmniFold_5D_${PL}_active_${BAND}_${EP}.root"
      [[ -s "${FINAL}" ]] && continue
      while [ "$(jobs -rp | wc -l)" -ge "$MAX" ]; do sleep 8; done
      W="${ND}/evloop_work_5d_active_${MODE}_${BAND}_${EP}_${PL}"
      D="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
      M="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"
      FPSENV=""; [[ "${MODE}" == "fps" ]] && FPSENV="export MNV101_FULL_PHASE_SPACE=1;"
      srun --overlap --exact --gres=none -n1 -c"${CPT}" bash -lc "
        export HOME=/global/homes/j/josephrb
        source '${REPO}/setup_salloc_env.sh' >/dev/null 2>&1
        export MNV101_ACTIVE_UNIVERSE='${BAND}:${EP}' MNV101_DUMP_POINTCLOUD=1 PYTHONUNBUFFERED=1
        unset MNV101_DUMP_UNIVERSES; ${FPSENV}
        rm -rf '${W}'; mkdir -p '${W}'; cd '${W}'
        if '${BIN}' '${D}' '${M}' > '${OUTDIR}/${PL}.log' 2>&1 && [ -f runEventLoopOmniFold.root ]; then
          mv -f runEventLoopOmniFold.root '${FINAL}' && echo '[done] ${BAND}:${EP} ${PL} '\$(date -u +%T)
          cd '${REPO}' && rm -rf '${W}'
        else
          echo '[FAIL] ${BAND}:${EP} ${PL} rc='\$? '(see ${OUTDIR}/${PL}.log)'
        fi" &
      sleep 1
    done
  done
done
wait
DONE=$(find "${ND}/active_universe_5d/${MODE}" -name 'runEventLoopOmniFold_5D_*_active_*.root' -size +0c 2>/dev/null | wc -l)
echo "[p3s-inside] window done $(date -u +%T); outputs present=${DONE}/120"
