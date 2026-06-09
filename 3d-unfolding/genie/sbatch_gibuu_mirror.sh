#!/bin/bash
#SBATCH --job-name=gibuu_mir
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=gibuu_mirror_%A.out
#SBATCH --error=gibuu_mirror_%A.err

# Rebuild the short-path buuinput mirror (cleaned up in the 2026-06-03 sweep) that
# GiBUU's filename handling needs, then submit the 80-run regeneration array. CVMFS
# is mounted on compute nodes, so the rsync runs here. Regenerates FinalEvents.dat
# (which carries Enu col 15 + muon ID 902 -> experimenter's W), enabling GiBUU as the
# 4th generator in the (E_avail,W) band via gibuu_to_xsec_eavailW.py.
set -eo pipefail
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
G=$REPO/3d-unfolding/genie
source "$G/setup_gibuu.sh"
SHORT_INPUT=/pscratch/sd/j/josephrb/gbi

echo "[mirror] GIBUU_INPUT=${GIBUU_INPUT}"
echo "[mirror] rsync -> ${SHORT_INPUT} $(date -u '+%F %T UTC')"
mkdir -p "${SHORT_INPUT}"
rsync -a --delete "${GIBUU_INPUT}/" "${SHORT_INPUT}/"
echo "[mirror] mirror size: $(du -sh ${SHORT_INPUT} | cut -f1); flux present: $(ls ${SHORT_INPUT}/neutrino/MINERvA_MEflux.dat 2>/dev/null || echo NO)"

cd "$G"
echo "[mirror] submitting regeneration array"
JID=$(sbatch --parsable sbatch_gibuu_mefhc.sh)
echo "[mirror] gibuu regen array=${JID}"
echo "${JID}" > .gibuu_regen_job.txt
echo "[mirror] done $(date -u '+%F %T UTC')"
