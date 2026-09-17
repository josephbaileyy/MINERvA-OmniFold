#!/bin/bash
# A1: bounded counts-and-energy characterization of the two pinned sources,
# authorized by Joseph on 2026-09-18. CPU only, no GPU, no retry, no resubmission.
# It reads counts plus cluster energy and writes one receipt; it trains nothing and
# decides nothing. The ceiling is 8 CPU core-hours; 2 cpus x 2 h caps this at 4.
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --job-name=pet-source-characterization
set -euo pipefail

checkout=$1
output=$2
expected_commit=$3
entries=${4:-200000}

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
[[ ! -e "$output" ]]
mkdir -p "$output"
trap 'status=$?; if (( status != 0 )); then echo FAILED > "$output/terminal.txt"; printf "%s\n" "$status" > "$output/exit-code.txt"; fi' EXIT
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"

# ROOT and TensorFlow do not coexist in one interpreter on this machine; this read
# needs ROOT only, so it runs in the root_6_28 environment rather than the campaign
# runtime. Activation is by PREFIX because a 2026-07-02 default-module change stopped
# the env resolving by name.
ROOT628_PREFIX="${ROOT628_PREFIX:-$HOME/.conda/envs/root_6_28}"
ROOT628_CONDA="${ROOT628_CONDA:-/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda}"
# `set -u` and conda activation do not mix: root_6_28 ships
# activate.d/activate-binutils_linux-64.sh, which reads $ADDR2LINE unbound and kills
# the job in four seconds. Unset -u across activation only, then restore it.
set +u
eval "$("$ROOT628_CONDA" shell.bash hook)"
conda activate "$ROOT628_PREFIX"
set -u
python -c "import ROOT, numpy; print('ROOT', ROOT.gROOT.GetVersion(), 'numpy', numpy.__version__)" \
  > "$output/environment.txt"

export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
python nd-unfolding/pet/direct_token_comparison/characterize_source_multiplicity.py \
  --checkout "$checkout" --entries "$entries" --crosscheck-every 2000 \
  --output "$output/source-multiplicity.json" > "$output/characterize.log" 2>&1

[[ -z "$(git status --porcelain)" ]]
python -c "
import json, pathlib, sys
receipt = json.loads(pathlib.Path('$output/source-multiplicity.json').read_text())
assert len(receipt['sources']) == 2, 'both pinned sources must be characterized'
for source in receipt['sources']:
    assert source['entries_read'] > 0, source['role']
    assert source['production_crosschecks_passed'] > 0, (
        f\"{source['role']}: no entry was checked against the production builder\"
    )
print('receipt verified:', [s['entries_read'] for s in receipt['sources']])
"
echo 0 > "$output/exit-code.txt"
echo COMPLETE > "$output/terminal.txt"
