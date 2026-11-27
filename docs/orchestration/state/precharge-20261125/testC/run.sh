#!/bin/bash
# One test C task: "reco <playlist>" reruns the MC reco table with true E_nu,
# "truth <playlist>" writes the Truth-tree denominators. Writes only in the cwd.
set -eo pipefail
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null
export OPENBLAS_NUM_THREADS=1
manifests=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/manifests
mode=$1
pl=$2
sha256sum -c staged.sha256 built.sha256
echo "[testC] $mode $pl node=$(hostname) job=${SLURM_JOB_ID:-none} start=$(date -u +%FT%TZ)"
case $mode in
    reco)  ./measure "$pl" MC "$manifests/${pl}_MC.txt" "${pl}_MC.tmp" > "${pl}_MC.log" 2>&1
           gzip -n -c "${pl}_MC.tmp" > "${pl}_MC.csv.gz" ;;
    truth) ./truth "$pl" "$manifests/${pl}_MC.txt" axes.txt "${pl}_truth.tmp" > "${pl}_truth.log" 2>&1
           gzip -n -c "${pl}_truth.tmp" > "${pl}_truth.csv.gz" ;;
    *)     exit 2 ;;
esac
rm "${pl}_${mode/reco/MC}.tmp"
touch "${mode}_${pl}.done"
echo "[testC] $mode $pl done=$(date -u +%FT%TZ)"
