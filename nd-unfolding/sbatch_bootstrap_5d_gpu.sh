#!/bin/bash
#SBATCH --job-name=boot5dG
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=03:00:00
#SBATCH --array=1-100%32
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=boot5dG_%a_%A.out --error=boot5dG_%a_%A.err
# GPU-allocation variant of sbatch_bootstrap_5d.sh (2026-07-13): CPU top-up not
# coming, but GPU-hours are available -> run the UNCHANGED bootstrap_nd.py on GPU
# NODE HOST CORES (32 cpus/task), charged to m3246_g. The reserved GPU is idle
# (bootstrap is LightGBM CPU code); we are buying host cores with GPU-hours.
# Content-validated resume + same output dir (boot_nd_5d/) as the CPU script, so it
# is combine-compatible and resumable. --export HOME fixes the school-acct conda trap.
#
# 2026-08-06: the resume guard was a bare size test that exited 0, the BEN-023
# size-as-completion-proof defect -- a truncated npz opens fine and only fails when a
# member is actually read, so a partial file permanently blocked its own repair.
# Converted to the content-validated guard in lib/resume_guard.sh: a complete npz is
# validated and adopted (no recompute), a truncated one is detected and redone. See
# FINDINGS.md BEN-023.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
source "${REPO}/lib/resume_guard.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p boot_nd_5d
OUT="boot_nd_5d/res_boot_${SLURM_ARRAY_TASK_ID}.npz"
rg_skip_if_complete "$OUT" rg_valid_npz && exit 0
rg_run "$OUT" python3 bootstrap_nd.py --npz of_inputs_5d.npz \
  --seed ${SLURM_ARRAY_TASK_ID} --iters 5 --out "$OUT"
