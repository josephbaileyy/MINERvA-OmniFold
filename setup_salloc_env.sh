#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
module load python
conda activate root_6_28
source "${SCRIPT_DIR}/unbinned_unfolding/build/setup.sh"
# Pin MINERvA101 sub-setups to the migrated opt tree (default would be old HOME path)
export MINERVA_PREFIX="${SCRIPT_DIR}/MINERvA101/opt"
source "${SCRIPT_DIR}/MINERvA101/opt/bin/setup.sh"
