#!/bin/bash
# Pick each arm's learning rate from the tuning split. Between tuning and pilot.
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --job-name=pet-select-lr
set -eo pipefail
checkout=${CHECKOUT:?}; output=${OUTPUT:?}; commit=${COMMIT:?}; inputs=${INPUTS_NPZ:?}
cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$commit" ]]
module load python
python3 nd-unfolding/pet/configuration_comparison/select_learning_rate.py \
  --campaign "$output" --closure-npz "$inputs" \
  --output "$output/tuning/selected_learning_rate.json"
