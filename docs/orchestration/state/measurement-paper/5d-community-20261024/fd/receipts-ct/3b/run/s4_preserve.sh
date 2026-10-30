#!/bin/bash
# FD-CT-3B-DECLARATION.md section 2.4: the 13 closures to HPSS by the committed stage0_preserve.sh (the deploy's copy).
P=/pscratch/sd/j/josephrb
B=$P/fd-ct-3b-20261029
D=$B/deploy/e904d635
W=$B/preserve
H=/home/j/josephrb/mnv-5d-ct-3b-closures-20261029
[ -e "$W" ] && { echo "STOP: $W exists"; exit 9; }
mkdir -p $W
{ echo "[R] $(date -u +%FT%TZ) host $(hostname)"; echo "[R] hpssquota before:"; hpssquota 2>&1 | grep -E 'HPSS'
  ls $B/closures/closure_*.npz | sort > $W/sources.list; echo "[R] sources $(wc -l < $W/sources.list)"
  [ "$(wc -l < $W/sources.list)" -eq 13 ] || { echo "[R] STOP: not 13 closures"; exit 3; }
  xargs -a $W/sources.list sha256sum > $W/INVENTORY.sha256; echo "[R] inventory sha256 $(sha256sum $W/INVENTORY.sha256 | cut -c1-64)"; } > $W/run.log 2>&1
bash $D/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/stage0_preserve.sh $W/INVENTORY.sha256 $W $H; rc=$?
{ echo "[R] stage0_preserve rc=$rc $(date -u +%FT%TZ)"; echo "[R] hpssquota after:"; hpssquota 2>&1 | grep -E 'HPSS'; hsi -q "ls -l $H" 2>&1; } >> $W/run.log 2>&1
exit $rc
