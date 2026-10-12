#!/bin/bash
# Stage C input copy to CFS (grant AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md, "data copy").
# Runs on a NERSC data-transfer node (dtn01). Source is read-only; sha256 measured at the source before the
# copy and re-measured at the destination after it. Refuses if the destination exists or if CFS free space
# after the copy would be below 3 TB.
#   nohup bash copy_stageC_inputs.sh > copy.log 2>&1 &
set -eo pipefail
SRC_A=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/active_universe_5d/standard/merged
SRC_N=/pscratch/sd/j/josephrb/2d-closeout-stageAB-20261012/b-genie-truth
DST=/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012
LOG=/pscratch/sd/j/josephrb/2d-closeout-stageB-diag-20261012/copy
mkdir -p "$LOG"
echo "start $(date -u +%FT%TZ) host $(hostname)"
[ -e "$DST" ] && { echo "REFUSE: $DST exists"; exit 2; }

quota() { /global/common/software/nersc/bin/cfsquota m3246 2>&1 | awk '$1=="m3246"{print $2, $3}'; }
read used q < <(quota)
need=$(( ( $(stat -c %s "$SRC_A"/runEventLoopOmniFold_5D_MEFHC_active_*.root "$SRC_N"/{sweeps,adopted_cov}.npz | paste -sd+ | bc) + 999999999 ) / 1000000000 ))
free_after=$(( q - used - need ))
echo "cfsquota m3246 before: used ${used} GB quota ${q} GB; copy ${need} GB; free after ${free_after} GB"
[ "$free_after" -ge 3000 ] || { echo "STOP: free after copy ${free_after} GB < 3000 GB"; exit 3; }

cd "$SRC_A"
ls runEventLoopOmniFold_5D_MEFHC_active_*.root > "$LOG/files_active.txt"
[ "$(wc -l < "$LOG/files_active.txt")" -eq 10 ] || { echo "REFUSE: expected 10 active files"; exit 2; }
echo "source sha256 (active) $(date -u +%FT%TZ)"
xargs -P 5 -n 1 sha256sum < "$LOG/files_active.txt" | sort -k2 > "$LOG/SHA256SUMS.active.src"
(cd "$SRC_N" && sha256sum sweeps.npz adopted_cov.npz) > "$LOG/SHA256SUMS.npz.src"

mkdir -p "$DST/active_universe_5d_standard_merged" "$DST/stageB_npz"
echo "copy $(date -u +%FT%TZ)"
xargs -P 5 -I{} cp --preserve=timestamps,mode "$SRC_A/{}" "$DST/active_universe_5d_standard_merged/" < "$LOG/files_active.txt"
cp --preserve=timestamps,mode "$SRC_A"/merge_*.log "$DST/active_universe_5d_standard_merged/"
cp --preserve=timestamps,mode "$SRC_N/sweeps.npz" "$SRC_N/adopted_cov.npz" "$DST/stageB_npz/"
cp "$LOG/SHA256SUMS.active.src" "$DST/active_universe_5d_standard_merged/SHA256SUMS"
cp "$LOG/SHA256SUMS.npz.src" "$DST/stageB_npz/SHA256SUMS"

echo "destination sha256 $(date -u +%FT%TZ)"
(cd "$DST/active_universe_5d_standard_merged" && xargs -P 5 -n 1 sha256sum < "$LOG/files_active.txt" | sort -k2) > "$LOG/SHA256SUMS.active.dst"
(cd "$DST/stageB_npz" && sha256sum sweeps.npz adopted_cov.npz) > "$LOG/SHA256SUMS.npz.dst"
if cmp -s "$LOG/SHA256SUMS.active.src" "$LOG/SHA256SUMS.active.dst" && cmp -s "$LOG/SHA256SUMS.npz.src" "$LOG/SHA256SUMS.npz.dst"; then
  echo "SHA256 MATCH: 10 active + 2 npz"
else
  echo "SHA256 MISMATCH"; diff "$LOG/SHA256SUMS.active.src" "$LOG/SHA256SUMS.active.dst" || true; exit 4
fi
read used2 q2 < <(quota)
echo "cfsquota m3246 after: used ${used2} GB quota ${q2} GB; free $(( q2 - used2 )) GB"
chmod -R a-w "$DST"
echo "done $(date -u +%FT%TZ)"
