#!/bin/bash
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook 2>/dev/null)"; set +u; conda activate $HOME/.conda/envs/root_6_28
cd /pscratch/sd/j/josephrb/oflow-split-20261123
srun -A m3246 -C cpu -q interactive -N 1 -n 1 -c 32 -t 00:30:00 -J wstest-ibu /usr/bin/time -v python3 wbuild.py > wbuild.out 2> wbuild.err < /dev/null
echo "srun rc=$?"; cat wbuild.out; grep -E 'Elapsed|Maximum resident' wbuild.err; grep -E 'Error|Traceback' -A3 wbuild.err | head; sha256sum wsplit.npz
