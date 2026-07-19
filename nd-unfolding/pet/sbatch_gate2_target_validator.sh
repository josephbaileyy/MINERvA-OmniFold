#!/usr/bin/env bash
#SBATCH --job-name=g2gate2
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=192G
#SBATCH --time=24:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=nd-unfolding/g2_fullevent/gate2/logs/g2gate2_%j.out
#SBATCH --error=nd-unfolding/g2_fullevent/gate2/logs/g2gate2_%j.err
set -eo pipefail

REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
RUNNER=${REPO}/nd-unfolding/pet/run_gate2_target_validator.sh
EXPECTED_RUNNER_SHA=3e43962602a630f49eea590e031cc0c5538d6442cee3d5c209903a821032a159

[[ -x "$RUNNER" ]] || { echo "[g2gate2][FAIL] runner missing/not executable" >&2; exit 1; }
[[ "$(sha256sum "$RUNNER" | awk '{print $1}')" == "$EXPECTED_RUNNER_SHA" ]] || {
  echo "[g2gate2][FAIL] runner changed after submission" >&2; exit 1;
}
exec env GATE2_EXECUTION_ROUTE=batch GATE2_RUN_ID="slurm-${SLURM_JOB_ID}" "$RUNNER"
