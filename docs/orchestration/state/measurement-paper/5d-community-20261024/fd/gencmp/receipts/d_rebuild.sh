#!/bin/bash
#SBATCH -q regular
#SBATCH -C cpu
#SBATCH -N 1
#SBATCH -t 01:00:00
#SBATCH -A m3246
#SBATCH -J gencmp-drb
#SBATCH -o /pscratch/sd/j/josephrb/gencmp-20261101/logs/drb-%j.out
#SBATCH -e /pscratch/sd/j/josephrb/gencmp-20261101/logs/drb-%j.err
# GENCMP step D rebuild: nuwro_C12, nuwro_H and nuwro_CHnative in one rebuild directory, so that fd_gencmp.py native
# reads all three from one rebuild.json. The native files are pinned by d/native_pins.sha256, written by the generation
# job; the committed INPUTS.sha256 pins everything else. From the deploy at M with empty porcelain.
B=/pscratch/sd/j/josephrb/gencmp-20261101
M=3410ed0c2a1847ddf590d3869f624bd974f2dce7
cd "$B/deploy" || exit 9
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
[ -s "$B/d/native_pins.sha256" ] || { echo "no native pins"; exit 9; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
export TMPDIR=$B/tmp
date -u +%FT%TZ; hostname
python -B nd-unfolding/fd_gencmp_rebuild.py --out "$B/d/rebuild" --nproc 64 \
  --samples nuwro_C12,nuwro_H,nuwro_CHnative \
  --inputs "$B/deploy/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp/INPUTS.sha256" \
  --inputs "$B/d/native_pins.sha256" \
  --nuwro-chnative-main $(cat "$B/d/native_main.txt") \
  --nuwro-chnative-supp $(cat "$B/d/native_supp.txt")
rc=$?
echo "rc=$rc"; date -u +%FT%TZ
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
exit $rc
