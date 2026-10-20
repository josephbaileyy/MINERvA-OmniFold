#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q debug
#SBATCH -N 1
#SBATCH -t 00:30:00
#SBATCH -J mp3cb
#SBATCH -o /pscratch/sd/j/josephrb/measurement-paper/phase1/mp3c/logs/mp3cb-%j.out
# MP3-C option (b): the declared POST-HOC DESCRIPTIVE bias check (DECLARATION-b.json, sha256 checked), then on
# PASS the GiBUU-on-CH replay with the FROZEN r(E) and, beside it, with the alternative reweight. B3 stays FAILED.
# No generation. Writes only under $D/out_b. No set -u. Absolute paths.
set -o pipefail
D=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3c
S5P=/pscratch/sd/j/josephrb/s5p-20260926
DSHA=00efbb25651f2939709e6e704ebf6d4744fafc795a7ff7c507906eec424728e5
[ -e "$D/out_b" ] && { echo "STOP: $D/out_b exists"; exit 2; }
echo "host $(hostname) start $(date -u +%FT%TZ) job ${SLURM_JOB_ID:-none}"
sha256sum "$D"/code/* "$D"/inputs/*
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
unset PYTHONPATH
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TMPDIR=$D/tmp
mkdir -p "$D/run"; cd "$D/run" || exit 2
python3 "$D/code/mp3c_bcheck.py" --declaration "$D/code/DECLARATION-b.json" --declaration-sha256 "$DSHA" \
  --h-glob "$D/prod/task*/FinalEvents.dat" --inputs "$D/inputs" --out "$D/out_b/bcheck"
rb=$?; echo "BCHECK rc=$rb $(date -u +%FT%TZ)"
[ $rb = 0 ] || { echo "no GiBUU-on-CH number (rc=$rb)"; exit $rb; }
EV=(--design "$D/inputs/design.json" --s5c-contract "$D/inputs/s5c_contract.json" --v "$S5P/stage3/V/V-s3v.npz"
    --frozen-eval "$D/inputs/joint-evaluate.json" --build-dir "$D/out_b/bcheck" --null-key GiBUU_2019 --b4-gating yes)
python3 "$D/code/mp3c_eval.py" "${EV[@]}" --fine mp3c_fine_gibuu_frozen.npz --out "$D/out_b/eval_frozen" \
  --variant "B3 (sampling closure) failed on hydrogen; a post-hoc bias check of its premise passed at <= 0.1 sigma_c"
r1=$?; echo "EVAL_frozen rc=$r1 $(date -u +%FT%TZ)"
python3 "$D/code/mp3c_eval.py" "${EV[@]}" --fine mp3c_fine_gibuu_alt.npz --out "$D/out_b/eval_alt" \
  --variant "GiBUU-on-CH under the post-hoc alternative (b) reweight; descriptive, beside the frozen-r(E) replay"
r2=$?; echo "EVAL_alt rc=$r2 end $(date -u +%FT%TZ)"
[ $r1 = 0 ] && [ $r2 = 0 ]
