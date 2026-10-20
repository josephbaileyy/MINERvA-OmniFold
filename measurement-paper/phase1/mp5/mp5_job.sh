#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q shared
#SBATCH -c 32
#SBATCH -t 01:30:00
#SBATCH -J mp5
#SBATCH -o /pscratch/sd/j/josephrb/measurement-paper/phase1/mp5/logs/mp5-%j.out
# MP-5 (BINDING-PHASE1-ADDENDUM-1 section 3 + the director's MP-5(a) amendment). Three steps, each stopping the job on a
# failed control: (1) mp5_tune.py, the analysis-MC truth content about the beam axis and about the nu axis, controls
# T0-T4; (2) mp5_genie.py, the GENIE CV beam-axis rebuild, control G1 before any rotated build is read; (3) mp5_eval.py,
# the readouts of (a) and (b) through s5p_joint's own functions. Writes only under $D. No set -u (it aborts the
# activation). sbatch runs a copy of this file, so $D is absolute, never derived from BASH_SOURCE.
set -o pipefail
D=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp5
DECL_SHA=3806fc58282f04ed29681bbc8ede148d5f5efb347764619c4b2696ca5a941a99
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
unset PYTHONPATH
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TMPDIR=$D/tmp
mkdir -p "$D/tmp" "$D/out/tune" "$D/out/genie" "$D/out/eval" "$D/run/pool"
cd "$D/run" || exit 2
echo "host $(hostname) start $(date -u +%FT%TZ) python $(command -v python3)"
python3 -c 'import sys, numpy, scipy; print(sys.version.split()[0], numpy.__version__, scipy.__version__)'
read -r got _ < <(sha256sum "$D/code/mp5_declaration.json")
[ "$got" = "$DECL_SHA" ] || { echo "STOP: declaration sha256 $got is not the declared $DECL_SHA"; exit 4; }
python3 "$D/code/mp5_tune.py" "$D/out/tune" "$D/run/pool" 32 "$D/inputs/s5c_contract.json"
rc1=$?
echo "TUNE rc=$rc1 $(date -u +%FT%TZ)"
[ $rc1 = 0 ] || { echo "STOP: a tune control failed (rc=$rc1); nothing else is read"; exit $rc1; }
python3 "$D/code/mp5_genie.py" "$D/out/genie" "$D/run/pool" "$D/code/mp5_declaration.json" "$D/inputs/s5c_contract.json"
rc2=$?
echo "GENIE rc=$rc2 $(date -u +%FT%TZ)"
[ $rc2 = 0 ] || { echo "STOP: the GENIE unrotated control failed (rc=$rc2); no rotated build is read"; exit $rc2; }
python3 "$D/code/mp5_eval.py" --design "$D/inputs/design.json" --s5c-contract "$D/inputs/s5c_contract.json" \
  --v /pscratch/sd/j/josephrb/s5p-20260926/stage3/V/V-s3v.npz --frozen-eval "$D/inputs/joint-evaluate.json" \
  --tune "$D/out/tune/mp5_tune.npz" --genie "$D/out/genie/mp5_genie.npz" --m4w-gen "$D/inputs/m4w_probe_gen.json" \
  --declaration "$D/code/mp5_declaration.json" --out "$D/out/eval"
rc3=$?
echo "EVAL rc=$rc3 end $(date -u +%FT%TZ)"
exit $rc3
