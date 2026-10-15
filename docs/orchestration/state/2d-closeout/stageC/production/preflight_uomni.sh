#!/bin/bash
# Stage C production preflight (not a Slurm job): hash the 171 GB universe omnifile once on a NERSC data-transfer node
# and record its size, mtime and inode, which every universe job then checks (sbatch_prod.sh uomni_check).
# Refuses unless the sha256 equals the Stage B digest. Run right before the first universe batch (G2):
#   ssh dtn01.nersc.gov bash /pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015/repo/docs/orchestration/state/2d-closeout/stageC/production/preflight_uomni.sh
set -eo pipefail
NS=/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015
UOMNI=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root
WANT=220c479efa9751116fd396ea32398de5631f8b755e6b16a94ce090975f011418   # Stage B digest (full)
mkdir -p "$NS/preflight"
[ -e "$NS/preflight/uomni.stat" ] && { echo "REFUSE: preflight already recorded"; exit 3; }
before=$(stat -c '%s %Y %i' "$UOMNI")
echo "start $(date -u +%FT%TZ) host $(hostname) stat $before"
got=$(sha256sum "$UOMNI" | cut -c1-64)
after=$(stat -c '%s %Y %i' "$UOMNI")
[ "$before" = "$after" ] || { echo "REFUSE: the file changed while hashing"; exit 4; }
[ "$got" = "$WANT" ] || { echo "REFUSE: sha256 $got != $WANT"; exit 4; }
echo "$got  $UOMNI" > "$NS/preflight/uomni.sha256"
echo "$after" > "$NS/preflight/uomni.stat"
echo "done $(date -u +%FT%TZ) sha256 $got"
