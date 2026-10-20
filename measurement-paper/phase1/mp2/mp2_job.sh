#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q debug
#SBATCH -N 1
#SBATCH -t 00:30:00
#SBATCH -J mp2s01
#SBATCH -o /pscratch/sd/j/josephrb/measurement-paper/phase1/mp2/logs/mp2-%j.out
# MP-2 S1 (stage s1) or S0 (stage s0; requires an admitted S1 receipt) (BINDING-PHASE1-20261019 section 2: both granted). Each step is its own srun step so sacct prices it.
# (1) S1, mp2_s1_dump.py (omnifold_py310): the aligned final-state dump, admitted only on the bitwise MCgen/w_truth/
#     pass_truth check; on any failed control the job stops and nothing downstream runs.
# (2) S0 features, mp2_s0_features.py (omnifold_py310), controls N0/N1.
# (3) S0 fits, mp2_s0_fit.py (root_6_28: LightGBM 4.6; omnifold_py310 has no LightGBM). DESCRIPTIVE.
# Writes only under $D. No set -u before the conda hook. sbatch runs a copy of this file, so $D is absolute.
set -o pipefail
D=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp2
DECL_SHA=6ded06daaf13d537bed706283ed5ebf770a773eb4d2d05fe77faf99c15676244
PYO="$HOME/.conda/envs/omnifold_py310/bin/python"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 TMPDIR=$D/tmp
mkdir -p "$D/tmp" "$D/s1" "$D/s0/features" "$D/s0/fit"
cd "$D/tmp" || exit 2
STAGE=${1:?usage: mp2_job.sh s1|s0}
echo "host $(hostname) start $(date -u +%FT%TZ)"
read -r got _ < <(sha256sum "$D/code/mp2_s0_declaration.json")
[ "$got" = "$DECL_SHA" ] || { echo "STOP: declaration sha256 $got is not the declared $DECL_SHA"; exit 4; }
sha256sum "$D"/code/*
if [ "$STAGE" = s1 ]; then
srun -n 1 -c 128 "$PYO" -I "$D/code/mp2_s1_dump.py" "$D/s1" 64 "$D/tmp/s1"
rc1=$?
echo "S1 rc=$rc1 $(date -u +%FT%TZ)"
[ $rc1 = 0 ] || { echo "STOP: an S1 control failed (rc=$rc1); S0 does not run"; exit $rc1; }
exit 0
fi
[ -f "$D/s1/s1_receipt.json" ] && grep -q '"exit": 0' "$D/s1/s1_receipt.json" || { echo "STOP: S1 not admitted"; exit 5; }
srun -n 1 -c 128 "$PYO" -I "$D/code/mp2_s0_features.py" "$D/s1" "$D/code/mp2_s0_declaration.json" "$D/s0/features"
rc2=$?
echo "S0-features rc=$rc2 $(date -u +%FT%TZ)"
[ $rc2 = 0 ] || { echo "STOP: an S0 feature control failed (rc=$rc2)"; exit $rc2; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
unset PYTHONPATH
srun -n 1 -c 128 python3 "$D/code/mp2_s0_fit.py" "$D/s0/features" "$D/code/mp2_s0_declaration.json" "$D/s0/fit" 64
rc3=$?
echo "S0-fit rc=$rc3 end $(date -u +%FT%TZ)"
exit $rc3
