#!/bin/bash
#SBATCH --job-name=boot5dI
#SBATCH --account=m3246_g
#SBATCH --qos=gpu_interactive --constraint=gpu --nodes=1 --gpus=4 --ntasks=1 --cpus-per-task=128 --time=04:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=boot5dI_%j.out --error=boot5dI_%j.err
# ASAP hedge (2026-07-13): the gpu_shared boot5d array (55871150) is stuck pending
# (low fairshare). gpu_interactive has higher priority + dedicated capacity, so it
# dispatches fast. Grab a whole A100 node and run boot5d replicas PACKED: 16
# concurrent x 8 threads = 128 logical cores. DESCENDING seeds (100->1) so this
# barely overlaps the shared array's ascending order -> minimal double-compute
# (deterministic output makes any overlap harmless anyway). Content-validated resume
# shares progress with the shared array. Same output dir/format -> combine-compatible.
#
# 2026-08-06: the resume guard was a bare size test that continued, the BEN-023
# size-as-completion-proof defect -- and it was worse here than in the array variant,
# because this script SHARES boot_nd_5d/ with a concurrent array job, so it could see a
# peer's half-written npz and skip it permanently. Converted to the content-validated
# guard in lib/resume_guard.sh: complete npz adopted without recompute, truncated redone.
# 2026-08-20: `set -u` must NOT be in force while sourcing the environment. setup_salloc_env.sh
# activates a conda env whose activate-binutils_linux-64.sh reads an unset ADDR2LINE; under
# nounset bash 4.4 exits the SHELL, so the job dies before its first line of work. Measured:
# job 57290646 died in 16s, rc=1, with zero-byte logs. The sibling
# sbatch_evloop_array_5d_active_laterals.sh:30 already documents this hazard for setup_MAT.sh.
# pipefail is safe to set early; -u goes on AFTER both sources so the script's own logic is
# still protected (the sourced FUNCTIONS execute below, hence under -u exactly as before).
set -o pipefail
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold; source "$REPO/setup_salloc_env.sh"
source "$REPO/lib/resume_guard.sh"
set -u
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
       NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
cd "$REPO/nd-unfolding"; mkdir -p boot_nd_5d
CONC=16
echo "[boot5dI] start $(date -u +%T) on $(hostname)"
for s in $(seq 100 -1 1); do
  out=boot_nd_5d/res_boot_${s}.npz
  rg_skip_if_complete "$out" rg_valid_npz && continue
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 10; done
  rg_run "$out" python3 bootstrap_nd.py --npz of_inputs_5d.npz --seed ${s} --iters 5 \
    --out "$out" > boot_nd_5d/iboot_${s}.log 2>&1 &
done
wait
echo "[boot5dI] done $(date -u +%T); banked=$(ls boot_nd_5d/res_boot_*.npz 2>/dev/null|wc -l)/100"
