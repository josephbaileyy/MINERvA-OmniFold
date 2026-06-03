#!/bin/bash
# Roll up the data-only and mc-only split-bootstrap campaigns into covariances,
# then run the closure + paper-StatOnly comparison (compare_split_bootstrap.py).
#
# Safe to run repeatedly: it rolls up whatever replicas are on disk. Pass a
# minimum count to gate the "final" run, e.g.:
#   bash run_split_analysis.sh           # run on whatever is present (warns if low)
#   bash run_split_analysis.sh 200       # only proceed if both streams have >=200
#
# Arrays: 53678615 (data -> boot_data/), 53678616 (mc -> boot_mc/), 200 each.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
UQ="${REPO}/2d-unfolding/uq"
cd "${UQ}"
source "${REPO}/setup_salloc_env.sh" >/dev/null 2>&1
MIN="${1:-0}"

nd=$(ls boot_data/2d_xsec_*_boot*.root 2>/dev/null | wc -l)
nm=$(ls boot_mc/2d_xsec_*_boot*.root   2>/dev/null | wc -l)
echo "[split] replicas on disk: data=${nd}  mc=${nm}  (gate MIN=${MIN})"
if [[ "${nd}" -lt "${MIN}" || "${nm}" -lt "${MIN}" ]]; then
  echo "[split] below gate (${MIN}); not running yet. Re-run when arrays drain."
  exit 0
fi
if [[ "${nd}" -lt 2 || "${nm}" -lt 2 ]]; then
  echo "[split] need >=2 replicas per stream to form a covariance; aborting."
  exit 1
fi

echo "[split] rolling up C_data (${nd} replicas) ..."
python analyze_uq.py --glob 'boot_data/2d_xsec_*_boot*.root' \
  --outdir boot_data --out-root uq_covariance_bootdata.root \
  2>&1 | grep -vE "ReadRootmapFile|already in libRooUnfold" | sed 's/^/   /'

echo "[split] rolling up C_mc (${nm} replicas) ..."
python analyze_uq.py --glob 'boot_mc/2d_xsec_*_boot*.root' \
  --outdir boot_mc --out-root uq_covariance_bootmc.root \
  2>&1 | grep -vE "ReadRootmapFile|already in libRooUnfold" | sed 's/^/   /'

echo "[split] comparison (closure + paper StatOnly) ..."
python compare_split_bootstrap.py \
  --data boot_data/uq_covariance_bootdata.root:hCov2D_reported \
  --mc   boot_mc/uq_covariance_bootmc.root:hCov2D_reported \
  --both bootstrap_MEFHC_300/uq_covariance_boot300.root:hCov2D_reported \
  2>&1 | grep -vE "ReadRootmapFile|already in libRooUnfold"
