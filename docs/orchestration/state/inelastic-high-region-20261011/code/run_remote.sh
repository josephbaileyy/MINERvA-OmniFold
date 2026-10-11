#!/bin/bash
# run_remote.sh SCRIPT CAP_S ARGS... -- run one study script on a Perlmutter login node in root_6_28,
# under ulimit -t, from the study's own scratch directory. No set -u (it aborts the activation).
D=/pscratch/sd/j/josephrb/inelastic-high-region-20261011
SCRIPT=$1; CAP=$2; shift 2
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate $HOME/.conda/envs/root_6_28
cd "$D" || exit 2
ulimit -t "$CAP"
exec python3 "$D/code/$SCRIPT" "$@"
