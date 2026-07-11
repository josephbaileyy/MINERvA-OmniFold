#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# --- root_6_28 activation (robust against default-module changes) ---
# root_6_28 was built under conda 24.10.0. A 2026-07-02 change to the default `python`
# module moved conda to a newer base (26.1.0) that no longer registers the env by NAME,
# so the old `module load python; conda activate root_6_28` fails with
# `EnvironmentNameNotFound`. We activate by FULL PREFIX via the creating base's hook, which
# survives future default-module changes. Override the env path with ROOT628_PREFIX if it
# ever moves. (sbatch/salloc set HOME to the real home, so $HOME resolves correctly here.)
ROOT628_PREFIX="${ROOT628_PREFIX:-$HOME/.conda/envs/root_6_28}"
ROOT628_CONDA="${ROOT628_CONDA:-/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda}"
if [ -x "$ROOT628_CONDA" ] && [ -d "$ROOT628_PREFIX" ]; then
    eval "$("$ROOT628_CONDA" shell.bash hook 2>/dev/null)"
    conda activate "$ROOT628_PREFIX"
else
    module load python && conda activate root_6_28   # legacy fallback (pre-2026-07-02 base)
fi
source "${SCRIPT_DIR}/unbinned_unfolding/build/setup.sh"
# Pin MINERvA101 sub-setups to the migrated opt tree (default would be old HOME path)
export MINERVA_PREFIX="${SCRIPT_DIR}/MINERvA101/opt"
source "${SCRIPT_DIR}/MINERvA101/opt/bin/setup.sh"

export CODEX_HOME=$SCRATCH/codex-home
export TMPDIR=$SCRATCH/tmp
