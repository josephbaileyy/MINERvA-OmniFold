#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q shared
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH --no-requeue
#SBATCH -J oofvc_dump
#SBATCH -o /pscratch/sd/j/josephrb/oofvc-20261126/logs/dump-%A_%a.log
# OOFVC step 1A: one MC playlist per task (PLS[i]). The time limit is set per submission by oofvc_dump.sh.
# Writes only $R/dump/<pl>.{root,log,sha256,done}.
set -u
R=/pscratch/sd/j/josephrb/oofvc-20261126
MAN=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/manifests
PLS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
pl=${PLS[$SLURM_ARRAY_TASK_ID]}
cd "$R/dump" || exit 2
echo "[oofvc_dump] $pl node=$(hostname) job=${SLURM_JOB_ID} start=$(date -u +%FT%TZ)"
sha256sum -c built.sha256 || exit 3
grep -q " $MAN/${pl}_MC.txt\$" manifests.sha256 && sha256sum -c <(grep " $MAN/${pl}_MC.txt\$" manifests.sha256) || exit 3
[ ! -e "$pl.root" ] && [ ! -e "$pl.tmp.root" ] || { echo "STOP: $pl output exists"; exit 2; }
( set +u; source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null
  export OPENBLAS_NUM_THREADS=1
  ./oofvc_dump "$pl" "$MAN/${pl}_MC.txt" "$pl.tmp.root" ) > "$pl.log" 2>&1
rc=$?
echo "[oofvc_dump] $pl rc=$rc $(tail -1 "$pl.log")"
[ $rc = 0 ] || exit $rc
mv "$pl.tmp.root" "$pl.root" && sha256sum "$pl.root" > "$pl.sha256" && touch "$pl.done"
echo "[oofvc_dump] $pl done=$(date -u +%FT%TZ)"
