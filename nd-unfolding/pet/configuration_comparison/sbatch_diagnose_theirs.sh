#!/bin/bash
# Is his arm non-finite at initialisation, or does it diverge while training?
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=00:30:00
#SBATCH --job-name=pet-diagnose-theirs
set -eo pipefail
checkout=${CHECKOUT:?}; output=${OUTPUT:?}; cache=${CACHE:?}
cd "$checkout"
mkdir -p "$output"
export PYTHONUNBUFFERED=1 TF_FORCE_GPU_ALLOW_GROWTH=true NVIDIA_TF32_OVERRIDE=0
( module load tensorflow/2.15.0
  for lr in 1e-4 1e-5; do
    python nd-unfolding/pet/configuration_comparison/diagnose_theirs_forward.py \
      --cache "$cache" --repo "$checkout" --learning-rate "$lr" \
      --output "$output/diagnose-lr$lr.json" || echo "LR $lr FAILED ($?)"
  done
) > "$output/diagnose.log" 2>&1
echo DONE > "$output/terminal.txt"
