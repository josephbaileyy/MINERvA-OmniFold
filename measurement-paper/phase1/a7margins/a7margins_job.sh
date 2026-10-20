#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q debug
#SBATCH -N 1
#SBATCH -c 4
#SBATCH -t 00:30:00
#SBATCH -J a7margins
#SBATCH -o /pscratch/sd/j/josephrb/measurement-paper/phase1/a7margins/logs/a7margins-%j.out
# A7 decision-boundary margins (descriptive receipt; not a re-grade). Writes only under $D.
# No set -u (it aborts the conda activation). sbatch runs a copy of this file: every path is absolute.
set -o pipefail
D=/pscratch/sd/j/josephrb/measurement-paper/phase1/a7margins
S5P=/pscratch/sd/j/josephrb/s5p-20260926
[ -e "$D/out" ] && { echo "STOP: $D/out exists; refusing to overwrite"; exit 2; }
mkdir -p "$D/tmp" "$D/run" || exit 2
echo "host $(hostname) start $(date -u +%FT%TZ) job ${SLURM_JOB_ID:-none}"
cd "$D" || exit 2
for f in code/* inputs/*; do echo "$(git hash-object "$f") $(sha256sum "$f")"; done
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
unset PYTHONPATH
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TMPDIR=$D/tmp
cd "$D/run" || exit 2
echo "python $(command -v python3)"
python3 -c 'import sys, numpy, scipy; print(sys.version.split()[0], numpy.__version__, scipy.__version__)'
python3 "$D/code/a7margins.py" --design "$D/inputs/design.json" --s5c-contract "$D/inputs/s5c_contract.json" \
  --v "$S5P/stage3/V/V-s3v.npz" --frozen-eval "$D/inputs/joint-evaluate.json" --out "$D/out"
rc=$?
echo "A7MARGINS rc=$rc end $(date -u +%FT%TZ)"
exit $rc
