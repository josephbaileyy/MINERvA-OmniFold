#!/bin/bash
# Which primitive is not batch-invariant under XLA, and is the compiled matmul
# actually float32?
#
# The open question from the production validation: the same compiled program,
# with TF32 reportedly off, gives different answers at batch 2048 and batch 256
# on the same rows. k-NN ties and TF32 were both tested and rejected -- but the
# TF32 test compared the path to ITSELF, which cannot tell "the override worked"
# from "the override never reached the compiled path". This run compares it to a
# float64 answer instead.
#
# Measures primitives. Trains nothing, reads no real source, decides nothing.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=00:25:00
#SBATCH --job-name=pet-batch-variance
set -eo pipefail

checkout=${CHECKOUT:?}
output=${OUTPUT:?}
expected_commit=${COMMIT:?}

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
mkdir -p "$output"
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
nvidia-smi --query-gpu=uuid,pci.bus_id,name,memory.total --format=csv > "$output/gpu.csv"

export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8
export TF_FORCE_GPU_ALLOW_GROWTH=true
# `module load python` has no TensorFlow. The GPU work in this directory runs
# under tensorflow/2.15.0, which is what the production validation measured on
# and therefore the only environment whose answer is comparable to it.
module load tensorflow/2.15.0

# Run it BOTH ways. If the override reaches the compiled path the two reports
# differ; if they are identical to the digit, the override is not binding there
# and the precision witness says which arithmetic actually ran.
for override in 0 1; do
  NVIDIA_TF32_OVERRIDE=$override python3 \
    nd-unfolding/pet/configuration_comparison/isolate_batch_variance.py \
    --repo "$checkout" --output "$output/isolate-tf32override-${override}.json"
done

echo DONE > "$output/terminal.txt"
