#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q debug
#SBATCH -N 1
#SBATCH -t 00:20:00
#SBATCH -J mp3bApost
#SBATCH -o /pscratch/sd/j/josephrb/measurement-paper/phase1/mp3b/runA/logs/mp3bApost-%j.out
# MP3-B run A, post-processing rerun: job 60029039 generated every chunk under both cards and finished (C), but both
# NuWro builds crashed on a print bug in C1 (TypeError) before any gate was evaluated. This job reruns ONLY the
# build and the eval for k1 and k0 on the SAME generated files (gen/, gen_k0/, gen/parity), into out_r2/.
# No generation, no change to any gate or formula (the fix is the one print line). Writes only under $D/out_r2.
set -o pipefail
D=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3b/runA
S5P=/pscratch/sd/j/josephrb/s5p-20260926
SEEDS=$D/code/SEEDS-chunked.txt
[ -e "$D/out_r2" ] && { echo "STOP: $D/out_r2 exists"; exit 2; }
mkdir -p "$D/out_r2" "$D/run"
echo "host $(hostname) start $(date -u +%FT%TZ) job ${SLURM_JOB_ID:-none}"
sha256sum "$D"/code/* "$SEEDS"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
unset PYTHONPATH
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TMPDIR=$D/tmp
cd "$D/run" || exit 2
EV=(--design "$D/inputs/design.json" --s5c-contract "$D/inputs/s5c_contract.json" --v "$S5P/stage3/V/V-s3v.npz"
    --frozen-eval "$D/inputs/joint-evaluate.json")
rcall=0
for c in k1 k0; do
  g=$D/gen; [ $c = k0 ] && g=$D/gen_k0
  python3 "$D/code/mp3b_build.py" --out "$D/out_r2/build_$c" --gen "$g" --seeds "$SEEDS" --card $c --parity-dir "$D/gen/parity"
  rb=$?; echo "BUILD_$c rc=$rb $(date -u +%FT%TZ)"
  re=skipped
  if [ $rb = 0 ]; then
    python3 "$D/code/mp3b_eval.py" "${EV[@]}" --build-dir "$D/out_r2/build_$c" --out "$D/out_r2/eval_$c" \
      --fine mp3b_fine_nuwro.npz --variant "NuWro-on-CH, H card $c (kaskada_on $([ $c = k0 ] && echo 0 || echo 1)), chunked" --b4-gating yes
    re=$?
  fi
  echo "EVAL_$c rc=$re $(date -u +%FT%TZ)"
  [ "$rb" = 0 ] && [ "$re" = 0 ] || rcall=6
done
exit $rcall
