#!/bin/bash
# Interactive-GPU packed bkg-aware dump-all evloop (2026-07-13): gpu_shared was
# fairshare-stuck, so run the CPU MAT event loop on interactive GPU-node host cores.
# srun --ntasks-per-node=1 -> one instance per node; each picks a round-robin slice
# of the 12 playlists (i%NPROC==PROCID) and runs CONC concurrent EVLOOP_BIN, each in
# its OWN per-playlist workdir (binary writes runEventLoopOmniFold.root in cwd, so
# distinct cwd avoids collision). NON-DESTRUCTIVE _bkgaware output. skip-if-exists.
# HOME/ROOT fix inline; NO set -u (breaks conda activate).
set -o pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
source "$REPO/setup_salloc_env.sh"
export MNV101_DUMP_UNIVERSES=1 PYTHONUNBUFFERED=1
EVLOOP_BIN="$REPO/MINERvA101/opt/bin/runEventLoopOmniFold"
ND="$REPO/nd-unfolding"; mkdir -p "$ND/uq_4d"
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PROCID=${SLURM_PROCID:-0}; NPROC=${SLURM_NTASKS:-1}; CONC=4
echo "[ev-bkg-i proc ${PROCID}/${NPROC}] start $(date -u +%T) on $(hostname)"
for i in "${!PLAYLISTS[@]}"; do
  (( i % NPROC == PROCID )) || continue
  PL=${PLAYLISTS[$i]}
  FINAL="$ND/runEventLoopOmniFold_5D_${PL}_universes_full_bkgaware.root"
  [[ -s "$FINAL" ]] && { echo "[skip] $PL (exists)"; continue; }
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 10; done
  (
    WD="$ND/evloop_work_5d_uni_bkgaware_${PL}"; mkdir -p "$WD"; cd "$WD"
    "$EVLOOP_BIN" "$REPO/2d-unfolding/playlist_manifests/${PL}_Data.txt" \
                  "$REPO/2d-unfolding/playlist_manifests/${PL}_MC.txt" \
      > "$ND/uq_4d/ev5dbkgI_${PL}.log" 2>&1 \
      && mv -f runEventLoopOmniFold.root "$FINAL" && echo "[done] $PL $(date -u +%T)"
  ) &
done
wait
echo "[ev-bkg-i proc ${PROCID}] done $(date -u +%T)"
