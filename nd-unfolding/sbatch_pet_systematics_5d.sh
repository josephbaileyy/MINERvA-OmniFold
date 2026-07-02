#!/bin/bash
#SBATCH --job-name=pet_syst5d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=80G --time=06:00:00
#SBATCH --output=pet_syst5d_%j.out --error=pet_syst5d_%j.err
# PET 5D VERTICAL covariance (C_syst block-sum over 12 knob + 100 flux bands on the
# clean bank_uthrow, + C_stat 100 Poisson bootstraps + C_ML 2-training spread),
# 5D (pt,pz,Eavail,q3,W) via the row-aligned W splice. Writes
# products/pet/pet_5d_covariance_combined.root. Mirrors the 4D rebank recipe.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p products/pet

# alignment gate (cheap): bank_uthrow must be bit-identical in row order to of_inputs_pc
python3 - <<'EOF'
import numpy as np
b = np.load("bank_uthrow/cv.npz")["w_truth"]
p = np.load("of_inputs_pc.npz")["w_truth"]
assert b.shape == p.shape and np.array_equal(b.astype(np.float64), p.astype(np.float64)), \
    "bank/pc w_truth not bit-identical"
print(f"[gate] bank/pc alignment OK: {b.size} rows")
EOF

python3 pet_systematics_5d.py \
  --bank bank_uthrow \
  --out-root products/pet/pet_5d_covariance_combined.root
