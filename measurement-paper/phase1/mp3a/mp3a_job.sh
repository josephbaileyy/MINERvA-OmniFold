#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q shared
#SBATCH -c 8
#SBATCH -t 00:45:00
#SBATCH -J mp3a
#SBATCH -o /pscratch/sd/j/josephrb/measurement-paper/phase1/mp3a/logs/mp3a-%j.out
# MP3-A (PLAN.md §4.2-4.3, frozen by BINDING-PHASE1-20261019): step 1 rebuilds the frozen GENIE CV/MEC 5D
# predictions split by target code (control: bitwise vs the frozen products); step 2 maps CH vs C-only over the
# 109 J cells through s5p_joint's own evaluation path. Writes only under $D. No set -u (it aborts the activation).
# sbatch runs a copy of this file, so $D is absolute, never derived from BASH_SOURCE.
set -o pipefail
D=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3a
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
unset PYTHONPATH
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TMPDIR=$D/tmp
mkdir -p "$D/tmp" "$D/out/build" "$D/out/eval" "$D/run"
cd "$D/run" || exit 2
echo "host $(hostname) start $(date -u +%FT%TZ) python $(command -v python3)"
python3 -c 'import sys, numpy, scipy; print(sys.version.split()[0], numpy.__version__, scipy.__version__)'
python3 "$D/code/mp3a_build.py" "$D/out/build"
rc1=$?
echo "BUILD rc=$rc1 $(date -u +%FT%TZ)"
[ $rc1 = 0 ] || { echo "STOP: build control failed (rc=$rc1); no evaluation"; exit $rc1; }
python3 "$D/code/mp3a_eval.py" --design "$D/inputs/design.json" --s5c-contract "$D/inputs/s5c_contract.json" \
  --v /pscratch/sd/j/josephrb/s5p-20260926/stage3/V/V-s3v.npz --frozen-eval "$D/inputs/joint-evaluate.json" \
  --build-dir "$D/out/build" --out "$D/out/eval"
rc2=$?
echo "EVAL rc=$rc2 end $(date -u +%FT%TZ)"
exit $rc2
