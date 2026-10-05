#!/bin/bash
# Exact k-NN boundary ambiguity on the production cloud, all three inventories.
# CPU only; reads the inventory read-only and writes one JSON.
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=01:30:00
#SBATCH --job-name=pet-knn-census
set -euo pipefail
checkout=$1
output=$2
expected_commit=$3
inventory=$4
cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
mkdir -p "$output"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/terminal.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
module load python
python3 nd-unfolding/pet/configuration_comparison/census_knn_ties.py \
  --inventory "$inventory" --k 3,10 \
  --output "$output/knn-tie-census.json" > "$output/census.log" 2>&1
[[ -s "$output/knn-tie-census.json" ]]
echo COMPLETE > "$output/terminal.txt"
