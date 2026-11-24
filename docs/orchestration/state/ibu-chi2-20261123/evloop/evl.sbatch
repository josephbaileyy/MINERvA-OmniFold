#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q shared
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -t 08:00:00
#SBATCH -J ibuchi_evl
#SBATCH --array=0-11
#SBATCH -o /pscratch/sd/j/josephrb/ibuchi-evloop-20261123/logs/evl_%a_%A.out
#SBATCH -e /pscratch/sd/j/josephrb/ibuchi-evloop-20261123/logs/evl_%a_%A.err
# ibuchi event loop: production configuration + MNV101_DUMP_MUONQ only. Writes only under ROOT.
set -eo pipefail
PLS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P); PL=${PLS[$SLURM_ARRAY_TASK_ID]}
ROOT=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123; REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
set +u; source $REPO/setup_salloc_env.sh
export MNV101_DUMP_MUONQ=1
mkdir -p $ROOT/work/$PL $ROOT/out && cd $ROOT/work/$PL
echo "[ibuchi] $PL node=$(hostname) job=$SLURM_JOB_ID start=$(date -u +%FT%TZ) bin=$(sha256sum $ROOT/opt/bin/runEventLoopOmniFold | cut -c1-16)"
env | grep '^MNV101_' | sort
$ROOT/opt/bin/runEventLoopOmniFold $ROOT/manifests/${PL}_Data.txt $ROOT/manifests/${PL}_MC.txt
mv -v runEventLoopOmniFold.root $ROOT/out/runEventLoopOmniFold_${PL}.root
echo "[ibuchi] $PL done=$(date -u +%FT%TZ) sha=$(sha256sum $ROOT/out/runEventLoopOmniFold_${PL}.root | cut -c1-16)"
