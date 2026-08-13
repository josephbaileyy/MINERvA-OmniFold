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
# ADVANCED 2026-08-13 for the Gate-2 bit-identity re-run. Prior value
# d5b86c3639917ff82101f112df25d1ff51830223f834e1a689c8088a1156d062.
#
# THE PIN CHAIN IS THREE DEEP AND THE DECISION NAMED ONLY ITS MIDDLE. Advancing the loader forces
# advancing EXPECTED_LOADER_SHA in run_gate2_target_validator.sh, which changes THAT file's sha,
# which this launcher and docs/orchestration/run_gate2_r4_detached.sh both pin as
# EXPECTED_RUNNER_SHA. So: loader <- validator <- {this launcher, the detached runner}. The chain
# terminates here -- nothing pins this file, verified by grep.
EXPECTED_RUNNER_SHA=42386ab5e3b81d9a5e656dffce73910820d137489ba7ca78bfe89cf14ce627b4

[[ -x "$RUNNER" ]] || { echo "[g2gate2][FAIL] runner missing/not executable" >&2; exit 1; }
[[ "$(sha256sum "$RUNNER" | awk '{print $1}')" == "$EXPECTED_RUNNER_SHA" ]] || {
  echo "[g2gate2][FAIL] runner changed after submission" >&2; exit 1;
}
exec env GATE2_EXECUTION_ROUTE=batch GATE2_RUN_ID="slurm-${SLURM_JOB_ID}" "$RUNNER"
