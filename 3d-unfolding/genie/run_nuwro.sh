#!/bin/bash
# run_nuwro.sh N SEED TAG -- generate NuWro numu-on-C12 truth events with the
# MINERvA ME FHC flux, then convert to a flat observable tree.
# Produces work_nuwro_<TAG>/nuwro_flat.root (consumed by nuwro_to_xsec3d.py).
#
# Target: C12 (target_type=0). NuWro's composite target_content crashed; C12 is
# ~92% of CH by nucleons, an acceptable approximation for an independent-model
# comparison (documented). NuWro weight = flux-averaged total CC xsec/nucleon.
set -eo pipefail
N=${1:-250000}
SEED=${2:-1}
TAG=${3:-cv}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "[run_nuwro] starting N=$N seed=$SEED tag=$TAG"

set +e
source "$HERE/setup_nuwro.sh"
SETUP_RC=$?
set -e
[ $SETUP_RC -eq 0 ] || { echo "[run_nuwro] setup failed" >&2; exit 1; }

WORK="$HERE/work_nuwro_${TAG}"
mkdir -p "$WORK"; cd "$WORK"
cat > params.txt <<EOF
random_seed = $SEED
number_of_events = $N
number_of_test_events = 50000
beam_particle = 14
beam_type = 5
beam_inputroot = $NUWRO_FLUX
beam_inputroot_flux = $NUWRO_FLUX_HIST
target_type = 0
nucleus_p = 6
nucleus_n = 6
dyn_qel_cc = 1
dyn_res_cc = 1
dyn_dis_cc = 1
dyn_coh_cc = 1
dyn_mec_cc = 1
EOF

echo "[run_nuwro] generating ($(date -u '+%F %T UTC')) ..."
"$NUWRO_HOME/bin/nuwro" -i params.txt -o "nuwro_${TAG}.root" > "nuwro_${TAG}.log" 2>&1
echo "[run_nuwro] nuwro rc=$? ; converting to flat tree"
root -l -b -q "${NUWRO_FLAT_MACRO}(\"nuwro_${TAG}.root\",\"nuwro_flat.root\")" \
  > "flat_${TAG}.log" 2>&1
echo "[run_nuwro] done $(date -u '+%F %T UTC'); $(ls -la nuwro_flat.root | awk '{print $5}') bytes"
