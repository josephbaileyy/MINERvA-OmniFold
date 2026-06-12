#!/bin/bash
#SBATCH --job-name=pet_rebank
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=12:00:00
#SBATCH --output=pet_rebank_%j.out --error=pet_rebank_%j.err

# KNOWN_ISSUES #12 residual: re-run the PET combined covariance on the clean
# regenerated bank and compare against the published budget (C_syst median
# 18.31%). Writes a NEW artifact (does not overwrite the published one).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"

# alignment gate: the rebank must be bit-identical in row order to of_inputs_pc
python3 - <<'EOF'
import numpy as np
b = np.load("bank_uthrow/cv.npz")["w_truth"]
p = np.load("of_inputs_pc.npz")["w_truth"]
assert b.shape == p.shape, f"row-count mismatch bank {b.shape} vs pc {p.shape}"
assert np.array_equal(b.astype(np.float64), p.astype(np.float64)), "w_truth not bit-identical"
print(f"[gate] bank/pc alignment OK: {b.size} rows, w_truth bit-identical")
EOF

python3 pet_systematics.py --bank bank_uthrow \
  --out-root products/pet/pet_4d_covariance_combined_rebank.root
