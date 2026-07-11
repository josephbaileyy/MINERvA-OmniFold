#!/bin/bash
# Corrected root_6_28 activation for sbatch. setup_salloc_env.sh's `conda activate
# root_6_28` broke when the system's default `python` module moved to a conda base
# that doesn't register the env (root_6_28 was created under conda 24.10.0). We activate
# by FULL PREFIX via that base's shell hook (HOME must point at the real home so the
# env is discoverable). Provides ROOT 6.28 + lightgbm 4.6 + numpy for the python nd path.
export HOME=/global/homes/j/josephrb
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook 2>/dev/null)"
conda activate /global/homes/j/josephrb/.conda/envs/root_6_28
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build/setup.sh 2>/dev/null || true
export CODEX_HOME=$SCRATCH/codex-home
export TMPDIR=$SCRATCH/tmp
