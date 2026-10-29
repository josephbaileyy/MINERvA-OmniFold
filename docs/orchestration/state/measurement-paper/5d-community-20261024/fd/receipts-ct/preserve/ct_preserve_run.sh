#!/bin/bash
# Cheap tier, 3b's npz inputs to HPSS (director ruling (2), 2026-10-28, after PR #460). Login node, no Slurm, no node-h.
# Inventories the MP-1 S1 lateral+unf and W2b lateral+unf npz, cross-checks W2b against the CFS W2-SHA256SUMS,
# then runs the committed stage0_preserve.sh verbatim. Never modifies or deletes a source file.
set -o pipefail   # NOT set -u
P=/pscratch/sd/j/josephrb
W=$P/fd-ct-preserve-20261028
H=/home/j/josephrb/mnv-5d-ct-3b-inputs-20261028
CFSW2=/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/W2-SHA256SUMS
stamp() { date -u +%FT%TZ; }
mkdir -p $W
[ -e $W/INVENTORY.sha256 ] && { echo "REFUSE: $W/INVENTORY.sha256 exists"; exit 3; }
{
echo "[R] $(stamp) start host=$(hostname)"
echo "[R] hpssquota before:"; hpssquota 2>&1 | grep -E 'HPSS|pscratch'
ls $P/measurement-paper/phase1/mp1/s1/lateral/*.npz $P/measurement-paper/phase1/mp1/s1/unf/*.npz \
   $P/w2-recoil-20261006/w2b/lateral/*.npz $P/w2-recoil-20261006/w2b/unf/*.npz | sort > $W/sources.list
n=$(wc -l < $W/sources.list); echo "[R] sources: $n files, $(cat $W/sources.list | xargs stat -c %s | awk '{s+=$1} END{print s}') B"
[ "$n" -eq 42 ] || { echo "[R] STOP: expected 42 sources, found $n"; exit 3; }
xargs -a $W/sources.list sha256sum > $W/INVENTORY.sha256 || { echo "[R] STOP: sha256sum failed"; exit 3; }
echo "[R] $(stamp) inventory written: $(wc -l < $W/INVENTORY.sha256) lines, sha256 $(sha256sum $W/INVENTORY.sha256 | cut -c1-64)"
echo "[R] W2b cross-check against $CFSW2 (match = same digest recorded for the same pscratch-relative name):"
grep w2-recoil $W/INVENTORY.sha256 | while read d f; do
  rel=${f#/}; hit=$(grep -F "$d" $CFSW2 | grep -c -F "${f##*/}"); echo "  $hit  ${f##*/}"; done
echo "[R] $(stamp) calling stage0_preserve.sh"
} 2>&1 | tee -a $W/run.log
[ "${PIPESTATUS[0]}" -eq 0 ] || exit 3
bash $W/stage0_preserve.sh $W/INVENTORY.sha256 $W $H; rc=$?
{ echo "[R] $(stamp) stage0_preserve rc=$rc"; echo "[R] hpssquota after:"; hpssquota 2>&1 | grep -E 'HPSS|pscratch'; hsi -q "ls -l $H" 2>&1; echo "[R] $(stamp) end rc=$rc"; } 2>&1 | tee -a $W/run.log
exit $rc
