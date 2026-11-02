# 1B staged, stage 0: read-only collection of the receipts (our own products, logs and tables) on login37.
W=/pscratch/sd/j/josephrb/fd-1b-staged-20261102
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "== readout.log (warnings dropped)"; grep -v "UserWarning\|warnings.warn" $W/logs/readout.log
echo "== walls-d0.json"; cat $W/stage0/walls-d0.json
echo "== tables"; ls -l $W/tables; (cd $W/tables && sha256sum *)
echo "== SHA256SUMS"; (cd $W/stage0/unf && sha256sum fd1b_d_*.npz) > $W/stage0/SHA256SUMS; wc -l < $W/stage0/SHA256SUMS
(cd $W/stage0 && sha256sum readout.json walls-d0.json) >> $W/stage0/SHA256SUMS
(cd $W && sha256sum stage0-d0.tar stage0.tar) >> $W/stage0/SHA256SUMS
sha256sum $W/stage0/SHA256SUMS
echo "== SHA256SUMS content"; cat $W/stage0/SHA256SUMS
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
